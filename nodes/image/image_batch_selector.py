from ... import register_node

@register_node
class ImageBatchSelector:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "select": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Image"

    def run(self, image_batch, select):
        n, h, w, c = image_batch.shape
        if select >= n:
            select = n - 1
        return (image_batch[select].reshape(1, h, w, c),)