"""
Web Search MCP Adapter for Zmarty Dashboard
Provides web search and content extraction through MCP
"""
import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib
from urllib.parse import urlparse, urljoin
import aiohttp
from bs4 import BeautifulSoup
import feedparser
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result data structure"""
    title: str
    url: str
    snippet: str
    source: str
    timestamp: str
    relevance_score: float = 0.0
    content_type: str = "text"
    metadata: Dict[str, Any] = None


class WebSearchMCPAdapter:
    """
    MCP-compatible web search adapter
    Provides secure web search, content extraction, and news aggregation
    """
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 1000
        
        # Search engines configuration
        self.search_engines = {
            'duckduckgo': 'https://api.duckduckgo.com/',
            'news_api': 'https://newsapi.org/v2/',
            'reddit': 'https://www.reddit.com/search.json',
            'hackernews': 'https://hn.algolia.com/api/v1/search'
        }
        
        # RSS feeds for crypto/trading news
        self.rss_feeds = [
            'https://cointelegraph.com/rss',
            'https://coindesk.com/arc/outboundfeeds/rss/',
            'https://cryptonews.com/news/feed/',
            'https://feeds.feedburner.com/bitcoinist',
            'https://ambcrypto.com/feed/',
            'https://blockworks.co/feed/',
            'https://decrypt.co/feed'
        ]
        
        # User agents for web scraping
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'User-Agent': self.user_agents[0]}
            )
        logger.info("Web Search MCP initialized successfully")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, query: str, search_type: str, **kwargs) -> str:
        """Generate cache key for query"""
        key_data = f"{query}:{search_type}:{json.dumps(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: str) -> bool:
        """Check if cached data is still valid"""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            return datetime.utcnow() - cache_time < timedelta(seconds=self.cache_ttl)
        except:
            return False
    
    def _cache_result(self, key: str, data: Any):
        """Cache search result"""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result if valid"""
        if key in self.cache:
            cached = self.cache[key]
            if self._is_cache_valid(cached['timestamp']):
                return cached['data']
            else:
                del self.cache[key]
        return None
    
    async def search_web(
        self,
        query: str,
        limit: int = 10,
        search_engine: str = 'duckduckgo',
        safe_search: bool = True,
        region: str = 'us-en'
    ) -> List[SearchResult]:
        """Search the web using various engines"""
        try:
            cache_key = self._get_cache_key(query, 'web_search', 
                                          limit=limit, engine=search_engine, region=region)
            
            # Check cache first
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            await self.initialize()
            results = []
            
            if search_engine == 'duckduckgo':
                results = await self._search_duckduckgo(query, limit, safe_search, region)
            elif search_engine == 'hackernews':
                results = await self._search_hackernews(query, limit)
            
            # Cache and return results
            self._cache_result(cache_key, results)
            return results
            
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return []
    
    async def _search_duckduckgo(self, query: str, limit: int, safe_search: bool, region: str) -> List[SearchResult]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1',
                'no_redirect': '1',
                'safe_search': 'strict' if safe_search else 'moderate'
            }
            
            async with self.session.get('https://api.duckduckgo.com/', params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    # Process instant answer
                    if data.get('Abstract'):
                        results.append(SearchResult(
                            title=data.get('Heading', query),
                            url=data.get('AbstractURL', ''),
                            snippet=data.get('Abstract', ''),
                            source='DuckDuckGo',
                            timestamp=datetime.utcnow().isoformat(),
                            relevance_score=1.0,
                            content_type='instant_answer'
                        ))
                    
                    # Process related topics
                    for topic in data.get('RelatedTopics', [])[:limit-len(results)]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append(SearchResult(
                                title=topic.get('Text', '').split(' - ')[0],
                                url=topic.get('FirstURL', ''),
                                snippet=topic.get('Text', ''),
                                source='DuckDuckGo',
                                timestamp=datetime.utcnow().isoformat(),
                                relevance_score=0.8,
                                content_type='related_topic'
                            ))
                    
                    return results[:limit]
                    
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
        
        return []
    
    async def _search_hackernews(self, query: str, limit: int) -> List[SearchResult]:
        """Search Hacker News using Algolia API"""
        try:
            params = {
                'query': query,
                'tags': 'story',
                'hitsPerPage': limit,
                'attributesToRetrieve': 'title,url,author,points,num_comments,created_at'
            }
            
            async with self.session.get('https://hn.algolia.com/api/v1/search', params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for hit in data.get('hits', []):
                        results.append(SearchResult(
                            title=hit.get('title', ''),
                            url=hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                            snippet=f"Points: {hit.get('points', 0)}, Comments: {hit.get('num_comments', 0)}",
                            source='Hacker News',
                            timestamp=hit.get('created_at', datetime.utcnow().isoformat()),
                            relevance_score=min(hit.get('points', 0) / 100.0, 1.0),
                            content_type='news',
                            metadata={
                                'author': hit.get('author'),
                                'points': hit.get('points'),
                                'comments': hit.get('num_comments')
                            }
                        ))
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Hacker News search failed: {e}")
        
        return []
    
    async def search_news(
        self,
        query: str,
        limit: int = 20,
        category: str = 'business',
        language: str = 'en',
        sort_by: str = 'publishedAt'
    ) -> List[SearchResult]:
        """Search for news articles"""
        try:
            cache_key = self._get_cache_key(query, 'news_search', 
                                          limit=limit, category=category, language=language)
            
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            await self.initialize()
            results = []
            
            # Search RSS feeds
            rss_results = await self._search_rss_feeds(query, limit // 2)
            results.extend(rss_results)
            
            # Search Hacker News for tech/crypto news
            if any(keyword in query.lower() for keyword in ['crypto', 'bitcoin', 'blockchain', 'tech', 'trading']):
                hn_results = await self._search_hackernews(query, limit // 2)
                results.extend(hn_results)
            
            # Sort by relevance and timestamp
            results.sort(key=lambda x: (x.relevance_score, x.timestamp), reverse=True)
            results = results[:limit]
            
            self._cache_result(cache_key, results)
            return results
            
        except Exception as e:
            logger.error(f"News search failed for query '{query}': {e}")
            return []
    
    async def _search_rss_feeds(self, query: str, limit: int) -> List[SearchResult]:
        """Search RSS feeds for relevant articles"""
        results = []
        query_terms = set(query.lower().split())
        
        for feed_url in self.rss_feeds[:5]:  # Limit to 5 feeds to avoid timeout
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:10]:  # Check top 10 entries per feed
                            # Calculate relevance score
                            text_to_search = f"{entry.get('title', '')} {entry.get('description', '')}".lower()
                            word_matches = sum(1 for term in query_terms if term in text_to_search)
                            relevance_score = word_matches / len(query_terms) if query_terms else 0
                            
                            if relevance_score > 0.3:  # Only include if somewhat relevant
                                results.append(SearchResult(
                                    title=entry.get('title', ''),
                                    url=entry.get('link', ''),
                                    snippet=self._clean_html(entry.get('description', ''))[:200],
                                    source=feed.feed.get('title', 'RSS Feed'),
                                    timestamp=entry.get('published', datetime.utcnow().isoformat()),
                                    relevance_score=relevance_score,
                                    content_type='news_article',
                                    metadata={
                                        'published': entry.get('published'),
                                        'author': entry.get('author')
                                    }
                                ))
                        
            except Exception as e:
                logger.warning(f"Failed to fetch RSS feed {feed_url}: {e}")
                continue
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content to plain text"""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except:
            return html_content
    
    async def extract_content(self, url: str, content_type: str = 'text') -> Dict[str, Any]:
        """Extract content from a URL"""
        try:
            await self.initialize()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    if content_type == 'text':
                        # Extract text content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text
                        text = soup.get_text()
                        
                        # Clean up text
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = '\n'.join(chunk for chunk in chunks if chunk)
                        
                        # Extract metadata
                        title = soup.find('title')
                        title_text = title.string if title else ""
                        
                        meta_description = soup.find('meta', attrs={'name': 'description'})
                        description = meta_description.get('content', '') if meta_description else ''
                        
                        return {
                            'url': url,
                            'title': title_text,
                            'description': description,
                            'content': text[:5000],  # Limit content size
                            'word_count': len(text.split()),
                            'extracted_at': datetime.utcnow().isoformat()
                        }
                    
                    elif content_type == 'json':
                        # Try to parse as JSON
                        data = await response.json()
                        return {
                            'url': url,
                            'data': data,
                            'extracted_at': datetime.utcnow().isoformat()
                        }
                
                else:
                    return {
                        'error': f"HTTP {response.status}",
                        'url': url,
                        'extracted_at': datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return {
                'error': str(e),
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
    
    async def search_trading_news(self, symbols: List[str], limit: int = 20) -> List[SearchResult]:
        """Search for trading news related to specific symbols"""
        all_results = []
        
        for symbol in symbols[:5]:  # Limit to 5 symbols
            query = f"{symbol} trading analysis price"
            results = await self.search_news(query, limit // len(symbols))
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Sort by relevance and timestamp
        unique_results.sort(key=lambda x: (x.relevance_score, x.timestamp), reverse=True)
        return unique_results[:limit]
    
    async def monitor_sentiment(self, query: str) -> Dict[str, Any]:
        """Monitor sentiment for a query across multiple sources"""
        try:
            # Get recent news and discussions
            news_results = await self.search_news(query, limit=50)
            
            # Simple sentiment analysis based on keywords
            positive_keywords = ['bullish', 'positive', 'growth', 'increase', 'rise', 'gain', 'profit', 'success']
            negative_keywords = ['bearish', 'negative', 'decline', 'decrease', 'fall', 'loss', 'crash', 'fail']
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for result in news_results:
                text = f"{result.title} {result.snippet}".lower()
                
                pos_score = sum(1 for word in positive_keywords if word in text)
                neg_score = sum(1 for word in negative_keywords if word in text)
                
                if pos_score > neg_score:
                    positive_count += 1
                elif neg_score > pos_score:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = len(news_results)
            
            return {
                'query': query,
                'total_articles': total,
                'positive_sentiment': round(positive_count / total * 100, 2) if total > 0 else 0,
                'negative_sentiment': round(negative_count / total * 100, 2) if total > 0 else 0,
                'neutral_sentiment': round(neutral_count / total * 100, 2) if total > 0 else 0,
                'sentiment_score': round((positive_count - negative_count) / total, 2) if total > 0 else 0,
                'articles': news_results[:10],
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sentiment monitoring failed for '{query}': {e}")
            return {'error': str(e)}


# Global instance
web_search_mcp = WebSearchMCPAdapter()


# MCP-compatible interface functions
async def mcp_search_web(
    query: str,
    limit: int = 10,
    search_engine: str = 'duckduckgo',
    safe_search: bool = True,
    region: str = 'us-en'
) -> Dict[str, Any]:
    """MCP-compatible web search"""
    try:
        results = await web_search_mcp.search_web(query, limit, search_engine, safe_search, region)
        return {
            'query': query,
            'results': [result.__dict__ for result in results],
            'count': len(results),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}


async def mcp_search_news(
    query: str,
    limit: int = 20,
    category: str = 'business',
    language: str = 'en'
) -> Dict[str, Any]:
    """MCP-compatible news search"""
    try:
        results = await web_search_mcp.search_news(query, limit, category, language)
        return {
            'query': query,
            'results': [result.__dict__ for result in results],
            'count': len(results),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}


async def mcp_extract_content(url: str, content_type: str = 'text') -> Dict[str, Any]:
    """MCP-compatible content extraction"""
    return await web_search_mcp.extract_content(url, content_type)


async def mcp_monitor_sentiment(query: str) -> Dict[str, Any]:
    """MCP-compatible sentiment monitoring"""
    return await web_search_mcp.monitor_sentiment(query)