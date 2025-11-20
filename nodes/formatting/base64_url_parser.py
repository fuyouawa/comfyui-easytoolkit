from ... import register_node
from ...utils.format import all_resource_formats, data_url_prefixes


@register_node(emoji="🔧")
class Base64UrlParser:
    """
    Base64 prefix parser node.

    Parses data URL prefix from base64 strings to extract format and clean data.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64_url": ("STRING", {
                    "default": ""
                }),
            },
        }

    RETURN_TYPES = ("STRING", all_resource_formats, "STRING")
    RETURN_NAMES = ("base64_url", "format", "base64")
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Formatting"

    def run(self, base64_url):
        """
        Parse base64 prefix to extract format and clean data.
        """
        detected_format = self._detect_format(base64_url)
        clean_base64 = self._remove_prefix(base64_url)

        return (base64_url, detected_format, clean_base64)

    def _detect_format(self, base64_str):
        """
        Detect format from data URL prefix.
        """
        for prefix in data_url_prefixes:
            if base64_str.startswith(prefix):
                # Extract format from prefix: "data:format;base64,"
                format_part = prefix[5:-8]  # Remove "data:" and ";base64,"
                return format_part

        # If no prefix found, return default format
        return "application/octet-stream"

    def _remove_prefix(self, base64_str):
        """
        Remove data URL prefix from base64 string.
        """
        for prefix in data_url_prefixes:
            if base64_str.startswith(prefix):
                return base64_str[len(prefix):]

        # If no prefix found, return original string
        return base64_str