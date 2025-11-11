from ... import register_node

@register_node
class DialogBox:
    """
    A ComfyUI node that displays dialog boxes during workflow execution.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "dialog_type": (["info", "success", "warn", "error", "confirm"], {
                    "default": "info"
                }),
                "message": ("STRING", {
                    "default": "Hello from DialogBox!",
                    "multiline": True
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("message",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Debug"
    OUTPUT_NODE = True

    def run(self, dialog_type, message):
        """
        Display a dialog box and return user response.
        """
        # The actual dialog display is handled by the frontend JavaScript
        # This node triggers the frontend extension and passes the dialog configuration
        return {
            "result": (message,),  # Default empty response, will be updated by frontend
            "ui": {
                "dialogs": [{
                    "type": dialog_type,
                    "message": message
                }]
            }
        }