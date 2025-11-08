from ... import register_node
from ...utils.image import noise_image_to_base64


@register_node
class Base64NoiseDecoder:
    """
    Base64 noise decoder node.

    Decodes base64 string from a noise-like image where the data
    is hidden in the pixel values.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise_image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, noise_image) -> dict:
        """
        Decode base64 string from noise image.
        
        Args:
            noise_image: Image tensor with encoded data
        """
        base64_string = noise_image_to_base64(noise_image)
        return {"result": (base64_string,)}

