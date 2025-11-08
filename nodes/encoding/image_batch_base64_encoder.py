from ... import register_node
from ...utils.image import image_batch_to_base64_list
from ...utils.format import static_image_formats


@register_node
class ImageBatchBase64Encoder:
    """
    Base64 image batch encoder node.

    Encodes batch of ComfyUI image tensors to base64 strings.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_batch": ("IMAGE",),
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

    def run(self, image_batch, format="image/png"):
        """
        Encode image batch to base64 strings.
        """
        base64_list = image_batch_to_base64_list(image_batch, format)
        base64_text = "\n".join(base64_list)
        count = len(base64_list)
        suffix = format.split("/")[-1]

        return {"result": (base64_text, count, suffix,)}

