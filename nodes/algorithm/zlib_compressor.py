from ... import register_node
import zlib

@register_node(emoji="🧮")
class ZlibCompressor:
    """
    Bytes compression node
    Compress bytes data using gzip compression
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("BYTES", {}),
                "compression_level": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 9,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("compressed_bytes",)

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, data, compression_level):
        """
        Compress bytes data using gzip compression.
        """
        compressed_data = zlib.compress(data, level=compression_level)
        return (compressed_data,)