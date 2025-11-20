# from aiohttp import web
# import os
# import json
# from ... import register_node, register_route
# from ...utils.config import get_config

# @register_node(emoji="⚙️")
# class ConfigManager:
#     """
#     A ComfyUI node for managing configuration storage, export, and import.
#     """

#     def __init__(self):
#         pass

#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "storage_directory": (["input", "output", "temp"], {"default": "input"}),
#             },
#         }

#     RETURN_TYPES = ()
#     RETURN_NAMES = ()
#     FUNCTION = "run"
#     CATEGORY = "EasyToolkit/Config"
#     OUTPUT_NODE = False

#     def run(self, storage_directory):
#         # This node doesn't produce outputs, it manages configuration
#         return ()


# @register_route("/easytoolkit_config/apply_settings", method="POST")
# async def handle_apply_settings(request):
#     """
#     API endpoint to apply configuration settings.
#     """
#     try:
#         data = await request.json()
#         storage_directory = data.get("storage_directory", "input")

#         # Validate storage directory
#         valid_directories = ["input", "output", "temp"]
#         if storage_directory not in valid_directories:
#             return web.json_response({
#                 "success": False,
#                 "error": f"Invalid storage directory: {storage_directory}"
#             }, status=400)

#         # Get config instance and set storage directory
#         config = get_config()
#         config.set("storage_directory", storage_directory)

#         return web.json_response({
#             "success": True,
#             "message": f"Configuration settings applied successfully. Storage directory set to: {storage_directory}",
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)


# @register_route("/easytoolkit_config/export_config", method="GET")
# async def handle_export_config(request):
#     """
#     API endpoint to export current configuration as JSON.
#     """
#     try:
#         config = get_config()
#         config_data = config.get_all()

#         # Remove any sensitive data if needed
#         # config_data.pop('api_keys', None)
#         # config_data.pop('secrets', None)

#         return web.json_response({
#             "success": True,
#             "config": config_data,
#             "message": "Configuration exported successfully"
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)


# @register_route("/easytoolkit_config/import_config", method="POST")
# async def handle_import_config(request):
#     """
#     API endpoint to import configuration from JSON.
#     """
#     try:
#         data = await request.json()
#         config_data = data.get("config", {})

#         if not config_data:
#             return web.json_response({
#                 "success": False,
#                 "error": "No configuration data provided"
#             }, status=400)

#         # Get config instance
#         config = get_config()

#         # Clear existing override configuration
#         override_path = config._get_override_path()
#         if os.path.exists(override_path):
#             os.remove(override_path)

#         # Create new override configuration with imported data
#         override_config = {}

#         # Helper function to set nested values
#         def set_nested_value(config_dict, key_path, value):
#             keys = key_path.split('.')
#             current = config_dict
#             for k in keys[:-1]:
#                 if k not in current:
#                     current[k] = {}
#                 current = current[k]
#             current[keys[-1]] = value

#         # Flatten the config data and set each value
#         def flatten_config(data, prefix=""):
#             for key, value in data.items():
#                 full_key = f"{prefix}.{key}" if prefix else key
#                 if isinstance(value, dict):
#                     flatten_config(value, full_key)
#                 else:
#                     set_nested_value(override_config, full_key, value)

#         flatten_config(config_data)

#         # Save the imported configuration
#         with open(override_path, 'w', encoding='utf-8') as f:
#             json.dump(override_config, f, indent=2, ensure_ascii=False)

#         # Reload configuration to apply changes
#         config.reload()

#         return web.json_response({
#             "success": True,
#             "message": "Configuration imported successfully",
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)


# @register_route("/easytoolkit_config/get_current_settings", method="GET")
# async def handle_get_current_settings(request):
#     """
#     API endpoint to get current configuration settings.
#     """
#     try:
#         config = get_config()
#         storage_directory = config.get('storage_directory', 'input')

#         return web.json_response({
#             "success": True,
#             "storage_directory": storage_directory,
#             "message": "Current settings retrieved successfully"
#         })

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return web.json_response({
#             "success": False,
#             "error": str(e)
#         }, status=500)