"""
X API Integration Client
Comprehensive integration with X API v2 for social media intelligence gathering
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import urllib.parse
from enum import Enum

from ..utils.rate_limiter import RateLimiter
from ..utils.retry_handler import RetryHandler
from ...config.credentials.api_credentials import get_x_credentials
from ...config.settings.config import get_config


class EndpointType(Enum):
    """X API endpoint types for rate limiting"""
    SEARCH = "search"
    USERS = "users"
    TWEETS = "tweets"
    STREAMING = "streaming"


@dataclass
class Tweet:
    """Tweet data structure"""
    id: str
    text: str
    author_id: str
    created_at: str
    public_metrics: Dict[str, int]
    context_annotations: Optional[List[Dict]] = None
    entities: Optional[Dict] = None
    geo: Optional[Dict] = None
    lang: Optional[str] = None
    reply_settings: Optional[str] = None
    referenced_tweets: Optional[List[Dict]] = None
    
    @property
    def engagement_score(self) -> int:
        """Calculate engagement score based on metrics"""
        metrics = self.public_metrics
        return (
            metrics.get('like_count', 0) * 1 +
            metrics.get('retweet_count', 0) * 2 +
            metrics.get('reply_count', 0) * 3 +
            metrics.get('quote_count', 0) * 2
        )
    
    @property
    def created_datetime(self) -> datetime:
        """Convert created_at string to datetime object"""
        return datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))


@dataclass
class User:
    """User data structure"""
    id: str
    name: str
    username: str
    verified: bool
    public_metrics: Dict[str, int]
    description: Optional[str] = None
    created_at: Optional[str] = None
    location: Optional[str] = None
    
    @property
    def follower_count(self) -> int:
        """Get follower count"""
        return self.public_metrics.get('followers_count', 0)
    
    @property
    def credibility_score(self) -> float:
        """Calculate user credibility score"""
        base_score = 0.5
        
        # Verification bonus
        if self.verified:
            base_score += 0.3
        
        # Follower count influence (logarithmic scale)
        follower_count = self.follower_count
        if follower_count > 0:
            import math
            follower_score = min(0.2, math.log10(follower_count) / 10)
            base_score += follower_score
        
        # Account age influence
        if self.created_at:
            try:
                created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
                account_age_days = (datetime.now().replace(tzinfo=created.tzinfo) - created).days
                age_score = min(0.1, account_age_days / 3650)  # Max 0.1 for 10+ year old accounts
                base_score += age_score
            except:
                pass
        
        return min(1.0, base_score)


@dataclass
class SearchResult:
    """Search result container"""
    tweets: List[Tweet]
    users: Dict[str, User]
    meta: Dict[str, Any]
    includes: Optional[Dict] = None


class XAPIClient:
    """Comprehensive X API v2 client"""
    
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self):
        """Initialize X API client"""
        self.credentials = get_x_credentials()
        self.config = get_config().x_api
        self.logger = logging.getLogger(__name__)
        
        # Rate limiters for different endpoints
        self.rate_limiters = {
            EndpointType.SEARCH: RateLimiter(
                requests_per_minute=self.config.requests_per_minute,
                requests_per_hour=self.config.requests_per_hour
            ),
            EndpointType.USERS: RateLimiter(
                requests_per_minute=300,
                requests_per_hour=1500
            ),
            EndpointType.TWEETS: RateLimiter(
                requests_per_minute=300,
                requests_per_hour=1500
            )
        }
        
        self.retry_handler = RetryHandler(max_retries=3, base_delay=1.0)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def initialize_session(self):
        """Initialize HTTP session"""
        headers = {
            "Authorization": f"Bearer {self.credentials.bearer_token}",
            "Content-Type": "application/json",
            "User-Agent": "GrokXModule/1.0"
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=100)
        )
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    def _build_query_params(self, **kwargs) -> str:
        """Build query parameters for API requests"""
        params = {}
        
        # Tweet fields
        if 'tweet_fields' not in kwargs:
            params['tweet.fields'] = ','.join(self.config.tweet_fields)
        
        # User fields
        if 'user_fields' not in kwargs:
            params['user.fields'] = ','.join(self.config.user_fields)
        
        # Expansions
        if 'expansions' not in kwargs:
            params['expansions'] = ','.join(self.config.expansions)
        
        # Add custom parameters
        params.update(kwargs)
        
        return urllib.parse.urlencode(params)
    
    async def _make_request(
        self,
        endpoint: str,
        endpoint_type: EndpointType,
        params: Optional[Dict] = None,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting and retry logic"""
        
        # Apply rate limiting
        await self.rate_limiters[endpoint_type].acquire()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        async def _request():
            if method == "GET":
                async with self.session.get(url, params=params) as response:
                    return await self._handle_response(response)
            elif method == "POST":
                async with self.session.post(url, params=params, json=data) as response:
                    return await self._handle_response(response)
        
        return await self.retry_handler.execute(_request)
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response and errors"""
        if response.status == 200:
            return await response.json()
        elif response.status == 429:
            # Rate limit exceeded
            reset_time = response.headers.get('x-rate-limit-reset')
            if reset_time:
                wait_time = int(reset_time) - int(time.time())
                self.logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds.")
                await asyncio.sleep(max(wait_time, 60))
            raise Exception(f"Rate limit exceeded: {response.status}")
        else:
            error_text = await response.text()
            self.logger.error(f"API request failed: {response.status} - {error_text}")
            raise Exception(f"API request failed: {response.status} - {error_text}")
    
    def _parse_tweets(self, data: Dict[str, Any]) -> SearchResult:
        """Parse API response into structured data"""
        tweets = []
        users = {}
        
        # Parse tweets
        if 'data' in data:
            for tweet_data in data['data']:
                tweet = Tweet(**tweet_data)
                tweets.append(tweet)
        
        # Parse included users
        if 'includes' in data and 'users' in data['includes']:
            for user_data in data['includes']['users']:
                user = User(**user_data)
                users[user.id] = user
        
        return SearchResult(
            tweets=tweets,
            users=users,
            meta=data.get('meta', {}),
            includes=data.get('includes')
        )
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sort_order: str = "recency"
    ) -> SearchResult:
        """Search for tweets using X API v2 search endpoint"""
        
        params = {
            'query': query,
            'max_results': min(max_results, self.config.max_results_per_request),
            'sort_order': sort_order
        }
        
        if start_time:
            params['start_time'] = start_time.isoformat()
        if end_time:
            params['end_time'] = end_time.isoformat()
        
        # Add default fields
        query_string = self._build_query_params(**params)
        
        self.logger.info(f"Searching tweets with query: {query}")
        
        response = await self._make_request(
            f"tweets/search/recent?{query_string}",
            EndpointType.SEARCH
        )
        
        return self._parse_tweets(response)
    
    async def search_crypto_tweets(
        self,
        symbols: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        max_results: int = 100,
        time_window_hours: int = 24
    ) -> SearchResult:
        """Search for cryptocurrency-related tweets"""
        
        # Build search query
        query_parts = []
        
        # Add symbols
        if symbols:
            symbol_queries = [f"${symbol} OR {symbol}" for symbol in symbols]
            query_parts.append(f"({' OR '.join(symbol_queries)})")
        
        # Add keywords
        search_keywords = keywords or self.config.crypto_keywords
        if search_keywords:
            keyword_queries = [f'"{keyword}"' for keyword in search_keywords[:10]]  # Limit to avoid query length issues
            query_parts.append(f"({' OR '.join(keyword_queries)})")
        
        # Combine query parts
        if not query_parts:
            query_parts.append("(crypto OR bitcoin OR ethereum)")
        
        query = ' AND '.join(query_parts)
        
        # Add filters
        query += " -is:retweet lang:en"
        
        # Set time window
        start_time = datetime.now() - timedelta(hours=time_window_hours)
        
        return await self.search_tweets(
            query=query,
            max_results=max_results,
            start_time=start_time,
            sort_order="recency"
        )
    
    async def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 100,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> SearchResult:
        """Get tweets from a specific user"""
        
        params = {
            'max_results': min(max_results, 100),
            'exclude': []
        }
        
        if exclude_replies:
            params['exclude'].append('replies')
        if exclude_retweets:
            params['exclude'].append('retweets')
        
        if params['exclude']:
            params['exclude'] = ','.join(params['exclude'])
        else:
            del params['exclude']
        
        query_string = self._build_query_params(**params)
        
        response = await self._make_request(
            f"users/{user_id}/tweets?{query_string}",
            EndpointType.TWEETS
        )
        
        return self._parse_tweets(response)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user information by username"""
        
        query_string = self._build_query_params()
        
        try:
            response = await self._make_request(
                f"users/by/username/{username}?{query_string}",
                EndpointType.USERS
            )
            
            if 'data' in response:
                return User(**response['data'])
        except Exception as e:
            self.logger.error(f"Failed to get user {username}: {e}")
        
        return None
    
    async def get_users_by_usernames(self, usernames: List[str]) -> List[User]:
        """Get multiple users by usernames"""
        
        params = {'usernames': ','.join(usernames)}
        query_string = self._build_query_params(**params)
        
        try:
            response = await self._make_request(
                f"users/by?{query_string}",
                EndpointType.USERS
            )
            
            users = []
            if 'data' in response:
                for user_data in response['data']:
                    users.append(User(**user_data))
            
            return users
        except Exception as e:
            self.logger.error(f"Failed to get users {usernames}: {e}")
            return []
    
    async def monitor_influencers(
        self,
        usernames: Optional[List[str]] = None,
        max_tweets_per_user: int = 10
    ) -> Dict[str, SearchResult]:
        """Monitor tweets from crypto influencers"""
        
        influencers = usernames or self.config.track_influencers
        results = {}
        
        # Get user IDs first
        users = await self.get_users_by_usernames(influencers)
        user_map = {user.username: user for user in users}
        
        # Get tweets for each influencer
        for username in influencers:
            if username in user_map:
                user = user_map[username]
                try:
                    tweets = await self.get_user_tweets(
                        user.id,
                        max_results=max_tweets_per_user,
                        exclude_replies=True,
                        exclude_retweets=True
                    )
                    results[username] = tweets
                    self.logger.info(f"Retrieved {len(tweets.tweets)} tweets from @{username}")
                except Exception as e:
                    self.logger.error(f"Failed to get tweets for @{username}: {e}")
                    results[username] = SearchResult(tweets=[], users={}, meta={})
        
        return results
    
    async def get_trending_crypto_content(
        self,
        time_window_hours: int = 6,
        min_engagement: int = 100
    ) -> SearchResult:
        """Get trending cryptocurrency content based on engagement"""
        
        # Search for crypto content in recent time window
        result = await self.search_crypto_tweets(
            max_results=100,
            time_window_hours=time_window_hours
        )
        
        # Filter by engagement threshold
        high_engagement_tweets = [
            tweet for tweet in result.tweets
            if tweet.engagement_score >= min_engagement
        ]
        
        # Sort by engagement score
        high_engagement_tweets.sort(key=lambda t: t.engagement_score, reverse=True)
        
        return SearchResult(
            tweets=high_engagement_tweets,
            users=result.users,
            meta=result.meta,
            includes=result.includes
        )
    
    async def stream_crypto_tweets(self) -> AsyncGenerator[Tweet, None]:
        """Stream real-time cryptocurrency tweets (placeholder for streaming implementation)"""
        # Note: This would require implementing the streaming API
        # For now, we'll simulate with periodic searches
        
        while True:
            try:
                result = await self.search_crypto_tweets(max_results=10, time_window_hours=1)
                for tweet in result.tweets:
                    yield tweet
                
                # Wait before next batch
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error(f"Error in tweet streaming: {e}")
                await asyncio.sleep(300)  # 5 minute wait on error


# Utility functions for easy access
async def search_crypto_sentiment(
    symbols: List[str],
    time_window_hours: int = 24,
    max_results: int = 100
) -> SearchResult:
    """Convenience function to search for crypto sentiment"""
    async with XAPIClient() as client:
        return await client.search_crypto_tweets(
            symbols=symbols,
            max_results=max_results,
            time_window_hours=time_window_hours
        )


async def monitor_crypto_influencers(
    usernames: Optional[List[str]] = None
) -> Dict[str, SearchResult]:
    """Convenience function to monitor crypto influencers"""
    async with XAPIClient() as client:
        return await client.monitor_influencers(usernames)


async def get_trending_crypto() -> SearchResult:
    """Convenience function to get trending crypto content"""
    async with XAPIClient() as client:
        return await client.get_trending_crypto_content()

