import time

class PersistentContext:
    def __init__(self, value: any):
        self._value = value
        self._last_access_time = time.time()

    def get_value(self) -> any:
        self._last_access_time = time.time()
        return self._value
    
    def set_value(self, value: any):
        self._value = value
        self._last_access_time = time.time()

class PersistentContextCache:
    def __init__(self, timeout: float = 300.0, check_interval: float = 60.0):
        self._data: dict[str, PersistentContext] = {}
        self._timeout = timeout
        self._check_interval = check_interval
        self._last_cleanup_time = time.time()

    def get_context(self, key: str) -> PersistentContext:
        self._cleanup_expired()
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Context with key '{key}' not found")

    def has_context(self, key: str) -> bool:
        self._cleanup_expired()
        return key in self._data

    def create_context(self, key: str, value: any) -> PersistentContext:
        self._cleanup_expired()
        context = PersistentContext(value)
        self._data[key] = context
        return context

    def _cleanup_expired(self):
        current_time = time.time()
        # Only perform cleanup if enough time has passed since last cleanup
        if current_time - self._last_cleanup_time < self._check_interval:
            return

        expired_keys = []
        for key, context in self._data.items():
            if current_time - context._last_access_time > self._timeout:
                expired_keys.append(key)

        for key in expired_keys:
            del self._data[key]

        self._last_cleanup_time = current_time

    def force_cleanup(self):
        """Force immediate cleanup of expired contexts"""
        self._cleanup_expired()

    def size(self) -> int:
        """Get the current number of contexts in the cache"""
        return len(self._data)

_global_context_cache = PersistentContextCache()

def has_persistent_context(key: str) -> bool:
    return _global_context_cache.has_context(key)

def get_persistent_context(key: str, default_value = None) -> PersistentContext:
    if has_persistent_context(key):
        return _global_context_cache.get_context(key)
    return _global_context_cache.create_context(key, default_value)