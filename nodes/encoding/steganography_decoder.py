from ... import register_node
from ...utils.encoding import decode_steganography
import zlib


@register_node(emoji="🔐")
class SteganographyDecoder:
    """
    Steganography decoder node.

    Decodes hidden data from a noise-like image where the data
    is embedded in the pixel values using steganography.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steganography_image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("data",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, steganography_image) -> dict:
        """
        Decode hidden data from steganography image with optional decompression.
        """
        # Extract bytes from steganography image
        data_bytes = decode_steganography(steganography_image)

        return {"result": (data_bytes,)}

