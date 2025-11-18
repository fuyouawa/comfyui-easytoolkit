from ... import register_node
from ...utils.image import bytes_list_to_tensor_batch
from ...utils.encoding import b64decode


@register_node(emoji="🔐")
class ImageBatchTensorBase64Decoder:
    """
    Tensor base64 image batch decoder node.

    Decodes tensor base64 strings to batch of ComfyUI image tensors and masks.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64_batch": ("STRING", {
                    "default": ""
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT",)
    RETURN_NAMES = ("image_batch", "count",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64_batch):
        """
        Decode base64 strings to image tensor batch.
        """
        base64_array = [line.strip() for line in base64_batch.split("\n") if line.strip()]
        bytes_list = [b64decode(b64_str) for b64_str in base64_array]
        image_batch = bytes_list_to_tensor_batch(bytes_list)
        count = image_batch.shape[0] if image_batch.numel() > 0 else 0

        return {"result": (image_batch, count,)}

