from ... import register_node
from ...utils.image import base64_list_to_image_batch


@register_node
class ImageBatchBase64Decoder:
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

    RETURN_TYPES = ("IMAGE", "MASK", "INT",)
    RETURN_NAMES = ("images", "masks", "count",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64_list):
        """
        Decode base64 strings to a batch of images
        
        Args:
            base64_list: Newline-separated base64 strings
            
        Returns:
            Tuple of (images, masks, count) where:
            - images: Batch of images (N, H, W, C)
            - masks: Batch of masks (N, H, W)
            - count: Number of images decoded
        """
        # Split by newlines and filter empty lines
        base64_strings = [s.strip() for s in base64_list.strip().split("\n") if s.strip()]
        
        images, masks = base64_list_to_image_batch(base64_strings)
        count = len(base64_strings)
        
        return {"result": (images, masks, count,)}

