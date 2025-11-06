import os
import yaml

try:
    import folder_paths
except ImportError:
    folder_paths = None
    print("[comfyui-easytoolkit] Warning: Could not import folder_paths from ComfyUI")

class Config:
    """Configuration loader for comfyui-easytoolkit"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.yaml"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        
        # Default configuration
        self._config = {
            'persistent_context': {
                'lazy_initialization': True,
                'auto_save': True,
                'cache_directory': 'temp',
                'cache_filename': 'persistent_context_cache.pkl',
                'max_cache_size_mb': 100,
                'old_data_threshold_hours': 24,
                'absolute_max_cache_size_mb': 200,
                'max_context_size_mb': 50
            },
            'base64_uploader': {
                'max_upload_file_size_mb': 100
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        # Merge loaded config with defaults
                        self._config.update(loaded_config)
                print(f"[comfyui-easytoolkit] Configuration loaded from {config_path}")
            else:
                print(f"[comfyui-easytoolkit] Config file not found, using defaults")
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load config file: {e}")
            print(f"[comfyui-easytoolkit] Using default configuration")
    
    def get(self, key: str, default=None):
        """Get a configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_persistent_context_config(self):
        """Get persistent context configuration"""
        return self._config.get('persistent_context', {})
    
    def get_cache_directory_path(self):
        """Get the full path to the cache directory"""
        if folder_paths is None:
            # Fallback to a local directory if folder_paths is not available
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        
        config = self.get_persistent_context_config()
        cache_dir_type = config.get('cache_directory', 'temp')
        
        # Get the base directory from ComfyUI's folder_paths
        base_dir = None
        if cache_dir_type == 'input':
            base_dir = folder_paths.get_input_directory()
        elif cache_dir_type == 'output':
            base_dir = folder_paths.get_output_directory()
        elif cache_dir_type == 'temp':
            base_dir = folder_paths.get_temp_directory()
        else:
            # Default to temp if invalid value
            base_dir = folder_paths.get_temp_directory()
            print(f"[comfyui-easytoolkit] Warning: Invalid cache_directory '{cache_dir_type}', using 'temp'")
        
        # Create comfyui-easytoolkit subdirectory
        cache_dir = os.path.join(base_dir, 'comfyui-easytoolkit')
        
        # Ensure the directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        return cache_dir
    
    def get_cache_file_path(self):
        """Get the full path to the cache file"""
        config = self.get_persistent_context_config()
        cache_filename = config.get('cache_filename', 'persistent_context_cache.pkl')
        cache_dir = self.get_cache_directory_path()
        return os.path.join(cache_dir, cache_filename)
    
    def get_base64_uploader_config(self):
        """Get base64 uploader configuration"""
        return self._config.get('base64_uploader', {})
    
    def get_max_upload_file_size_mb(self):
        """Get maximum upload file size in MB"""
        config = self.get_base64_uploader_config()
        return config.get('max_upload_file_size_mb', 100)


# Global config instance
_config = Config()

def get_config():
    """Get the global configuration instance"""
    return _config

