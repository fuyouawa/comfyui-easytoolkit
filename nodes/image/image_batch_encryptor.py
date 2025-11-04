import torch
from ... import register_node
from ...utils.image import encrypt_image


@register_node
class ImageBatchEncryptor:
    """
    Image batch processor node
    Provides multiple image batch processing functions: color inversion, XOR encryption/decryption
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
        Main function for processing image batches
        """
        if not enable:
            return (image_batch,)

        # Get batch size
        batch_size = image_batch.shape[0]

        # Create a list to store processed images
        processed_batch = []

        # Iterate through each image in the batch
        for i in range(batch_size):
            # Get single image
            single_image = image_batch[i:i + 1]  # Maintain batch dimension

            # Apply image processing
            processed_image = encrypt_image(single_image, operation)

            # Add to processed batch
            processed_batch.append(processed_image)

        # Concatenate processed batch into a tensor
        result_batch = torch.cat(processed_batch, dim=0)

        return (result_batch,)
