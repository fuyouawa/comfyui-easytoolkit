from ... import register_node
from ...utils.image import image_batch_to_base64_list
from ...utils.format import static_image_formats


@register_node
class ImageBatchBase64Encoder:
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
                "format": (static_image_formats, {
                    "default": static_image_formats[0]
                }),
            },
        }

    RETURN_TYPES = ("STRING", "INT", "STRING",)
    RETURN_NAMES = ("base64_list", "count", "suffix",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, images, format="image/png"):
        """
        Encode a batch of images to base64 strings
        
        Args:
            images: Batch of images (N, H, W, C)
            format: Image format
            
        Returns:
            Tuple of (base64_list, count, suffix) where:
            - base64_list: Newline-separated base64 strings
            - count: Number of images in the batch
            - suffix: File extension
        """
        base64_list = image_batch_to_base64_list(images, format)
        
        # Join with newlines for easy splitting later
        base64_text = "\n".join(base64_list)
        count = len(base64_list)
        suffix = format.split("/")[-1]
        
        return {"result": (base64_text, count, suffix,)}

