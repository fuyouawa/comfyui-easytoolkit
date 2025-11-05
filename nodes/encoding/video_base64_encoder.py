import json
import base64
import folder_paths

from PIL.PngImagePlugin import PngInfo

from ...utils.format import animated_image_formats
from ...utils.video import image_batch_to_video_bytes, ffmpeg_path

from ... import register_node

@register_node
class VideoBase64Encoder:
    @classmethod
    def INPUT_TYPES(s):

        ffmpeg_formats = []
        if ffmpeg_path is not None:
            ffmpeg_formats = ["video/"+x[:-5] for x in folder_paths.get_filename_list("video_formats")]
            
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "frame_rate": (
                    "INT",
                    {"default": 8, "min": 1, "step": 1},
                ),
                "loop_count": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "video_format": (animated_image_formats + ffmpeg_formats,{
                    "default": "image/gif",
                }),
                "pingpong": ("BOOLEAN", {"default": False}),
                "save_metadata": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("base64", "suffix",)
    OUTPUT_NODE = True
    CATEGORY = "EasyToolKit/Video"
    FUNCTION = "run"

    def run(
        self,
        image_batch,
        frame_rate: int,
        loop_count: int,
        video_format="image/gif",
        pingpong=False,
        save_metadata=False,
        prompt=None,
        extra_pnginfo=None,
    ):
        images=image_batch

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

        # Use new generic function to generate video bytes
        video_bytes, ext = image_batch_to_video_bytes(
            image_batch=images,
            frame_rate=frame_rate,
            video_format=video_format,
            pingpong=pingpong,
            loop_count=loop_count,
            video_metadata=video_metadata,
        )

        # Convert video bytes to base64 string
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')

        return {"result":(video_base64,ext,)}
