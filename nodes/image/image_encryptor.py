from ... import register_node
from ...utils.image import encrypt_image

@register_node
class ImageEncryptor:
    """
    Image processor node
    Provides multiple image processing functions: color inversion, XOR encryption/decryption
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "operation": (["invert", "xor-16", "xor-32", "xor-64", "xor-128"], {
                    "default": "invert"
                }),
                "enable": ("BOOLEAN", {
                    "default": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"

    def run(self, image, enable, operation):
        """
        Main function for processing images
        """
        if not enable:
            return (image,)

        processed_images = encrypt_image(image, operation)
        return (processed_images,)