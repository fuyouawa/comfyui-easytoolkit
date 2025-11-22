from ... import register_node
from ...utils.encoding import b64encode


@register_node(emoji="🔐")
class Base64Encoder:
    """
    Base64 encoder node.

    Encodes bytes data to base64 encoded string.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("BYTES", {
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"

    def run(self, data):
        """
        Encode bytes data to base64 string.
        """
        encoded_data = b64encode(data)
        return (encoded_data,)