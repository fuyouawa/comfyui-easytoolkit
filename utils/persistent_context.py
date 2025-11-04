import time
import os
import pickle
import folder_paths
from .config import get_config

class PersistentContext:
    def __init__(self, value: any, cache=None):
        self._value = value
        self._cache = cache
        self.update_access_time()

    def update_access_time(self):
        self._last_access_time = time.time()

    def get_value(self) -> any:
        self.update_access_time()
        return self._value
    
    def set_value(self, value: any, save: bool = True):
        self._value = value
        self.update_access_time()
        # Save to disk whenever value is set
        if self._cache is not None and save:
            self._cache.save()

class PersistentContextCache:
    def __init__(self):
        # Load configuration from config file
        config = get_config().get_persistent_context_config()
        self._timeout = config.get('timeout', 300.0)
        self._check_interval = config.get('check_interval', 60.0)
        self._auto_save_interval = config.get('auto_save_interval', 60.0)
        
        self._data: dict[str, PersistentContext] = {}
        self._last_cleanup_time = time.time()
        self._storage_file = self._get_storage_path()
        self._load_from_disk()

    def get_context(self, key: str) -> PersistentContext:
        self._update_context_access_time(key)
        self._cleanup_expired()
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Context with key '{key}' not found")

    def has_context(self, key: str) -> bool:
        self._update_context_access_time(key)
        self._cleanup_expired()
        return key in self._data

    def create_context(self, key: str, value: any) -> PersistentContext:
        self._update_context_access_time(key)
        self._cleanup_expired()
        context = PersistentContext(value, cache=self)
        self._data[key] = context
        return context

    def _update_context_access_time(self, key: str):
        if key in self._data:
            self._data[key].update_access_time()

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
        
        # Save to disk if any contexts were removed
        if expired_keys:
            self._save_to_disk()
    
    def _auto_save_check(self):
        """Check if it's time to auto-save and save if needed"""
        # Skip if auto-save is disabled (interval <= 0)
        if self._auto_save_interval <= 0:
            return
        
        current_time = time.time()
        if current_time - self._last_save_time >= self._auto_save_interval:
            self._save_to_disk()

    def save(self):
        """Manually trigger a save to disk"""
        self._save_to_disk()
    
    def _get_storage_path(self) -> str:
        """Get the storage path for persistent context data"""
        user_dir = folder_paths.get_user_directory()
        storage_dir = os.path.join(user_dir, "default", "comfyui-easytoolkit")
        
        # Create directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        return os.path.join(storage_dir, "persistent_context.pkl")
    
    def _save_to_disk(self):
        """Save the context data to disk"""
        try:
            self._last_save_time = time.time()
            # Prepare data for serialization
            save_data = {
                'data': self._data,
                'last_cleanup_time': self._last_cleanup_time,
                'last_save_time': self._last_save_time
            }
            
            # Write to a temporary file first, then rename (atomic operation)
            temp_file = self._storage_file + '.tmp'
            with open(temp_file, 'wb') as f:
                pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Rename temp file to actual file (atomic on most systems)
            if os.path.exists(self._storage_file):
                os.replace(temp_file, self._storage_file)
            else:
                os.rename(temp_file, self._storage_file)
                
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to save persistent context to disk: {e}")
    
    def _load_from_disk(self):
        """Load the context data from disk"""
        try:
            if not os.path.exists(self._storage_file):
                return
            
            with open(self._storage_file, 'rb') as f:
                save_data = pickle.load(f)
            
            # Restore data (but keep current config values for timeout, check_interval, auto_save_interval)
            self._data = save_data.get('data', {})
            self._last_cleanup_time = save_data.get('last_cleanup_time', time.time())
            self._last_save_time = save_data.get('last_save_time', time.time())
            
            # Set cache reference for all loaded contexts
            for context in self._data.values():
                context._cache = self
            
            print(f"[comfyui-easytoolkit] Loaded {len(self._data)} persistent contexts from disk")
            
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load persistent context from disk: {e}")
            # If loading fails, start with empty data
            self._data = {}

_global_context_cache = PersistentContextCache()

def has_persistent_context(key: str) -> bool:
    return _global_context_cache.has_context(key)

def get_persistent_context(key: str, default_value = None) -> PersistentContext:
    if has_persistent_context(key):
        return _global_context_cache.get_context(key)
    return _global_context_cache.create_context(key, default_value)

def save_persistent_context():
    """Manually save all persistent contexts to disk"""
    _global_context_cache.save()