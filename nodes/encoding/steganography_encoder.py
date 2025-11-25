from ... import register_node
from ...utils.encoding import encode_steganography


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
    RETURN_NAMES = ("steganography_image", )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, data, use_alpha: bool = True, top_margin_percent: float = 20.0, bottom_margin_percent: float = 20.0, width: int = 0, height: int = 0) -> dict:
        """
        Encode data into steganography image with optional compression.
        """
        # Convert 0 to None for auto-calculation
        w = None if width == 0 else width
        h = None if height == 0 else height

        steganography_image = encode_steganography(data, w, h, use_alpha, top_margin_percent / 100, bottom_margin_percent / 100)
        return {"result": (steganography_image,)}

