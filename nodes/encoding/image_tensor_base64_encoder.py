from ... import register_node
from ...utils.image import tensor_to_bytes
from ...utils.encoding import b64encode


@register_node
class ImageTensorBase64Encoder:
    """
    Tensor base64 image encoder node.

    Encodes ComfyUI image tensor to tensor base64 string.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        Encode image tensor to base64.
        """
        tensor_bytes = tensor_to_bytes(image)
        b64 = b64encode(tensor_bytes)
        return {"result": (b64,)}

