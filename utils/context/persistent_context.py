"""
Persistent context object that holds a value with metadata.
"""
import time


class PersistentContext:
    def __init__(self, value: any, key: str = None, cache=None, auto_save: bool = True):
        self._value = value
        self._key = key
        self._cache = cache
        self._last_access_time = 0.0
        self._dirty = True  # Mark as dirty when created

    def update_access_time(self):
        self._last_access_time = time.time()

    def get_key(self) -> str:
        return self._key

    def get_value(self) -> any:
        self.update_access_time()
        return self._value
    
    def _get_auto_save(self) -> bool:
        """Get auto_save setting from config (real-time) via cache"""
        if self._cache is not None:
            return self._cache._get_auto_save()
        # Default to False if no cache is available
        return False
    
    def set_value(self, value: any, save: bool = None):
        self._value = value
        self._dirty = True  # Mark as dirty when value changes
        self.update_access_time()
        # Save to disk based on auto_save setting or explicit save parameter
        should_save = save if save is not None else self._get_auto_save()
        if self._cache is not None and should_save:
            self._cache.save()
    
    def is_dirty(self) -> bool:
        """Check if this context has unsaved changes"""
        return self._dirty
    
    def mark_clean(self):
        """Mark this context as clean (saved)"""
        self._dirty = False
    
    def __getstate__(self):
        """Only serialize _last_access_time and _value fields"""
        # Only save these two fields, other fields will be restored during deserialization
        return {
            '_last_access_time': self._last_access_time,
            '_value': self._value
        }
    
    def __setstate__(self, state):
        """Restore state when unpickling and check for empty values"""
        # Restore the serialized fields
        self._last_access_time = state.get('_last_access_time', 0.0)
        self._value = state.get('_value', None)
        
        # These fields will be set by the cache after loading
        self._key = None
        self._cache = None
        self._dirty = False  # Not dirty when loaded from disk

