from ... import register_node
from ...utils.image import image_batch_to_bytes_list
from ...utils.format import static_image_formats, mime_type_to_file_suffix
from ...utils.serialization import merge_bytes_with_headers


@register_node(emoji="📦")
class ImageBatchSerializer:
    """
    Image batch serializer node.

    Serializes batch of ComfyUI image tensors to a single bytes object with size headers.
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

    RETURN_TYPES = ("BYTES", "INT", "STRING",)
    RETURN_NAMES = ("data", "count", "suffix",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"
    OUTPUT_NODE = True

    def run(self, image_batch, format="image/png"):
        """
        Serialize image batch to a single bytes object with size headers.
        """
        bytes_list = image_batch_to_bytes_list(image_batch, format)
        count = len(bytes_list)
        suffix = mime_type_to_file_suffix(format)

        # Merge bytes_list into a single bytes object with size headers
        data = merge_bytes_with_headers(bytes_list)

        return {"result": (data, count, suffix,)}


