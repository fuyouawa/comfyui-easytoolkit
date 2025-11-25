from ... import register_node
from ...utils.encoding import decode_steganography


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
                "top_margin_percent": ("FLOAT", {
                    "default": 20.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 1.0,
                    "display": "number",
                }),
                "bottom_margin_percent": ("FLOAT", {
                    "default": 20.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 1.0,
                    "display": "number",
                }),
            },
        }

    RETURN_TYPES = ("BYTES",)
    RETURN_NAMES = ("data",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, steganography_image, top_margin_percent: float = 20.0, bottom_margin_percent: float = 20.0) -> dict:
        """
        Decode hidden data from steganography image with optional decompression.
        """
        # Extract bytes from steganography image
        data_bytes = decode_steganography(steganography_image, top_margin_percent / 100, bottom_margin_percent / 100)

        return {"result": (data_bytes,)}

