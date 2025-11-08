from ... import register_node
from ...utils.image import base64_to_tensor


@register_node
class ImageTensorBase64Decoder:
    """
    Tensor base64 image decoder node.

    Decodes tensor base64 string to ComfyUI image tensor and mask.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        Decode base64 to image tensor.
        """
        image = base64_to_tensor(base64)
        return {"result": (image,)}

