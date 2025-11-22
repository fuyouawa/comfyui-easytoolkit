from ... import register_node
from ...utils.encoding import encode_steganography
import zlib


@register_node(emoji="🔐")
class SteganographyEncoder:
    """
    Steganography encoder node.

    Encodes hidden data into a noise-like image where the data
    is embedded in the pixel values using steganography.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("BYTES", {
                }),
                "use_alpha": ("BOOLEAN", {
                    "default": False,
                    "label_on": "RGBA (4 channels)",
                    "label_off": "RGB (3 channels)",
                }),
            },
            "optional": {
                "width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "display": "number",
                }),
                "height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 8192,
                    "step": 1,
                    "display": "number",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("steganography_image", "compression", )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, data, width: int = 0, height: int = 0, use_alpha: bool = True) -> dict:
        """
        Encode data into steganography image with optional compression.
        """
        # Convert 0 to None for auto-calculation
        w = None if width == 0 else width
        h = None if height == 0 else height

        steganography_image = encode_steganography(data, w, h, use_alpha)
        return {"result": (steganography_image,)}

