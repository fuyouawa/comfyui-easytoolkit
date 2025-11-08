import os
import yaml

try:
    import folder_paths
except ImportError:
    folder_paths = None
    print("[comfyui-easytoolkit] Warning: Could not import folder_paths from ComfyUI")

class Config:
    """
    Singleton configuration loader for comfyui-easytoolkit.
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """
        Load configuration from YAML files and merge them hierarchically.
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(base_dir, 'config.yaml')
        override_path = os.path.join(base_dir, 'config.override.yaml')
        
        # Default configuration
        self._config = {
            'persistent_context': {
                'lazy_initialization': True,
                'auto_save': False,
                'cache_directory': 'temp',
                'max_cache_size_mb': 100,
                'old_data_threshold_hours': 24,
                'absolute_max_cache_size_mb': 200,
                'max_context_size_mb': 50,
                'max_key_length': 256
            },
            'base64_uploader': {
                'max_upload_file_size_mb': 100
            }
        }
        
        # Load base configuration
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        # Deep merge loaded config with defaults
                        self._deep_merge(self._config, loaded_config)
                print(f"[comfyui-easytoolkit] Configuration loaded from {config_path}")
            else:
                print(f"[comfyui-easytoolkit] Config file not found, using defaults")
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load config file: {e}")
            print(f"[comfyui-easytoolkit] Using default configuration")
        
        # Load and merge override configuration
        try:
            if os.path.exists(override_path):
                with open(override_path, 'r', encoding='utf-8') as f:
                    override_config = yaml.safe_load(f)
                    if override_config:
                        # Deep merge override config (overrides take precedence)
                        self._deep_merge(self._config, override_config)
                print(f"[comfyui-easytoolkit] Override configuration loaded from {override_path}")
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load override file: {e}")
    
    def _deep_merge(self, base_dict, override_dict):
        """
        Recursively merge two dictionaries, with override values taking precedence.
        """
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._deep_merge(base_dict[key], value)
            else:
                # Override the value
                base_dict[key] = value
    
    def get(self, key: str, default=None):
        """
        Get a configuration value by key with support for dot notation.
        """
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
        """Get the full path to the persistent context cache directory"""
        if folder_paths is None:
            # Fallback to a local directory if folder_paths is not available
            fallback_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache', 'persistent_context')
            os.makedirs(fallback_dir, exist_ok=True)
            return fallback_dir
        
        config = self.get_persistent_context_config()
        cache_dir_type = config.get('cache_directory', 'input')
        
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
        
        # Create comfyui-easytoolkit/persistent_context subdirectory
        cache_dir = os.path.join(base_dir, 'comfyui-easytoolkit', 'persistent_context')
        
        # Ensure the directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        return cache_dir
    
    def get_base64_uploader_config(self):
        """Get base64 uploader configuration"""
        return self._config.get('base64_uploader', {})
    
    def get_max_upload_file_size_mb(self):
        """Get maximum upload file size in MB"""
        config = self.get_base64_uploader_config()
        return config.get('max_upload_file_size_mb', 100)
    
    def reload(self):
        """Reload configuration from disk"""
        print("[comfyui-easytoolkit] Reloading configuration...")
        self._load_config()
        print("[comfyui-easytoolkit] Configuration reloaded successfully")


# Global config instance
_config = Config()

def get_config():
    """
    Get the global singleton configuration instance.
    """
    return _config

