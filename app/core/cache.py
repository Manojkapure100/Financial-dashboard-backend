"""
Cache management
"""


class CacheManager:
    """Manages application caching"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str):
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value):
        """Set value in cache"""
        self.cache[key] = value
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]


cache_manager = CacheManager()
