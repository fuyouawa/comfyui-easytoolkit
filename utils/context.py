import time
import os
import pickle
import gzip
import threading
import atexit
from concurrent.futures import ThreadPoolExecutor
from .config import get_config
from .. import register_route

class PersistentContext:
    def __init__(self, value: any, key: str = None, cache=None, auto_save: bool = True):
        self._value = value
        self._key = key
        self._cache = cache
        self._auto_save = auto_save
        self._last_access_time = 0.0
        self._dirty = True  # Mark as dirty when created

    def update_access_time(self):
        self._last_access_time = time.time()

    def get_key(self) -> str:
        return self._key

    def get_value(self) -> any:
        self.update_access_time()
        return self._value
    
    def set_value(self, value: any, save: bool = None):
        self._value = value
        self._dirty = True  # Mark as dirty when value changes
        self.update_access_time()
        # Save to disk based on auto_save setting or explicit save parameter
        should_save = save if save is not None else self._auto_save
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
        self._auto_save = True
        self._dirty = False  # Not dirty when loaded from disk

class PersistentContextCache:
    def __init__(self):
        # Load configuration from config file
        config = get_config().get_persistent_context_config()
        # Get cache directory directly
        self._cache_dir = get_config().get_cache_directory_path()
        self._auto_save = config.get('auto_save', True)
        
        self._data: dict[str, PersistentContext] = {}
        self._last_save_time = time.time()
        
        # Thread pool for async disk operations
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="persistent_context_saver")
        self._save_lock = threading.Lock()
        self._pending_save = False
        self._needs_another_save = False
        self._save_future = None
        self._shutdown_flag = False
        
        # Create cache directory if it doesn't exist
        os.makedirs(self._cache_dir, exist_ok=True)
        
        # Load existing cache from disk
        self._load()
        
        # Load cleanup configuration
        self._max_cache_size_bytes = config.get('max_cache_size_mb', 100) * 1024 * 1024
        self._old_data_threshold_seconds = config.get('old_data_threshold_hours', 24) * 3600
        self._absolute_max_cache_size_bytes = config.get('absolute_max_cache_size_mb', 200) * 1024 * 1024
        self._max_context_size_bytes = config.get('max_context_size_mb', 50) * 1024 * 1024
        self._max_key_length = config.get('max_key_length', 256)
    
    @staticmethod
    def _sanitize_filename(key: str) -> str:
        """Convert a key to a safe filename by URL-encoding special characters"""
        import urllib.parse
        # URL encode the key to make it filesystem-safe
        safe_name = urllib.parse.quote(key, safe='')
        # Limit filename length to avoid filesystem issues
        if len(safe_name) > 200:
            # Use hash for very long keys
            import hashlib
            hash_suffix = hashlib.md5(safe_name.encode()).hexdigest()[:16]
            safe_name = safe_name[:180] + '_' + hash_suffix
        return safe_name + '.pkl'
    
    def _get_context_file_path(self, key: str) -> str:
        """Get the file path for a context key"""
        filename = self._sanitize_filename(key)
        return os.path.join(self._cache_dir, filename)
    
    def _validate_key(self, key: str):
        """Validate key length and format
        
        Raises:
            ValueError: If key is invalid
        """
        if not key:
            raise ValueError("Context key cannot be empty")
        
        if self._max_key_length > 0 and len(key) > self._max_key_length:
            raise ValueError(f"Context key length ({len(key)}) exceeds maximum allowed length ({self._max_key_length})")

    def get_context(self, key: str) -> PersistentContext:
        self._validate_key(key)
        self.update_context_access_time(key)
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Context with key '{key}' not found")

    def has_context(self, key: str) -> bool:
        try:
            self._validate_key(key)
        except ValueError:
            return False
        self.update_context_access_time(key)
        return key in self._data

    def remove_context(self, key: str):
        self._validate_key(key)
        self.update_context_access_time(key)
        if key in self._data:
            del self._data[key]
            # Delete the file from disk
            file_path = self._get_context_file_path(key)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"[comfyui-easytoolkit] Removed context file: {file_path}")
            except Exception as e:
                print(f"[comfyui-easytoolkit] Error removing context file {file_path}: {e}")

    def create_context(self, key: str, value: any) -> PersistentContext:
        self._validate_key(key)
        context = PersistentContext(value, key=key, cache=self, auto_save=self._auto_save)
        self._data[key] = context
        # Trigger an async save after creating a new context (if auto_save is enabled)
        if self._auto_save:
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
        try:
            self._validate_key(key)
        except ValueError:
            return
        if key in self._data:
            self._data[key].update_access_time()
    
    def _load(self):
        """Load cache from disk - scan directory for individual context files"""
        if not os.path.exists(self._cache_dir):
            print(f"[comfyui-easytoolkit] No existing cache directory found at {self._cache_dir}")
            return
        
        # Scan directory for .pkl files
        try:
            loaded_count = 0
            failed_count = 0
            
            for filename in os.listdir(self._cache_dir):
                if not filename.endswith('.pkl'):
                    continue
                
                file_path = os.path.join(self._cache_dir, filename)
                
                try:
                    # Load and decompress the context from file
                    with open(file_path, 'rb') as f:
                        compressed_data = f.read()
                    
                    # Decompress and deserialize
                    decompressed_data = gzip.decompress(compressed_data)
                    data = pickle.loads(decompressed_data)
                    
                    # Extract key and context from saved data
                    if not isinstance(data, dict) or 'key' not in data or 'context' not in data:
                        failed_count += 1
                        print(f"[comfyui-easytoolkit] Error: Invalid format in {filename}, skipping")
                        continue
                    
                    key = data['key']
                    context_obj = data['context']
                    
                    # Restore the fields that were not serialized
                    context_obj._key = key
                    context_obj._cache = self
                    context_obj._auto_save = self._auto_save
                    context_obj._dirty = False  # Loaded from disk, so not dirty
                    
                    # Check if value is empty (indicates serialization failure)
                    value = context_obj.get_value()
                    if value is None or (hasattr(value, '__len__') and len(value) == 0):
                        failed_count += 1
                        print(f"[comfyui-easytoolkit] Error: Context '{key}' has empty value, skipping")
                        # Delete the corrupted file
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        continue
                    
                    self._data[key] = context_obj
                    loaded_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    print(f"[comfyui-easytoolkit] Warning: Failed to load context from {filename}: {e}")
                    continue
            
            print(f"[comfyui-easytoolkit] Loaded {loaded_count} context(s) from {self._cache_dir}")
            if failed_count > 0:
                print(f"[comfyui-easytoolkit] Failed to load {failed_count} context file(s)")
                
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to scan cache directory: {e}")
            print(f"[comfyui-easytoolkit] Starting with empty cache")
            self._data = {}
    
    def _do_save(self):
        """Internal method to perform the actual save operation - save only dirty contexts"""
        try:
            saved_count = 0
            removed_count = 0
            skipped_count = 0
            oversized_count = 0
            
            # Only save dirty contexts
            for key, context in list(self._data.items()):
                # Skip if not dirty
                if not context.is_dirty():
                    skipped_count += 1
                    continue
                
                value = context.get_value()
                
                # Check if value is empty (None, empty string, empty list, empty dict, etc.)
                if value is None or (hasattr(value, '__len__') and len(value) == 0):
                    removed_count += 1
                    print(f"[comfyui-easytoolkit] Warning: Removing context '{key}' with empty value")
                    # Remove from memory
                    del self._data[key]
                    # Remove file if exists
                    file_path = self._get_context_file_path(key)
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except:
                        pass
                    continue
                
                # Save this context to its own file
                file_path = self._get_context_file_path(key)
                temp_file = file_path + '.tmp'
                
                try:
                    # Save with metadata (key and context)
                    data = {
                        'key': key,
                        'context': context
                    }
                    
                    # Serialize to bytes
                    serialized_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
                    
                    # Compress the data
                    compressed_data = gzip.compress(serialized_data, compresslevel=6)
                    data_size = len(compressed_data)
                    
                    # Check if data size exceeds limit (if limit is set)
                    if self._max_context_size_bytes > 0 and data_size > self._max_context_size_bytes:
                        oversized_count += 1
                        size_mb = data_size / 1024 / 1024
                        limit_mb = self._max_context_size_bytes / 1024 / 1024
                        print(f"[comfyui-easytoolkit] Warning: Context '{key}' size ({size_mb:.2f} MB) exceeds limit ({limit_mb:.2f} MB), skipping save")
                        # Mark as clean to avoid repeated attempts to save
                        context.mark_clean()
                        # Remove file if exists (since we won't save it)
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"[comfyui-easytoolkit] Removed existing oversized context file: {file_path}")
                        except:
                            pass
                        continue
                    
                    # Write compressed data to temp file
                    with open(temp_file, 'wb') as f:
                        f.write(compressed_data)
                    
                    # Replace the old file with the new one atomically
                    if os.path.exists(file_path):
                        os.replace(temp_file, file_path)
                    else:
                        os.rename(temp_file, file_path)
                    
                    # Mark as clean after successful save
                    context.mark_clean()
                    saved_count += 1
                    
                except Exception as e:
                    print(f"[comfyui-easytoolkit] Error saving context '{key}': {e}")
                    # Clean up temp file if it exists
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
            
            self._last_save_time = time.time()
            
            if saved_count > 0:
                print(f"[comfyui-easytoolkit] Saved {saved_count} context(s) to {self._cache_dir}")
            if removed_count > 0:
                print(f"[comfyui-easytoolkit] Removed {removed_count} context(s) with empty values")
            if oversized_count > 0:
                print(f"[comfyui-easytoolkit] Skipped {oversized_count} oversized context(s)")
            
            return True
            
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error during save operation: {e}")
            return False
    
    def _calculate_total_cache_size(self) -> int:
        """Calculate total size of all cache files in bytes"""
        total_size = 0
        try:
            if not os.path.exists(self._cache_dir):
                return 0
            
            for filename in os.listdir(self._cache_dir):
                if not filename.endswith('.pkl'):
                    continue
                
                file_path = os.path.join(self._cache_dir, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except Exception as e:
                    print(f"[comfyui-easytoolkit] Warning: Failed to get size of {filename}: {e}")
            
            return total_size
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error calculating cache size: {e}")
            return 0
    
    def _cleanup_old_data(self):
        """Clean up old data when cache size exceeds threshold"""
        try:
            # Calculate current cache size
            current_size = self._calculate_total_cache_size()
            
            # If below normal threshold, no cleanup needed
            if current_size <= self._max_cache_size_bytes:
                return
            
            print(f"[comfyui-easytoolkit] Cache size ({current_size / 1024 / 1024:.2f} MB) exceeds threshold ({self._max_cache_size_bytes / 1024 / 1024:.2f} MB)")
            
            # Get current time
            current_time = time.time()
            
            # Determine if we need forced cleanup (exceeds absolute maximum)
            force_cleanup = current_size > self._absolute_max_cache_size_bytes and self._absolute_max_cache_size_bytes > 0
            
            if force_cleanup:
                print(f"[comfyui-easytoolkit] Cache size exceeds absolute maximum ({self._absolute_max_cache_size_bytes / 1024 / 1024:.2f} MB), forcing cleanup")
            
            # Collect all contexts with their metadata
            all_contexts = []
            old_contexts = []
            
            for key, context in self._data.items():
                last_access = context._last_access_time
                age = current_time - last_access
                
                # Get file size for this context
                file_path = self._get_context_file_path(key)
                try:
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    context_info = (key, last_access, file_size, age)
                    all_contexts.append(context_info)
                    
                    # Also track which are "old" based on threshold
                    if age >= self._old_data_threshold_seconds:
                        old_contexts.append(context_info)
                except Exception as e:
                    print(f"[comfyui-easytoolkit] Warning: Failed to get size for context '{key}': {e}")
            
            # Decide which contexts to clean
            contexts_to_clean = []
            
            if force_cleanup:
                # Forced cleanup: use all contexts, sorted by age (oldest first)
                contexts_to_clean = sorted(all_contexts, key=lambda x: x[1])
                target_size = self._max_cache_size_bytes  # Clean down to normal threshold
                print(f"[comfyui-easytoolkit] Forced cleanup mode: will clean oldest data regardless of age")
            else:
                # Normal cleanup: only clean old data
                if not old_contexts:
                    print(f"[comfyui-easytoolkit] No old data found (threshold: {self._old_data_threshold_seconds / 3600:.1f} hours), skipping cleanup")
                    return
                
                contexts_to_clean = sorted(old_contexts, key=lambda x: x[1])
                target_size = self._max_cache_size_bytes
            
            # Remove contexts until size is below target
            removed_count = 0
            freed_size = 0
            
            for key, last_access, file_size, age in contexts_to_clean:
                # Remove this context
                self.remove_context(key)
                removed_count += 1
                freed_size += file_size
                
                # Check if we're below target now
                new_size = current_size - freed_size
                if new_size <= target_size:
                    break
            
            if removed_count > 0:
                cleanup_type = "forced" if force_cleanup else "old data"
                print(f"[comfyui-easytoolkit] Cleaned up {removed_count} context(s) ({cleanup_type}), freed {freed_size / 1024 / 1024:.2f} MB")
                print(f"[comfyui-easytoolkit] New cache size: {(current_size - freed_size) / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error during cleanup: {e}")
    
    def _save_task(self):
        """Task to run in thread pool for async saves"""
        with self._save_lock:
            self._pending_save = True
            self._needs_another_save = False
        
        success = self._do_save()
        
        # After successful save, check if cleanup is needed
        if success:
            self._cleanup_old_data()
        
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
            success = self._do_save()
            if success:
                self._cleanup_old_data()
            return success
        
        # Asynchronous save
        with self._save_lock:
            if self._pending_save:
                # A save is already in progress, mark that we need another one
                self._needs_another_save = True
            else:
                # Submit a new save task
                self._save_future = self._executor.submit(self._save_task)
    
    def shutdown(self):
        """Shutdown the cache and save all pending data"""
        print("[comfyui-easytoolkit] Shutting down persistent context cache...")
        self._shutdown_flag = True
        
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
