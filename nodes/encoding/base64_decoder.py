from ... import register_node
from ...utils.encoding import b64decode



@register_node(emoji="🔐")
class Base64Decoder:
    """
    Base64 decoder node.

    Decodes base64 encoded string back to bytes data.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("data",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"

    def run(self, base64):
        """
        Decode base64 string to bytes data.
        """
        decoded_data = b64decode(base64)
        return (decoded_data,)