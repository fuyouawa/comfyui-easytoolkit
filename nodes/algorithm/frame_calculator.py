from ... import register_node


@register_node
class FrameCalculator:
    """
    帧数计算节点
    根据持续时间、帧率和附加帧数计算总帧数

    计算公式：总帧数 = 持续时间 * 帧率 + 附加帧数
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "duration": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.0,
                    "max": 1000.0,
                    "step": 1,
                    "display": "number",
                    "lazy": True
                }),
                "frame_rate": ("FLOAT", {
                    "default": 16.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 1.0,
                    "display": "number",
                    "lazy": True
                }),
                "extra_frames": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 1000,
                    "step": 1,
                    "display": "number",
                    "lazy": True
                }),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("total_frames",)

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, duration, frame_rate, extra_frames):
        total_frames = int(duration * frame_rate + extra_frames)

        return (total_frames,)
