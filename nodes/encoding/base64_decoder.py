from ... import register_node
from ...utils.encoding import b64decode
from ...utils.format import format_filename
import os
import folder_paths


@register_node(emoji="🔐")
class Base64Decoder:
    """
    Base64 decoder node.

    Decodes base64 string to byte stream and saves to output directory.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64": ("STRING", {
                    "multiline": True
                }),
                "filename": ("STRING", {
                    "default": "%date:yyyy-MM-dd%_%date:hhmmss%"
                }),
                "suffix": ("STRING", {
                    "default": "bin"
                }),
                "save_output": ("BOOLEAN", {
                    "default": True
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64: str, filename: str, suffix: str, save_output: bool) -> dict:
        """
        Decode base64 to byte stream and save to file.
        """
        # Decode base64 string
        decoded_bytes = b64decode(base64)

        # Format filename
        formatted_filename = format_filename(filename)

        # Ensure suffix doesn't start with dot
        clean_suffix = suffix.lstrip('.')

        # Create full filename
        full_filename = f"{formatted_filename}.{clean_suffix}"

        # Get output directory
        output_dir = folder_paths.get_output_directory()

        # Create full file path
        file_path = os.path.join(output_dir, full_filename)

        if save_output:
            # Write decoded bytes to file
            with open(file_path, 'wb') as f:
                f.write(decoded_bytes)

        return {"result": (file_path,)}