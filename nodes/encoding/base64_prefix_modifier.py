from ... import register_node
from ...utils.format import all_resource_formats, data_url_prefixes


@register_node
class Base64PrefixModifier:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "base64": ("STRING", {
                    "default": "",
                }),
                "format": (all_resource_formats, {
                    "default": all_resource_formats[0]
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"

    def run(self, base64, format):
        """
        Modify or add prefix to base64 string based on format

        Args:
            base64: Input base64 string
            format: Target format (e.g., 'image/png', 'image/jpeg', etc.)

        Returns:
            Modified base64 string with correct prefix
        """
        # Remove any existing prefix
        base64_data = self._remove_existing_prefix(base64)

        # Add new prefix based on format
        modified_base64 = self._add_prefix(base64_data, format)

        return (modified_base64,)

    def _remove_existing_prefix(self, base64_str):
        """
        Remove existing data URL prefix from base64 string
        """
        # Use data_url_prefixes from format.py which contains all supported formats
        for prefix in data_url_prefixes:
            if base64_str.startswith(prefix):
                return base64_str[len(prefix):]

        # If no prefix found, return original string
        return base64_str

    def _add_prefix(self, base64_data, format):
        """
        Add appropriate data URL prefix to base64 data
        """
        # Construct data URL prefix
        prefix = f"data:{format};base64,"
        return prefix + base64_data