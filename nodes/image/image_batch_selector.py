from ... import register_node

@register_node
class ImageBatchSelector:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
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

    def run(self, images, select):
        n, h, w, c = images.shape
        if select >= n:
            select = n - 1
        return (images[select].reshape(1, h, w, c),)