from ... import register_node
import zlib

@register_node(emoji="🧮")
class ZlibDecompressor:
    """
    Bytes decompression node
    Decompress gzip-compressed bytes data
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("BYTES", {}),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("decompressed_bytes",)

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, data):
        """
        Decompress gzip-compressed bytes data.
        """
        decompressed_data = zlib.decompress(data)
        return (decompressed_data,)