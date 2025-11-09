from ... import register_node
from ...utils.image import bytes_to_noise_image
from ...utils.encoding import b64decode
import zlib


@register_node
class Base64NoiseEncoder:
    """
    Base64 noise encoder node.

    Encodes base64 string into a noise-like image where the data
    is hidden in the pixel values.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64": ("STRING", {
                    "multiline": True
                }),
                "compresslevel": ("INT", {
                    "default": "-1",
                    "min": -1,
                    "max": 9,
                    "step": 1,
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
    RETURN_NAMES = ("noise_image", "compression", )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64: str, compresslevel = -1, width: int = 0, height: int = 0) -> dict:
        """
        Encode base64 string to noise image with optional compression.
        """
        # Convert base64 string to bytes
        data_bytes = b64decode(base64)

        # Apply compression if requested
        if compresslevel != 0:
            data_bytes = zlib.compress(data_bytes, level=compresslevel)

        # Convert 0 to None for auto-calculation
        w = None if width == 0 else width
        h = None if height == 0 else height

        noise_image = bytes_to_noise_image(data_bytes, w, h)
        return {"result": (noise_image,)}

