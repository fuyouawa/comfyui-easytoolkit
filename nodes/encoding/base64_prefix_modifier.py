from ... import register_node
from ...utils.format import all_resource_formats, data_url_prefixes


@register_node
class Base64PrefixModifier:
    """
    Base64 prefix modifier node.

    Modifies or adds data URL prefix to base64 strings based on format.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        Modify base64 prefix based on format.
        """
        base64_data = self._remove_existing_prefix(base64)
        modified_base64 = self._add_prefix(base64_data, format)

        return (modified_base64,)

    def _remove_existing_prefix(self, base64_str):
        """
        Remove existing data URL prefix.
        """
        for prefix in data_url_prefixes:
            if base64_str.startswith(prefix):
                return base64_str[len(prefix):]

        return base64_str

    def _add_prefix(self, base64_data, format):
        """
        Add data URL prefix.
        """
        prefix = f"data:{format};base64,"
        return prefix + base64_data