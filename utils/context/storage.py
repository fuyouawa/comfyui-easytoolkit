"""
Storage operations for persistent contexts: loading, saving, and serialization.
"""
import os
import pickle
import gzip


class StorageManager:
    """Handles file I/O and serialization for persistent contexts"""
    
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
    
    @staticmethod
    def get_context_file_path(cache_dir: str, key: str) -> str:
        """Get the file path for a context key"""
        filename = StorageManager._sanitize_filename(key)
        return os.path.join(cache_dir, filename)
    
    @staticmethod
    def load_contexts(cache_dir: str, cache_instance):
        """Load all contexts from disk
        
        Args:
            cache_dir: Directory containing cache files
            cache_instance: The cache instance to attach to loaded contexts
            
        Returns:
            Dictionary of {key: PersistentContext}
        """
        if not os.path.exists(cache_dir):
            print(f"[comfyui-easytoolkit] No existing cache directory found at {cache_dir}")
            return {}
        
        loaded_data = {}
        loaded_count = 0
        failed_count = 0
        
        try:
            for filename in os.listdir(cache_dir):
                if not filename.endswith('.pkl'):
                    continue
                
                file_path = os.path.join(cache_dir, filename)
                
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
                    context_obj._cache = cache_instance
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
                    
                    loaded_data[key] = context_obj
                    loaded_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    print(f"[comfyui-easytoolkit] Warning: Failed to load context from {filename}: {e}")
                    continue
            
            print(f"[comfyui-easytoolkit] Loaded {loaded_count} context(s) from {cache_dir}")
            if failed_count > 0:
                print(f"[comfyui-easytoolkit] Failed to load {failed_count} context file(s)")
            
            return loaded_data
                
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to scan cache directory: {e}")
            print(f"[comfyui-easytoolkit] Starting with empty cache")
            return {}
    
    @staticmethod
    def save_context(cache_dir: str, key: str, context, max_context_size: int) -> tuple[bool, str]:
        """Save a single context to disk
        
        Args:
            cache_dir: Directory to save cache files
            key: Context key
            context: PersistentContext object to save
            max_context_size: Maximum allowed size in bytes (0 = no limit)
            
        Returns:
            Tuple of (success: bool, status: str)
            status can be: 'saved', 'removed_empty', 'oversized', 'error'
        """
        value = context.get_value()
        
        # Check if value is empty (None, empty string, empty list, empty dict, etc.)
        if value is None or (hasattr(value, '__len__') and len(value) == 0):
            print(f"[comfyui-easytoolkit] Warning: Removing context '{key}' with empty value")
            # Remove file if exists
            file_path = StorageManager.get_context_file_path(cache_dir, key)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            return True, 'removed_empty'
        
        # Save this context to its own file
        file_path = StorageManager.get_context_file_path(cache_dir, key)
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
            if max_context_size > 0 and data_size > max_context_size:
                size_mb = data_size / 1024 / 1024
                limit_mb = max_context_size / 1024 / 1024
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
                return True, 'oversized'
            
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
            return True, 'saved'
            
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error saving context '{key}': {e}")
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            return False, 'error'
    
    @staticmethod
    def delete_context_file(cache_dir: str, key: str) -> bool:
        """Delete a context file from disk
        
        Returns:
            True if file was deleted or didn't exist, False on error
        """
        file_path = StorageManager.get_context_file_path(cache_dir, key)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[comfyui-easytoolkit] Removed context file: {file_path}")
            return True
        except Exception as e:
            print(f"[comfyui-easytoolkit] Error removing context file {file_path}: {e}")
            return False

