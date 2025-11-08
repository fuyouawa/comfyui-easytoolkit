from ... import register_node
from ...utils.image import bytes_to_noise_image
from ...utils.compression import compress_bytes, compressions
import base64


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
                "compression": (compressions, {
                    "default": "gzip"
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

    RETURN_TYPES = ("IMAGE", compressions,)
    RETURN_NAMES = ("noise_image", "compression", )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64: str, compression = "none", width: int = 0, height: int = 0) -> dict:
        """
        Encode base64 string to noise image with optional compression.

        Args:
            base64: Base64 string to encode
            compression: Compression algorithm (none, gzip, zlib, bz2, lzma)
            width: Optional width (0 = auto)
            height: Optional height (0 = auto)
        """
        # Convert base64 string to bytes
        data_bytes = base64.encode('utf-8')

        # Apply compression if requested
        if compression != "none":
            data_bytes = compress_bytes(data_bytes, compression)

        # Convert 0 to None for auto-calculation
        w = None if width == 0 else width
        h = None if height == 0 else height

        noise_image = bytes_to_noise_image(data_bytes, w, h)
        return {"result": (noise_image,compression,)}

