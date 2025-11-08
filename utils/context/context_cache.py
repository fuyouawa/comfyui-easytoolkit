"""
Persistent context cache management system.

Provides disk-based caching with automatic cleanup and async save operations.
"""
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from .persistent_context import PersistentContext
from .storage import StorageManager
from .cleanup import CleanupManager
from ..config import get_config


class PersistentContextCache:
    def __init__(self):
        self._data: dict[str, PersistentContext] = {}
        self._last_save_time = time.time()

        # Async save system: single worker thread pool with coordination flags
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="persistent_context_saver")
        self._save_lock = threading.Lock()
        self._pending_save = False      # True when save is in progress
        self._needs_another_save = False  # True if save requested while saving
        self._save_future = None

        # Create cache directory if it doesn't exist
        os.makedirs(self._get_cache_dir(), exist_ok=True)

        # Load existing cache from disk
        self._load()
    
    def _get_cache_dir(self) -> str:
        """Get cache directory from config."""
        return get_config().get_cache_directory_path()

    def _get_auto_save(self) -> bool:
        """Get auto_save setting from config."""
        config = get_config().get_persistent_context_config()
        return config.get('auto_save', False)

    def _get_max_cache_size_bytes(self) -> int:
        """Get max cache size from config."""
        config = get_config().get_persistent_context_config()
        return config.get('max_cache_size_mb', 100) * 1024 * 1024

    def _get_old_data_threshold_seconds(self) -> float:
        """Get old data threshold from config."""
        config = get_config().get_persistent_context_config()
        return config.get('old_data_threshold_hours', 24) * 3600

    def _get_absolute_max_cache_size_bytes(self) -> int:
        """Get absolute max cache size from config."""
        config = get_config().get_persistent_context_config()
        return config.get('absolute_max_cache_size_mb', 200) * 1024 * 1024

    def _get_max_context_size_bytes(self) -> int:
        """Get max context size from config."""
        config = get_config().get_persistent_context_config()
        return config.get('max_context_size_mb', 50) * 1024 * 1024

    def _get_max_key_length(self) -> int:
        """Get max key length from config."""
        config = get_config().get_persistent_context_config()
        return config.get('max_key_length', 256)
    
    def _validate_key(self, key: str):
        """Validate key length and format.

        Raises:
            ValueError: If key is invalid
        """
        if not key:
            raise ValueError("Context key cannot be empty")

        max_key_length = self._get_max_key_length()
        if max_key_length > 0 and len(key) > max_key_length:
            raise ValueError(f"Context key length ({len(key)}) exceeds maximum allowed length ({max_key_length})")

    def get_context(self, key: str) -> PersistentContext:
        """Get context by key, updating access time."""
        self._validate_key(key)
        self.update_context_access_time(key)
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Context with key '{key}' not found")

    def has_context(self, key: str) -> bool:
        """Check if context exists for given key."""
        try:
            self._validate_key(key)
        except ValueError:
            return False
        self.update_context_access_time(key)
        return key in self._data

    def remove_context(self, key: str):
        """Remove context from cache and disk."""
        self._validate_key(key)
        self.update_context_access_time(key)
        if key in self._data:
            del self._data[key]
            StorageManager.delete_context_file(self._get_cache_dir(), key)

    def create_context(self, key: str, value: any) -> PersistentContext:
        """Create new context and optionally trigger auto-save."""
        self._validate_key(key)
        context = PersistentContext(value, key=key, cache=self)
        self._data[key] = context
        if self._get_auto_save():
            self.save()
        return context

    def resolve_contexts_by_value_type(self, value_type: type) -> list[PersistentContext]:
        """Get contexts filtered by value type.

        Args:
            value_type: Type to filter by (e.g., str, int, dict, list)

        Returns:
            List of PersistentContext objects with matching value types
        """
        result = []
        for context in self._data.values():
            if isinstance(context.get_value(), value_type):
                result.append(context)
        return result

    def update_context_access_time(self, key: str):
        """Update access time for context (silently handles invalid keys)."""
        try:
            self._validate_key(key)
        except ValueError:
            return
        if key in self._data:
            self._data[key].update_access_time()

    def _load(self):
        """Load cache from disk."""
        cache_dir = self._get_cache_dir()
        self._data = StorageManager.load_contexts(cache_dir, self)
    
    def _do_save(self):
        """Save only dirty contexts to disk."""
        try:
            saved_count = 0
            removed_count = 0
            skipped_count = 0
            oversized_count = 0

            cache_dir = self._get_cache_dir()
            max_context_size = self._get_max_context_size_bytes()

            for key, context in list(self._data.items()):
                if not context.is_dirty():
                    skipped_count += 1
                    continue

                success, status = StorageManager.save_context(cache_dir, key, context, max_context_size)

                if status == 'saved':
                    saved_count += 1
                elif status == 'removed_empty':
                    removed_count += 1
                    del self._data[key]
                elif status == 'oversized':
                    oversized_count += 1

            self._last_save_time = time.time()

            if saved_count > 0:
                print(f"[comfyui-easytoolkit] Saved {saved_count} context(s) to {cache_dir}")
            if removed_count > 0:
                print(f"[comfyui-easytoolkit] Removed {removed_count} context(s) with empty values")
            if oversized_count > 0:
                print(f"[comfyui-easytoolkit] Skipped {oversized_count} oversized context(s)")

            return True

        except Exception as e:
            print(f"[comfyui-easytoolkit] Error during save operation: {e}")
            return False
    
    def _cleanup_old_data(self):
        """Clean up old data when cache size exceeds threshold."""
        CleanupManager.cleanup_old_data(
            cache_dir=self._get_cache_dir(),
            contexts_dict=self._data,
            max_cache_size=self._get_max_cache_size_bytes(),
            absolute_max_cache_size=self._get_absolute_max_cache_size_bytes(),
            old_data_threshold=self._get_old_data_threshold_seconds(),
            remove_context_callback=self.remove_context
        )

    def _save_task(self):
        """Task for async save operations in thread pool.

        Implements coordination logic: if another save was requested while
        this save was running, immediately start a new save task.
        """
        with self._save_lock:
            self._pending_save = True
            self._needs_another_save = False

        success = self._do_save()

        if success:
            self._cleanup_old_data()

        with self._save_lock:
            self._pending_save = False
            if self._needs_another_save:
                self._save_future = self._executor.submit(self._save_task)
            else:
                self._save_future = None

        return success

    def save(self, force_sync=False):
        """Save cache to disk asynchronously or synchronously.

        Async save coordination:
        - If no save in progress: start new save task
        - If save in progress: mark that another save is needed
        - The save task will check this flag and restart if needed

        Args:
            force_sync: If True, perform synchronous save
        """
        if force_sync:
            success = self._do_save()
            if success:
                self._cleanup_old_data()
            return success

        with self._save_lock:
            if self._pending_save:
                self._needs_another_save = True
            else:
                self._save_future = self._executor.submit(self._save_task)

