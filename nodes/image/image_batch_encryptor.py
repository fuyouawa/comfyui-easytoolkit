import torch
from ... import register_node
from ...utils.image import encrypt_image


@register_node
class ImageBatchEncryptor:
    """
    Batch image encryption and processing node.
    
    Supports color inversion and XOR encryption/decryption operations.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "operation": (["invert", "xor-16", "xor-32", "xor-64", "xor-128"], {
                    "default": "invert"
                }),
                "enable": ("BOOLEAN", {
                    "default": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_batch",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"

    def run(self, image_batch, operation, enable):
        """
        Process image batch with selected encryption operation.
        """
        if not enable:
            return (image_batch,)

        batch_size = image_batch.shape[0]
        processed_batch = []

        for i in range(batch_size):
            single_image = image_batch[i:i + 1]
            processed_image = encrypt_image(single_image, operation)
            processed_batch.append(processed_image)

        result_batch = torch.cat(processed_batch, dim=0)
        return (result_batch,)
