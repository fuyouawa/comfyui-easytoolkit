import time
import os
import pickle
import threading
import atexit
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from .config import get_config
from .. import register_route

class PersistentContext:
    def __init__(self, value: any, key: str = None, cache=None):
        self._value = value
        self._key = key
        self._cache = cache
        self._last_access_time = 0.0

    def update_access_time(self):
        self._last_access_time = time.time()

    def get_key(self) -> str:
        return self._key

    def get_value(self) -> any:
        self.update_access_time()
        return self._value
    
    def set_value(self, value: any, save: bool = True):
        self._value = value
        self.update_access_time()
        # Save to disk whenever value is set
        if self._cache is not None and save:
            self._cache.save()
    
    def __getstate__(self):
        """Exclude _cache when pickling to avoid circular reference issues"""
        state = self.__dict__.copy()
        state['_cache'] = None
        return state
    
    def __setstate__(self, state):
        """Restore state when unpickling"""
        self.__dict__.update(state)

class PersistentContextCache:
    def __init__(self):
        # Load configuration from config file
        config = get_config().get_persistent_context_config()
        self._auto_save_interval = config.get('auto_save_interval', 60.0)
        
        self._data: dict[str, PersistentContext] = {}
        self._last_save_time = time.time()
        
        # Thread pool for async disk operations
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="persistent_context_saver")
        self._save_lock = threading.Lock()
        self._pending_save = False
        self._needs_another_save = False
        self._save_future = None

    def get_context(self, key: str) -> PersistentContext:
        self.update_context_access_time(key)
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Context with key '{key}' not found")

    def has_context(self, key: str) -> bool:
        self.update_context_access_time(key)
        return key in self._data

    def remove_context(self, key: str):
        self.update_context_access_time(key)
        if key in self._data:
            del self._data[key]
        self.save()

    def create_context(self, key: str, value: any) -> PersistentContext:
        context = PersistentContext(value, key=key, cache=self)
        self._data[key] = context
        return context

    def resolve_contexts_by_value_type(self, value_type: type) -> list[PersistentContext]:
        """Get all contexts whose value is an instance of the specified type
        
        Args:
            value_type: The type to filter by (e.g., str, int, dict, list, or custom classes)
        
        Returns:
            List of PersistentContext objects whose values match the specified type
        """
        result = []
        for context in self._data.values():
            if isinstance(context.get_value(), value_type):
                result.append(context)
        return result

    def update_context_access_time(self, key: str):
        if key in self._data:
            self._data[key].update_access_time()
    
    def save(self):
        pass
    
    def shutdown(self):
        """Shutdown the cache and save all pending data"""
        # Trigger a save and wait for all pending saves to complete
        self.save()
        
        # Shutdown the thread pool (will wait for all tasks to complete)
        self._executor.shutdown(wait=True)
    
_global_context_cache = PersistentContextCache()

def has_context(key: str) -> bool:
    return _global_context_cache.has_context(key)

def remove_context(key: str):
    return _global_context_cache.remove_context(key)

def get_context(key: str, default_value = None) -> PersistentContext:
    if has_context(key):
        return _global_context_cache.get_context(key)
    return _global_context_cache.create_context(key, default_value)

def update_context(key: str):
    return _global_context_cache.update_context_access_time(key)

def resolve_contexts_by_value_type(value_type: type) -> list[PersistentContext]:
    """Get all persistent contexts whose value is an instance of the specified type
    
    Args:
        value_type: The type to filter by (e.g., str, int, dict, list, or custom classes)
    
    Returns:
        List of PersistentContext objects whose values match the specified type
    
    Example:
        # Get all contexts with string values
        str_contexts = get_persistent_contexts_by_value_type(str)
        for ctx in str_contexts:
            print(f"Key: {ctx.get_key()}, Value: {ctx.get_value()}")
        
        # Get all contexts with dict values
        dict_contexts = get_persistent_contexts_by_value_type(dict)
    """
    return _global_context_cache.resolve_contexts_by_value_type(value_type)

def _shutdown_handler():
    """Handler to ensure data is saved on program exit"""
    try:
        _global_context_cache.shutdown()
        print("[comfyui-easytoolkit] Persistent context cache shutdown complete")
    except Exception as e:
        print(f"[comfyui-easytoolkit] Error during shutdown: {e}")

# Register shutdown handler
atexit.register(_shutdown_handler)


@register_route("/context/remove_key")
async def handle_clear(request):
    """Clear the persistent context for a given key"""
    data = await request.json()
    key = data.get("key", "")

    if not key or not has_context(key):
        return web.json_response({"success": False, "error": "没有上下文数据。"})
    
    # Clear the persistent context by setting it to None
    remove_context(key)
    return web.json_response({"success": True})