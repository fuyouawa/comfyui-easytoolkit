from ... import register_node
from ...utils.image import base64_to_tensor


@register_node
class ImageTensorBase64Decoder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        Define input parameters
        """
        return {
            "required": {
                "base64": ("STRING", {"multiline": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64):
        """
        Decode base64 string to image tensor (raw tensor data)
        
        Args:
            base64: Base64 encoded string of raw tensor data
            
        Returns:
            Image tensor (1, H, W, C)
        """
        image = base64_to_tensor(base64)
        return {"result": (image,)}

