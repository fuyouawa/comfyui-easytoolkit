from ... import register_node
from ...utils.image import tensor_batch_to_base64_list


@register_node
class ImageBatchTensorBase64Encoder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "images": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING", "INT",)
    RETURN_NAMES = ("base64_list", "count",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, images):
        """
        Encode a batch of image tensors to base64 strings (raw tensor data)
        
        Args:
            images: Batch of image tensors (N, H, W, C)
            
        Returns:
            Tuple of (base64_list, count) where:
            - base64_list: Newline-separated base64 strings
            - count: Number of images in the batch
        """
        base64_list = tensor_batch_to_base64_list(images)
        
        # Join with newlines for easy splitting later
        base64_text = "\n".join(base64_list)
        count = len(base64_list)
        
        return {"result": (base64_text, count,)}

