from ... import register_node
from ...utils.image import bytes_to_data_image
import zlib


@register_node(emoji="📦")
class DataImageSerializer:
    """
    Data image serializer node.

    Serializes bytes data into a noise-like image where the data
    is hidden in the pixel values.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("BYTES", {
                }),
                "compresslevel": ("INT", {
                    "default": "-1",
                    "min": -1,
                    "max": 9,
                    "step": 1,
                    "display": "number",
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
    RETURN_NAMES = ("noise_image", "compression", )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"
    OUTPUT_NODE = True

    def run(self, data, compresslevel = -1, width: int = 0, height: int = 0, use_alpha: bool = True) -> dict:
        """
        Serialize bytes data to noise image with optional compression.
        """
        # Apply compression if requested
        if compresslevel != 0:
            data = zlib.compress(data, level=compresslevel)

        # Convert 0 to None for auto-calculation
        w = None if width == 0 else width
        h = None if height == 0 else height

        noise_image = bytes_to_data_image(data, w, h, use_alpha)
        return {"result": (noise_image,)}

