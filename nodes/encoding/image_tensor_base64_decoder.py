from ... import register_node
from ...utils.image import bytes_to_tensor
from ...utils.encoding import b64decode


@register_node(emoji="🔐")
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
                "base64": ("STRING", {
                    "default": ""
                }),
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
        tensor_bytes = b64decode(base64)
        image = bytes_to_tensor(tensor_bytes)
        return {"result": (image,)}

