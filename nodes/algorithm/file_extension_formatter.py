from ... import register_node

@register_node
class FileExtensionFormatter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
        """
        return {
            "required": {
                "file_ext": ("STRING", {
                    "default": "png",
                }),
            },
        }
    
    RETURN_TYPES = (["image/png", "image/jpeg", "image/gif", "image/webp", "video/mp4", "video/webm", "text/plain"],)
    RETURN_NAMES = ("format",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, file_ext):
        format = None

        if file_ext == "png":
            format = "image/png"
        elif file_ext == "jpeg":
            format = "image/jpeg"
        elif file_ext == "gif":
            format = "image/gif"
        elif file_ext == "webp":
            format = "image/webp"
        elif file_ext == "mp4":
            format = "video/mp4"
        elif file_ext == "webm":
            format = "video/webm"
        elif file_ext == "txt":
            format = "text/plain"
        else:
            raise Exception("Unsupported extension: " + file_ext)

        return {"result": (format,)}