import json
import folder_paths

from PIL.PngImagePlugin import PngInfo

from ...utils.format import animated_image_formats
from ...utils.video import ffmpeg_image_batch_to_video_bytes, opencv_image_batch_to_video_bytes, ffmpeg_path
from ...utils.encoding import b64encode

from ... import register_node


@register_node(emoji="🔐")
class VideoBase64Encoder:
    """
    Base64 video encoder node.

    Encodes image batch to base64 encoded video or animated image.
    """
    @classmethod
    def INPUT_TYPES(cls):
        ffmpeg_formats = []
        if ffmpeg_path is not None:
            ffmpeg_formats = ["video/"+x[:-5] for x in folder_paths.get_filename_list("video_formats")]

        return {
            "required": {
                "image_batch": ("IMAGE", {
                }),
                "frame_rate": (
                    "INT",
                    {"default": 8, "min": 1, "step": 1,},
                ),
                "loop_count": ("INT", {
                    "default": 0, "min": 0, "max": 100, "step": 1,
                }),
                "library": (["ffmpeg", "opencv"], {
                    "default": "ffmpeg",
                }),
                "video_format": (animated_image_formats + ffmpeg_formats, {
                    "default": "image/gif",
                }),
                "pingpong": ("BOOLEAN", {
                    "default": False,
                }),
                "save_metadata": ("BOOLEAN", {
                    "default": False,
                }),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("base64", "suffix",)
    OUTPUT_NODE = True
    CATEGORY = "EasyToolkit/Encoding"
    FUNCTION = "run"

    def run(
        self,
        image_batch,
        frame_rate: int,
        loop_count: int,
        library: str = "ffmpeg",
        video_format: str = "image/gif",
        pingpong: bool = False,
        save_metadata: bool = False,
        prompt=None,
        extra_pnginfo=None,
    ):
        """
        Encode image batch to base64 video.
        """
        metadata = PngInfo()
        video_metadata = {}

        if save_metadata:
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
                video_metadata["prompt"] = prompt
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                    video_metadata[x] = extra_pnginfo[x]

        if library == "ffmpeg":
            video_bytes, ext = ffmpeg_image_batch_to_video_bytes(
                image_batch=image_batch,
                frame_rate=frame_rate,
                video_format=video_format,
                pingpong=pingpong,
                loop_count=loop_count,
                video_metadata=video_metadata,
            )
        elif library == "opencv":
            mapping = {
                "image/gif": "image/gif",
                "image/webp": "image/webp",
                "video/av1-webm": "video/webm",
                "video/h264-mp4": "video/mp4",
                "video/h265-mp4": "video/mp4",
                "video/webm": "video/webm",
                "video/mp4": "video/mp4",
            }
            video_bytes, ext = opencv_image_batch_to_video_bytes(
                image_batch=image_batch,
                frame_rate=frame_rate,
                video_format=mapping[video_format],
                pingpong=pingpong,
                loop_count=loop_count,
                video_metadata=video_metadata,
            )
        else:
            raise ValueError(f"Unknown library: {library}")

        video_base64 = b64encode(video_bytes)

        return {"result": (video_base64, ext,)}
