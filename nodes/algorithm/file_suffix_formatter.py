from ... import register_node

@register_node
class FileSuffixFormatter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数
        """
        return {
            "required": {
                "suffix": ("STRING", {
                    "default": "png",
                }),
            },
        }
    
    RETURN_TYPES = (["image/png", "image/jpeg", "image/gif", "image/webp", "video/mp4", "video/webm", "text/plain"],)
    RETURN_NAMES = ("format",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, suffix):
        format = None

        if suffix == "png":
            format = "image/png"
        elif suffix == "jpeg":
            format = "image/jpeg"
        elif suffix == "gif":
            format = "image/gif"
        elif suffix == "webp":
            format = "image/webp"
        elif suffix == "mp4":
            format = "video/mp4"
        elif suffix == "webm":
            format = "video/webm"
        elif suffix == "txt":
            format = "text/plain"
        else:
            raise Exception("Unsupported extension: " + suffix)

        return {"result": (format,)}