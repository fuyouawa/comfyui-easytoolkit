from ... import register_node
from ...utils.encoding import decode_bytes


@register_node(emoji="🔐")
class BytesDecoder:
    """
    Bytes decoder node.

    Decodes string representation back to bytes data from specified base.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "encoded_string": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "base": (["base64", "binary", "octal", "decimal", "hexadecimal"], {
                    "default": "base64"
                }),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("data",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"

    def run(self, encoded_string, base):
        """
        Decode string representation back to bytes data from specified base.
        """
        data = decode_bytes(encoded_string, base)
        return (data,)