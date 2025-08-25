"""
Cache Manager - Intelligent caching for LLM responses and analysis results
"""

import hashlib
import json
import time
import os
from typing import Any, Optional, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    key: str
    value: Any
    timestamp: float
    access_count: int
    cost_saved: float

class CacheManager:
    """Intelligent caching system for LLM responses and expensive computations"""
    
    def __init__(self, cache_dir: str = "cache", ttl_seconds: int = 3600):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.cost_saved = 0.0
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load persistent cache on startup
        self._load_persistent_cache()
    
    def _generate_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, str):
            content = data
        elif isinstance(data, dict):
            content = json.dumps(data, sort_keys=True)
        else:
            content = str(data)
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        return (time.time() - entry.timestamp) > self.ttl_seconds
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get cached value"""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            if not self._is_expired(entry):
                entry.access_count += 1
                self.hit_count += 1
                self.cost_saved += entry.cost_saved
                
                logger.debug(f"Cache HIT: {key} (accessed {entry.access_count} times)")
                return entry.value
            else:
                # Remove expired entry
                del self.memory_cache[key]
                self._remove_persistent_cache(key)
        
        # Check persistent cache
        value = self._load_from_persistent_cache(key)
        if value is not None:
            # Move to memory cache
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                access_count=1,
                cost_saved=0.01  # Estimated cost saved
            )
            self.memory_cache[key] = entry
            self.hit_count += 1
            
            logger.debug(f"Cache HIT (persistent): {key}")
            return value
        
        self.miss_count += 1
        logger.debug(f"Cache MISS: {key}")
        return default
    
    def set(self, key: str, value: Any, cost_saved: float = 0.01):
        """Set cached value"""
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            access_count=0,
            cost_saved=cost_saved
        )
        
        self.memory_cache[key] = entry
        self._save_to_persistent_cache(key, value)
        
        logger.debug(f"Cache SET: {key} (cost saved: ${cost_saved:.4f})")
    
    def cache_llm_response(self, prompt: str, system_prompt: str, response: Any, cost: float = 0.01):
        """Cache LLM response with intelligent key generation"""
        cache_data = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model": getattr(response, 'model', 'unknown'),
            "timestamp": time.time()
        }
        
        key = self._generate_key(cache_data)
        self.set(key, response, cost_saved=cost)
        
        return key
    
    def get_llm_response(self, prompt: str, system_prompt: str, model: str = None) -> Optional[Any]:
        """Get cached LLM response"""
        cache_data = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model": model or 'unknown',
            "timestamp": 0  # Ignore timestamp for lookup
        }
        
        # Try exact match first
        key = self._generate_key(cache_data)
        response = self.get(key)
        
        if response:
            return response
        
        # Try without model specification
        cache_data_no_model = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "model": 'unknown',
            "timestamp": 0
        }
        key = self._generate_key(cache_data_no_model)
        
        return self.get(key)
    
    def cache_analysis_result(self, input_data: str, analysis_type: str, result: Any, cost: float = 0.01):
        """Cache analysis results"""
        cache_data = {
            "input": input_data[:500],  # Truncate for key generation
            "analysis_type": analysis_type,
            "timestamp": time.time()
        }
        
        key = self._generate_key(cache_data)
        self.set(key, result, cost_saved=cost)
        
        return key
    
    def get_analysis_result(self, input_data: str, analysis_type: str) -> Optional[Any]:
        """Get cached analysis result"""
        cache_data = {
            "input": input_data[:500],
            "analysis_type": analysis_type,
            "timestamp": 0
        }
        
        key = self._generate_key(cache_data)
        return self.get(key)
    
    def _save_to_persistent_cache(self, key: str, value: Any):
        """Save to persistent cache file"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            # Prepare data for JSON serialization
            if hasattr(value, '__dict__'):
                # Handle objects with attributes
                cache_data = {
                    "type": value.__class__.__name__,
                    "data": value.__dict__ if hasattr(value, '__dict__') else str(value),
                    "timestamp": time.time()
                }
            else:
                cache_data = {
                    "type": "primitive",
                    "data": value,
                    "timestamp": time.time()
                }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.warning(f"Failed to save persistent cache for {key}: {e}")
    
    def _load_from_persistent_cache(self, key: str) -> Optional[Any]:
        """Load from persistent cache file"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if expired
            if (time.time() - cache_data.get("timestamp", 0)) > self.ttl_seconds:
                self._remove_persistent_cache(key)
                return None
            
            return cache_data.get("data")
            
        except Exception as e:
            logger.warning(f"Failed to load persistent cache for {key}: {e}")
            return None
    
    def _remove_persistent_cache(self, key: str):
        """Remove persistent cache file"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        except Exception as e:
            logger.warning(f"Failed to remove persistent cache for {key}: {e}")
    
    def _load_persistent_cache(self):
        """Load all persistent cache entries at startup"""
        if not os.path.exists(self.cache_dir):
            return
        
        loaded_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                key = filename[:-5]  # Remove .json extension
                value = self._load_from_persistent_cache(key)
                
                if value is not None:
                    entry = CacheEntry(
                        key=key,
                        value=value,
                        timestamp=time.time(),
                        access_count=0,
                        cost_saved=0.01
                    )
                    self.memory_cache[key] = entry
                    loaded_count += 1
        
        if loaded_count > 0:
            logger.info(f"Loaded {loaded_count} cache entries from persistent storage")
    
    def clear_cache(self):
        """Clear all cache data"""
        self.memory_cache.clear()
        
        # Clear persistent cache
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        
        self.hit_count = 0
        self.miss_count = 0
        self.cost_saved = 0.0
        
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate_percent": f"{hit_rate:.1f}%",
            "total_cost_saved": f"${self.cost_saved:.4f}",
            "cache_entries": len(self.memory_cache),
            "avg_cost_per_hit": f"${self.cost_saved / max(1, self.hit_count):.4f}"
        }
    
    def optimize_cache(self):
        """Optimize cache by removing least used entries"""
        if len(self.memory_cache) < 100:  # Only optimize when cache is large
            return
        
        # Sort by access count and remove bottom 25%
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].access_count
        )
        
        remove_count = len(sorted_entries) // 4
        for key, _ in sorted_entries[:remove_count]:
            del self.memory_cache[key]
            self._remove_persistent_cache(key)
        
        logger.info(f"Optimized cache: removed {remove_count} least-used entries")

# Global cache manager
cache_manager = CacheManager()

# Cache decorator for functions
def cached_result(cache_key_func=None, ttl_seconds=3600):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                key = cache_key_func(*args, **kwargs)
            else:
                key = cache_manager._generate_key(f"{func.__name__}_{args}_{kwargs}")
            
            # Try to get from cache
            cached_value = cache_manager.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(key, result)
            
            return result
        
        return wrapper
    return decorator