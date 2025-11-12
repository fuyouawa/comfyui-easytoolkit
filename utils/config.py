import os
import yaml
import json

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
        Load configuration from YAML and JSON files and merge them hierarchically.
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(base_dir, 'config.yaml')
        override_path = os.path.join(base_dir, 'config.override.json')
        
        # Default configuration
        self._config = {
        }
        
        # Load base configuration
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        # Deep merge loaded config with defaults
                        self._merge(self._config, loaded_config)
                print(f"[comfyui-easytoolkit] Configuration loaded from {config_path}")
            else:
                print(f"[comfyui-easytoolkit] Config file not found, using defaults")
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load config file: {e}")
            print(f"[comfyui-easytoolkit] Using default configuration")
        
        # Load and merge override configuration (JSON format)
        try:
            if os.path.exists(override_path):
                with open(override_path, 'r', encoding='utf-8') as f:
                    override_config = json.load(f)
                    if override_config:
                        # Deep merge override config (overrides take precedence)
                        self._merge(self._config, override_config)
                print(f"[comfyui-easytoolkit] Override configuration loaded from {override_path}")
        except Exception as e:
            print(f"[comfyui-easytoolkit] Warning: Failed to load override file: {e}")
    
    def _merge(self, base_dict, override_dict):
        """
        Recursively merge two dictionaries, with override values taking precedence.
        """
        for key, value in override_dict.items():
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
    
    def get_all(self):
        """
        Get the entire merged configuration dictionary.
        """
        return self._config.copy()
    
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

