from ... import register_node
from ...utils.type import any_type

@register_node(emoji="🪲")
class ToastBox:
    """
    A ComfyUI node that displays toast notifications during workflow execution.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "anything": (any_type, {}),
                "type": (["info", "success", "warn", "error"], {
                    "default": "info"
                }),
                "mode": (["comfyui", "system"], {
                    "default": "comfyui"
                }),
                "message": ("STRING", {
                    "default": "Hello from ToastBox!",
                    "multiline": True
                }),
                "duration": ("INT", {
                    "default": 3000,
                    "min": 1000,
                    "max": 10000,
                    "step": 500
                }),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("anything",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Debug"
    OUTPUT_NODE = True

    def run(self, anything, type, message, duration=3000, mode="comfyui"):
        """
        Display a toast notification and pass through any input data.
        """
        # This node doesn't modify data, it just triggers a frontend notification
        # The actual toast display is handled by the frontend JavaScript
        # The node execution itself triggers the frontend extension
        return {
            "result": (anything,),
            "ui": {
                "notifications": [{
                    "type": type,
                    "message": message,
                    "duration": duration,
                    "mode": mode
                }]
            }
        }