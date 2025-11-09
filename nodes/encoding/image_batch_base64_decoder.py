from ... import register_node
from ...utils.image import bytes_list_to_image_batch
from ...utils.encoding import b64decode


@register_node
class ImageBatchBase64Decoder:
    """
    Base64 image batch decoder node.

    Decodes base64 strings to batch of ComfyUI image tensors and masks.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_list": ("STRING",{
                    "multiline": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT",)
    RETURN_NAMES = ("images", "masks", "count",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Encoding"
    OUTPUT_NODE = True

    def run(self, base64_list: str) -> dict:
        """
        Decode base64 strings to image batch.
        """
        base64_strings = [s.strip() for s in base64_list.strip().split("\n") if s.strip()]

        if not base64_strings:
            raise ValueError("No valid base64 strings found in input")

        bytes_list = [b64decode(b64_str) for b64_str in base64_strings]
        images, masks = bytes_list_to_image_batch(bytes_list)
        count = len(base64_strings)

        return {"result": (images, masks, count,)}

