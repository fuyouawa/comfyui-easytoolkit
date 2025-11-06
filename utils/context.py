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
        self._cache_file_path = get_config().get_cache_file_path()
        
        self._data: dict[str, PersistentContext] = {}
        self._last_save_time = time.time()
        
        # Thread pool for async disk operations
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="persistent_context_saver")
        self._save_lock = threading.Lock()
        self._pending_save = False
        self._needs_another_save = False
        self._save_future = None
        self._shutdown_flag = False
        
        # Load existing cache from disk
        self._load()
        
        # Start auto-save background thread
        if self._auto_save_interval > 0:
            self._auto_save_thread = threading.Thread(
                target=self._auto_save_loop,
                daemon=True,
                name="persistent_context_auto_saver"
            )
            self._auto_save_thread.start()
        else:
            self._auto_save_thread = None

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
        # Trigger an async save after creating a new context
        self.save()
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
    
    def _load(self):
        """Load cache from disk"""
        if not os.path.exists(self._cache_file_path):
            print(f"[comfyui-easytoolkit] No existing cache file found at {self._cache_file_path}")
            return
        
        try:
            with open(self._cache_file_path, 'rb') as f:
                self._data = pickle.load(f)
            
            # Restore cache reference for all loaded contexts
            for context in self._data.values():
                context._cache = self
            
            print(f"[comfyui-easytoolkit] Loaded {len(self._data)} context(s) from {self._cache_file_path}")
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load cache file: {e}")
            print(f"[comfyui-easytoolkit] Starting with empty cache")
            self._data = {}
    
    def _do_save(self):
        """Internal method to perform the actual save operation"""
        try:
            # Create a temporary file first to avoid data corruption
            temp_file = self._cache_file_path + '.tmp'
            
            with open(temp_file, 'wb') as f:
                pickle.dump(self._data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Replace the old file with the new one atomically
            if os.path.exists(self._cache_file_path):
                os.replace(temp_file, self._cache_file_path)
            else:
                os.rename(temp_file, self._cache_file_path)
            
            self._last_save_time = time.time()
            print(f"[comfyui-easytoolkit] Saved {len(self._data)} context(s) to {self._cache_file_path}")
            return True
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error saving cache: {e}")
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            return False
    
    def _save_task(self):
        """Task to run in thread pool for async saves"""
        with self._save_lock:
            self._pending_save = True
            self._needs_another_save = False
        
        success = self._do_save()
        
        with self._save_lock:
            self._pending_save = False
            # If another save was requested while we were saving, do it now
            if self._needs_another_save and not self._shutdown_flag:
                self._save_future = self._executor.submit(self._save_task)
            else:
                self._save_future = None
        
        return success
    
    def save(self, force_sync=False):
        """Save cache to disk asynchronously (or synchronously if force_sync=True)"""
        if self._shutdown_flag:
            return
        
        if force_sync:
            # Synchronous save
            return self._do_save()
        
        # Asynchronous save
        with self._save_lock:
            if self._pending_save:
                # A save is already in progress, mark that we need another one
                self._needs_another_save = True
            else:
                # Submit a new save task
                self._save_future = self._executor.submit(self._save_task)
    
    def should_auto_save(self) -> bool:
        """Check if it's time for an automatic save"""
        if self._auto_save_interval <= 0:
            return False
        return (time.time() - self._last_save_time) >= self._auto_save_interval
    
    def _auto_save_loop(self):
        """Background thread that periodically saves the cache"""
        print("[comfyui-easytoolkit] Auto-save thread started")
        
        while not self._shutdown_flag:
            try:
                # Sleep for a short interval to check shutdown flag regularly
                time.sleep(min(1.0, self._auto_save_interval))
                
                if self._shutdown_flag:
                    break
                
                if self.should_auto_save():
                    self.save()
            except Exception as e:
                print(f"[comfyui-easytoolkit] Error in auto-save loop: {e}")
        
        print("[comfyui-easytoolkit] Auto-save thread stopped")
    
    def shutdown(self):
        """Shutdown the cache and save all pending data"""
        print("[comfyui-easytoolkit] Shutting down persistent context cache...")
        self._shutdown_flag = True
        
        # Wait for auto-save thread to finish
        if self._auto_save_thread is not None and self._auto_save_thread.is_alive():
            self._auto_save_thread.join(timeout=2.0)
        
        # Wait for any pending save to complete
        if self._save_future is not None:
            try:
                self._save_future.result(timeout=5.0)
            except Exception as e:
                print(f"[comfyui-easytoolkit] Error waiting for pending save: {e}")
        
        # Perform a final synchronous save
        self._do_save()
        
        # Shutdown the thread pool (will wait for all tasks to complete)
        self._executor.shutdown(wait=True)
    
# Global context cache (initialized lazily)
_global_context_cache = None
_initialization_lock = threading.Lock()

def _ensure_initialized():
    """Ensure the global context cache is initialized (lazy initialization)"""
    global _global_context_cache
    
    if _global_context_cache is not None:
        return
    
    with _initialization_lock:
        # Double-check pattern
        if _global_context_cache is not None:
            return
        
        # Check if lazy initialization is enabled
        config = get_config().get_persistent_context_config()
        lazy_init = config.get('lazy_initialization', True)
        
        if not lazy_init:
            # This shouldn't happen in normal flow, but handle it anyway
            _global_context_cache = PersistentContextCache()
            return
        
        # Initialize the cache
        print("[comfyui-easytoolkit] Initializing persistent context cache (lazy initialization)...")
        _global_context_cache = PersistentContextCache()

def has_persistent_context(key: str) -> bool:
    _ensure_initialized()
    return _global_context_cache.has_context(key)

def remove_persistent_context(key: str):
    _ensure_initialized()
    return _global_context_cache.remove_context(key)

def get_persistent_context(key: str, default_value = None) -> PersistentContext:
    _ensure_initialized()
    if _global_context_cache.has_context(key):
        return _global_context_cache.get_context(key)
    return _global_context_cache.create_context(key, default_value)

def update_persistent_context(key: str):
    _ensure_initialized()
    return _global_context_cache.update_context_access_time(key)

def resolve_persistent_contexts_by_value_type(value_type: type) -> list[PersistentContext]:
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
    _ensure_initialized()
    return _global_context_cache.resolve_contexts_by_value_type(value_type)

def _shutdown_handler():
    """Handler to ensure data is saved on program exit"""
    global _global_context_cache
    
    # Only shutdown if cache was initialized
    if _global_context_cache is None:
        return
    
    try:
        _global_context_cache.shutdown()
        print("[comfyui-easytoolkit] Persistent context cache shutdown complete")
    except Exception as e:
        print(f"[comfyui-easytoolkit] Error during shutdown: {e}")

# Register shutdown handler
atexit.register(_shutdown_handler)

# Initialize immediately if lazy_initialization is disabled
config = get_config().get_persistent_context_config()
if not config.get('lazy_initialization', True):
    print("[comfyui-easytoolkit] Lazy initialization disabled, initializing persistent context cache immediately...")
    _global_context_cache = PersistentContextCache()


@register_route("/persistent_context/remove_key")
async def handle_clear(request):
    """Clear the persistent context for a given key"""
    _ensure_initialized()
    
    data = await request.json()
    key = data.get("key", "")

    if not key or not has_persistent_context(key):
        return web.json_response({"success": False, "error": "没有上下文数据。"})
    
    # Clear the persistent context by setting it to None
    remove_persistent_context(key)
    return web.json_response({"success": True})