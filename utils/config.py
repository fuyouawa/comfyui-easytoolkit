import os
import yaml

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
                'timeout': 300.0,
                'check_interval': 60.0,
                'auto_save_interval': 30.0,
                'access_update_interval': 60.0,
                'start_timeout_on_first_access': True
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


# Global config instance
_config = Config()

def get_config():
    """Get the global configuration instance"""
    return _config

