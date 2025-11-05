from ... import register_node
from ...utils.image import base64_list_to_tensor_batch


@register_node
class ImageBatchTensorBase64Decoder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "base64_list": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT",)
    RETURN_NAMES = ("images", "count",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64_list):
        """
        Decode base64 strings to a batch of image tensors (raw tensor data)
        
        Args:
            base64_list: Newline-separated base64 encoded strings
            
        Returns:
            Tuple of (images, count) where:
            - images: Batch of image tensors (N, H, W, C)
            - count: Number of images in the batch
        """
        # Split by newlines to get individual base64 strings
        base64_array = [line.strip() for line in base64_list.split("\n") if line.strip()]
        
        images = base64_list_to_tensor_batch(base64_array)
        count = images.shape[0] if images.numel() > 0 else 0
        
        return {"result": (images, count,)}

