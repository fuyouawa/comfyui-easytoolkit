from ... import register_node
from ...utils.image import bytes_list_to_image_batch
from ...utils.serialization import split_bytes_with_headers


@register_node(emoji="📦")
class ImageBatchDeserializer:
    """
    Image batch deserializer node.

    Deserializes merged bytes object with size headers to batch of ComfyUI image tensors and masks.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": ("BYTES",),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT",)
    RETURN_NAMES = ("images", "masks", "count",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"
    OUTPUT_NODE = True

    def run(self, data):
        """
        Deserialize merged bytes with size headers to image batch.
        """
        # Split the merged bytes into individual bytes objects
        bytes_list = split_bytes_with_headers(data)
        count = len(bytes_list)

        # Convert bytes list to image batch
        images, masks = bytes_list_to_image_batch(bytes_list)

        return (images, masks, count,)


