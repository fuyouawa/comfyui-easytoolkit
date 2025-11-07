"""
Cache cleanup operations for managing cache size and removing old data.
"""
import os
import time


class CleanupManager:
    """Handles cache cleanup and size management"""
    
    @staticmethod
    def calculate_total_cache_size(cache_dir: str) -> int:
        """Calculate total size of all cache files in bytes"""
        total_size = 0
        try:
            if not os.path.exists(cache_dir):
                return 0
            
            for filename in os.listdir(cache_dir):
                if not filename.endswith('.pkl'):
                    continue
                
                file_path = os.path.join(cache_dir, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except Exception as e:
                    print(f"[comfyui-easytoolkit] Warning: Failed to get size of {filename}: {e}")
            
            return total_size
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error calculating cache size: {e}")
            return 0
    
    @staticmethod
    def cleanup_old_data(cache_dir: str, contexts_dict: dict, 
                        max_cache_size: int, absolute_max_cache_size: int,
                        old_data_threshold: float, remove_context_callback):
        """Clean up old data when cache size exceeds threshold
        
        Args:
            cache_dir: Cache directory path
            contexts_dict: Dictionary of {key: PersistentContext}
            max_cache_size: Normal maximum cache size in bytes
            absolute_max_cache_size: Absolute maximum cache size in bytes
            old_data_threshold: Age threshold in seconds for considering data "old"
            remove_context_callback: Function to call to remove a context by key
        """
        try:
            # Calculate current cache size
            current_size = CleanupManager.calculate_total_cache_size(cache_dir)
            
            # If below normal threshold, no cleanup needed
            if current_size <= max_cache_size:
                return
            
            print(f"[comfyui-easytoolkit] Cache size ({current_size / 1024 / 1024:.2f} MB) exceeds threshold ({max_cache_size / 1024 / 1024:.2f} MB)")
            
            # Get current time
            current_time = time.time()
            
            # Determine if we need forced cleanup (exceeds absolute maximum)
            force_cleanup = current_size > absolute_max_cache_size and absolute_max_cache_size > 0
            
            if force_cleanup:
                print(f"[comfyui-easytoolkit] Cache size exceeds absolute maximum ({absolute_max_cache_size / 1024 / 1024:.2f} MB), forcing cleanup")
            
            # Collect all contexts with their metadata
            all_contexts = []
            old_contexts = []
            
            for key, context in contexts_dict.items():
                last_access = context._last_access_time
                age = current_time - last_access
                
                # Get file size for this context
                from .storage import StorageManager
                file_path = StorageManager.get_context_file_path(cache_dir, key)
                try:
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    context_info = (key, last_access, file_size, age)
                    all_contexts.append(context_info)
                    
                    # Also track which are "old" based on threshold
                    if age >= old_data_threshold:
                        old_contexts.append(context_info)
                except Exception as e:
                    print(f"[comfyui-easytoolkit] Warning: Failed to get size for context '{key}': {e}")
            
            # Decide which contexts to clean
            contexts_to_clean = []
            
            if force_cleanup:
                # Forced cleanup: use all contexts, sorted by age (oldest first)
                contexts_to_clean = sorted(all_contexts, key=lambda x: x[1])
                target_size = max_cache_size  # Clean down to normal threshold
                print(f"[comfyui-easytoolkit] Forced cleanup mode: will clean oldest data regardless of age")
            else:
                # Normal cleanup: only clean old data
                if not old_contexts:
                    print(f"[comfyui-easytoolkit] No old data found (threshold: {old_data_threshold / 3600:.1f} hours), skipping cleanup")
                    return
                
                contexts_to_clean = sorted(old_contexts, key=lambda x: x[1])
                target_size = max_cache_size
            
            # Remove contexts until size is below target
            removed_count = 0
            freed_size = 0
            
            for key, last_access, file_size, age in contexts_to_clean:
                # Remove this context
                remove_context_callback(key)
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

