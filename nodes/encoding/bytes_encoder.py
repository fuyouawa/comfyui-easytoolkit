from ... import register_node
from ...utils.encoding import encode_bytes


@register_node(emoji="🔐")
class BytesEncoder:
    """
    Bytes encoder node.

    Encodes bytes data to string representation in specified base.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("BYTES", {
                }),
                "base": (["base64", "binary", "octal", "decimal", "hexadecimal"], {
                    "default": "base64"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("encoded_string",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"

    def run(self, data, base):
        """
        Encode bytes data to string in specified base.
        """
        encoded_string = encode_bytes(data, base)
        return (encoded_string,)