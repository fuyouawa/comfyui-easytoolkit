from ... import register_node
from ...utils.image import tensor_batch_to_bytes_list
from ...utils.encoding import b64encode


@register_node
class ImageBatchTensorBase64Encoder:
    """
    Tensor base64 image batch encoder node.

    Encodes batch of ComfyUI image tensors to tensor base64 strings.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        Encode image tensor batch to base64.
        """
        bytes_list = tensor_batch_to_bytes_list(images)
        base64_list = [b64encode(tensor_bytes) for tensor_bytes in bytes_list]
        base64_text = "\n".join(base64_list)
        count = len(base64_list)

        return {"result": (base64_text, count,)}

