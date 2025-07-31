#!/usr/bin/env python3
"""
Enhanced Cache Manager for Cryptometer Analysis
Implements 15-minute cache system to reduce computational load and API calls
"""

import json
import os
import time
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    symbol: str
    data: Dict[str, Any]
    timestamp: datetime
    expires_at: datetime
    data_hash: str
    analysis_type: str
    confidence_level: float
    endpoint_count: int

class EnhancedCacheManager:
    """
    Advanced cache manager for Cryptometer analysis results
    Implements intelligent caching with 15-minute expiry and volatility-based adjustments
    """
    
    def __init__(self, cache_dir: str = "cache", default_ttl_minutes: int = 15):
        """Initialize the Enhanced Cache Manager"""
        self.cache_dir = cache_dir
        self.default_ttl_minutes = default_ttl_minutes
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "saves": 0,
            "evictions": 0,
            "total_requests": 0
        }
        
        logger.info(f"Enhanced Cache Manager initialized with {default_ttl_minutes}min TTL")
    
    def _generate_cache_key(self, symbol: str, analysis_type: str = "comprehensive") -> str:
        """Generate cache key for symbol and analysis type"""
        return f"{symbol.replace('/', '_')}_{analysis_type}".lower()
    
    def _generate_data_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash of data for change detection"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _get_file_path(self, cache_key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_market_volatile(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Check if market is volatile to adjust cache TTL"""
        try:
            # Check for volatility indicators in the data
            if "market_price_analysis" in data:
                price_change = abs(data["market_price_analysis"].get("price_24h_change", 0))
                if price_change > 10:  # More than 10% change in 24h
                    return True
            
            # Check for rapid movements or high volume
            if "endpoint_analyses" in data:
                for analysis in data["endpoint_analyses"]:
                    if "rapid_movements" in analysis.get("endpoint_name", ""):
                        if analysis.get("processed_metrics", {}).get("momentum_score", 50) > 80:
                            return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking volatility for {symbol}: {e}")
            return False
    
    def _calculate_adaptive_ttl(self, symbol: str, data: Dict[str, Any], confidence: float) -> int:
        """Calculate adaptive TTL based on market conditions and confidence"""
        base_ttl = self.default_ttl_minutes
        
        # Adjust based on market volatility
        if self._is_market_volatile(symbol, data):
            base_ttl = max(5, base_ttl // 3)  # Reduce to 5 minutes for volatile markets
            logger.info(f"Volatile market detected for {symbol}, reducing TTL to {base_ttl} minutes")
        
        # Adjust based on confidence level
        if confidence < 0.5:
            base_ttl = max(5, base_ttl // 2)  # Reduce TTL for low confidence data
        elif confidence > 0.8:
            base_ttl = min(30, base_ttl * 1.5)  # Increase TTL for high confidence data
        
        # Adjust based on data quality (endpoint count)
        endpoint_count = len(data.get("endpoint_analyses", []))
        if endpoint_count < 5:
            base_ttl = max(5, base_ttl // 2)  # Reduce TTL for limited data
        elif endpoint_count > 15:
            base_ttl = min(30, base_ttl * 1.2)  # Increase TTL for comprehensive data
        
        return int(base_ttl)
    
    def get(self, symbol: str, analysis_type: str = "comprehensive") -> Optional[Dict[str, Any]]:
        """Get cached analysis for symbol"""
        self.stats["total_requests"] += 1
        cache_key = self._generate_cache_key(symbol, analysis_type)
        
        try:
            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                
                # Check if entry is still valid
                if datetime.now() < entry.expires_at:
                    self.stats["hits"] += 1
                    logger.info(f"Cache HIT for {symbol} (memory) - expires in {(entry.expires_at - datetime.now()).total_seconds():.0f}s")
                    return entry.data
                else:
                    # Remove expired entry from memory
                    del self.memory_cache[cache_key]
                    logger.debug(f"Expired memory cache entry removed for {symbol}")
            
            # Check file cache
            file_path = self._get_file_path(cache_key)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    cache_data = json.load(f)
                
                # Parse cache entry
                entry = CacheEntry(
                    symbol=cache_data["symbol"],
                    data=cache_data["data"],
                    timestamp=datetime.fromisoformat(cache_data["timestamp"]),
                    expires_at=datetime.fromisoformat(cache_data["expires_at"]),
                    data_hash=cache_data["data_hash"],
                    analysis_type=cache_data["analysis_type"],
                    confidence_level=cache_data["confidence_level"],
                    endpoint_count=cache_data["endpoint_count"]
                )
                
                # Check if file cache entry is still valid
                if datetime.now() < entry.expires_at:
                    # Load into memory cache for faster access
                    self.memory_cache[cache_key] = entry
                    self.stats["hits"] += 1
                    logger.info(f"Cache HIT for {symbol} (file) - expires in {(entry.expires_at - datetime.now()).total_seconds():.0f}s")
                    return entry.data
                else:
                    # Remove expired file
                    os.remove(file_path)
                    logger.debug(f"Expired file cache entry removed for {symbol}")
            
            # Cache miss
            self.stats["misses"] += 1
            logger.info(f"Cache MISS for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error reading cache for {symbol}: {e}")
            self.stats["misses"] += 1
            return None
    
    def set(self, symbol: str, data: Dict[str, Any], analysis_type: str = "comprehensive", confidence: float = 0.5) -> bool:
        """Set cached analysis for symbol"""
        cache_key = self._generate_cache_key(symbol, analysis_type)
        
        try:
            # Calculate adaptive TTL
            ttl_minutes = self._calculate_adaptive_ttl(symbol, data, confidence)
            
            # Create cache entry
            now = datetime.now()
            expires_at = now + timedelta(minutes=ttl_minutes)
            data_hash = self._generate_data_hash(data)
            endpoint_count = len(data.get("endpoint_analyses", []))
            
            entry = CacheEntry(
                symbol=symbol,
                data=data,
                timestamp=now,
                expires_at=expires_at,
                data_hash=data_hash,
                analysis_type=analysis_type,
                confidence_level=confidence,
                endpoint_count=endpoint_count
            )
            
            # Store in memory cache
            self.memory_cache[cache_key] = entry
            
            # Store in file cache
            file_path = self._get_file_path(cache_key)
            cache_data = {
                "symbol": entry.symbol,
                "data": entry.data,
                "timestamp": entry.timestamp.isoformat(),
                "expires_at": entry.expires_at.isoformat(),
                "data_hash": entry.data_hash,
                "analysis_type": entry.analysis_type,
                "confidence_level": entry.confidence_level,
                "endpoint_count": entry.endpoint_count
            }
            
            with open(file_path, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            self.stats["saves"] += 1
            logger.info(f"Cache SAVE for {symbol} - TTL: {ttl_minutes}min, expires at {expires_at.strftime('%H:%M:%S')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving cache for {symbol}: {e}")
            return False
    
    def invalidate(self, symbol: str, analysis_type: str = "comprehensive") -> bool:
        """Invalidate cached analysis for symbol"""
        cache_key = self._generate_cache_key(symbol, analysis_type)
        
        try:
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                logger.debug(f"Removed {symbol} from memory cache")
            
            # Remove from file cache
            file_path = self._get_file_path(cache_key)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed {symbol} from file cache")
            
            logger.info(f"Cache invalidated for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {symbol}: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        cleaned_count = 0
        now = datetime.now()
        
        try:
            # Clean memory cache
            expired_keys = [
                key for key, entry in self.memory_cache.items() 
                if now >= entry.expires_at
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleaned_count += 1
            
            # Clean file cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        expires_at = datetime.fromisoformat(cache_data["expires_at"])
                        if now >= expires_at:
                            os.remove(file_path)
                            cleaned_count += 1
                            
                    except Exception as e:
                        logger.debug(f"Error checking file {filename}: {e}")
                        # Remove corrupted files
                        os.remove(file_path)
                        cleaned_count += 1
            
            if cleaned_count > 0:
                self.stats["evictions"] += cleaned_count
                logger.info(f"Cleaned up {cleaned_count} expired cache entries")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0
    
    def get_cache_info(self, symbol: Optional[str] = None, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Get cache information for symbol or overall stats"""
        
        if symbol:
            cache_key = self._generate_cache_key(symbol, analysis_type)
            
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                return {
                    "symbol": entry.symbol,
                    "cached": True,
                    "location": "memory",
                    "timestamp": entry.timestamp.isoformat(),
                    "expires_at": entry.expires_at.isoformat(),
                    "expires_in_seconds": (entry.expires_at - datetime.now()).total_seconds(),
                    "confidence_level": entry.confidence_level,
                    "endpoint_count": entry.endpoint_count,
                    "data_hash": entry.data_hash
                }
            
            file_path = self._get_file_path(cache_key)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        cache_data = json.load(f)
                    
                    expires_at = datetime.fromisoformat(cache_data["expires_at"])
                    return {
                        "symbol": cache_data["symbol"],
                        "cached": True,
                        "location": "file",
                        "timestamp": cache_data["timestamp"],
                        "expires_at": cache_data["expires_at"],
                        "expires_in_seconds": (expires_at - datetime.now()).total_seconds(),
                        "confidence_level": cache_data["confidence_level"],
                        "endpoint_count": cache_data["endpoint_count"],
                        "data_hash": cache_data["data_hash"]
                    }
                except:
                    pass
            
            return {"symbol": symbol, "cached": False}
        
        # Overall cache statistics
        return {
            "cache_stats": self.stats.copy(),
            "memory_cache_size": len(self.memory_cache),
            "hit_rate": self.stats["hits"] / max(1, self.stats["total_requests"]) * 100,
            "default_ttl_minutes": self.default_ttl_minutes,
            "cache_directory": self.cache_dir
        }
    
    def force_refresh(self, symbol: str, analysis_type: str = "comprehensive") -> bool:
        """Force refresh by invalidating cache (next request will fetch fresh data)"""
        return self.invalidate(symbol, analysis_type)
    
    def get_all_cached_symbols(self) -> List[Dict[str, Any]]:
        """Get list of all cached symbols with their info"""
        cached_symbols = []
        
        # From memory cache
        for cache_key, entry in self.memory_cache.items():
            cached_symbols.append({
                "symbol": entry.symbol,
                "analysis_type": entry.analysis_type,
                "location": "memory",
                "expires_at": entry.expires_at.isoformat(),
                "confidence_level": entry.confidence_level,
                "endpoint_count": entry.endpoint_count
            })
        
        # From file cache (excluding those already in memory)
        memory_keys = set(self.memory_cache.keys())
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_key = filename[:-5]  # Remove .json extension
                
                if cache_key not in memory_keys:
                    try:
                        file_path = os.path.join(self.cache_dir, filename)
                        with open(file_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        cached_symbols.append({
                            "symbol": cache_data["symbol"],
                            "analysis_type": cache_data["analysis_type"],
                            "location": "file",
                            "expires_at": cache_data["expires_at"],
                            "confidence_level": cache_data["confidence_level"],
                            "endpoint_count": cache_data["endpoint_count"]
                        })
                    except:
                        continue
        
        return cached_symbols

# Global cache manager instance
cache_manager = EnhancedCacheManager()