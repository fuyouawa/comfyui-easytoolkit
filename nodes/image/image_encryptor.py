from ... import register_node
from ...utils.image import encrypt_image

@register_node
class ImageEncryptor:
    """
    Single image encryption and processing node.
    
    Supports color inversion and XOR encryption/decryption operations.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        Process single image with selected encryption operation.
        """
        if not enable:
            return (image,)

        processed_images = encrypt_image(image, operation)
        return (processed_images,)