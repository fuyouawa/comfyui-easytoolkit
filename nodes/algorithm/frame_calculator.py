from ... import register_node

@register_node(emoji="🧮")
class FrameCalculator:
    """
    Frame calculation node
    Calculate total frames based on duration, frame rate, and extra frames

    Calculation formula: total_frames = duration * frame_rate + extra_frames
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
                    "step": 1
                }),
                "frame_rate": ("FLOAT", {
                    "default": 16.0,
                    "min": 1.0,
                    "max": 120.0,
                    "step": 1.0
                }),
                "extra_frames": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 1000,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("total_frames",)

    FUNCTION = "run"

    CATEGORY = "EasyToolkit/Algorithm"

    def run(self, duration, frame_rate, extra_frames):
        """
        Calculate total frames based on duration, frame rate, and extra frames.
        """
        total_frames = int(duration * frame_rate + extra_frames)

        return (total_frames,)
