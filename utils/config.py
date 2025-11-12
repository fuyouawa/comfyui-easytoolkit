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

    def set(self, key: str, value):
        """
        Set a value in the override configuration file.

        Args:
            key: Configuration key in dot notation (e.g., "ai_services.deepseek_chat.api_key")
            value: Value to set
        """
        override_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.override.json')

        # Load existing override config
        override_config = {}
        if os.path.exists(override_path):
            try:
                with open(override_path, 'r', encoding='utf-8') as f:
                    override_config = json.load(f)
            except Exception as e:
                print(f"[comfyui-easytoolkit] Warning: Failed to load override file for set operation: {e}")

        # Set the value in override config using dot notation
        keys = key.split('.')
        current_dict = override_config

        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in current_dict:
                current_dict[k] = {}
            current_dict = current_dict[k]

        # Set the final value
        current_dict[keys[-1]] = value

        # Save the updated override config
        try:
            with open(override_path, 'w', encoding='utf-8') as f:
                json.dump(override_config, f, indent=2, ensure_ascii=False)
            print(f"[comfyui-easytoolkit] Set {key} in override configuration")

            # Reload configuration to apply changes
            self.reload()

        except Exception as e:
            print(f"[comfyui-easytoolkit] Error: Failed to save override configuration: {e}")

    def delete(self, key: str):
        """
        Delete a value from the override configuration file.

        If the key doesn't exist in override but exists in base config,
        copy that section from base config and then delete the specific sub-key.

        Args:
            key: Configuration key in dot notation (e.g., "ai_agents.t2v_prompt_expansion")
        """
        override_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.override.json')

        # Load existing override config
        override_config = {}
        if os.path.exists(override_path):
            try:
                with open(override_path, 'r', encoding='utf-8') as f:
                    override_config = json.load(f)
            except Exception as e:
                print(f"[comfyui-easytoolkit] Warning: Failed to load override file for delete operation: {e}")

        keys = key.split('.')

        # Check if the key exists in override config
        def key_exists_in_override(config, key_list):
            current = config
            for k in key_list:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return False
            return True

        if key_exists_in_override(override_config, keys):
            # Key exists in override, delete it
            current_dict = override_config
            for k in keys[:-1]:
                current_dict = current_dict[k]
            del current_dict[keys[-1]]

            # Clean up empty parent dictionaries
            self._clean_empty_dicts(override_config, keys[:-1])

        else:
            # Key doesn't exist in override, check if it exists in base config
            base_value = self.get(key)
            if base_value is not None:
                # Key exists in base config, copy the parent section and delete the specific key
                parent_keys = keys[:-1]
                final_key = keys[-1]

                # Get the parent section from base config
                parent_value = self._get_nested_value(self._config, parent_keys)
                if parent_value is not None and isinstance(parent_value, dict):
                    # Copy the parent section to override
                    current_dict = override_config
                    for k in parent_keys:
                        if k not in current_dict:
                            current_dict[k] = {}
                        current_dict = current_dict[k]

                    # Set the parent section value (copy from base)
                    current_dict.update(parent_value)

                    # Now delete the specific key from the copied section
                    if final_key in current_dict:
                        del current_dict[final_key]

                    # Clean up empty parent dictionaries
                    self._clean_empty_dicts(override_config, parent_keys)
                else:
                    print(f"[comfyui-easytoolkit] Warning: Cannot delete {key} - parent section not found in base config")
                    return
            else:
                print(f"[comfyui-easytoolkit] Warning: Cannot delete {key} - key not found in override or base config")
                return

        # Save the updated override config
        try:
            with open(override_path, 'w', encoding='utf-8') as f:
                json.dump(override_config, f, indent=2, ensure_ascii=False)
            print(f"[comfyui-easytoolkit] Deleted {key} from override configuration")

            # Reload configuration to apply changes
            self.reload()

        except Exception as e:
            print(f"[comfyui-easytoolkit] Error: Failed to save override configuration: {e}")

    def _get_nested_value(self, config_dict, keys):
        """Get nested value from dictionary using key list"""
        current = config_dict
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current

    def _clean_empty_dicts(self, config_dict, keys):
        """Recursively clean up empty dictionaries after deletion"""
        if not keys:
            return

        current_dict = config_dict
        for k in keys[:-1]:
            if isinstance(current_dict, dict) and k in current_dict:
                current_dict = current_dict[k]
            else:
                return

        # Check if the final dictionary is empty
        if isinstance(current_dict, dict) and keys[-1] in current_dict:
            final_dict = current_dict[keys[-1]]
            if isinstance(final_dict, dict) and not final_dict:
                del current_dict[keys[-1]]
                # Recursively clean parent dictionaries
                self._clean_empty_dicts(config_dict, keys[:-1])

# Global config instance
_config = Config()

def get_config():
    """
    Get the global singleton configuration instance.
    """
    return _config

