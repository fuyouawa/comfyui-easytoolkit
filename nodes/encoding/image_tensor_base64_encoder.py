from ... import register_node
from ...utils.image import tensor_to_base64


@register_node
class ImageTensorBase64Encoder:
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
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, image):
        """
        Encode image tensor to base64 string (raw tensor data)
        
        Args:
            image: Image tensor (H, W, C) or (1, H, W, C)
            
        Returns:
            Base64 encoded string of raw tensor data
        """
        b64 = tensor_to_base64(image)
        return {"result": (b64,)}

