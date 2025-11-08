from ... import register_node
from ...utils.image import base64_to_noise_image


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
    RETURN_NAMES = ("noise_image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64: str, width: int = 0, height: int = 0) -> dict:
        """
        Encode base64 string to noise image.
        
        Args:
            base64: Base64 string to encode
            width: Optional width (0 = auto)
            height: Optional height (0 = auto)
        """
        # Convert 0 to None for auto-calculation
        w = None if width == 0 else width
        h = None if height == 0 else height
        
        noise_image = base64_to_noise_image(base64, w, h)
        return {"result": (noise_image,)}

