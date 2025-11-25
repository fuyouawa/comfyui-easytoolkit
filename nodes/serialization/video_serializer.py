import json
import folder_paths
import os
import uuid

from PIL.PngImagePlugin import PngInfo

from ...utils.format import animated_image_formats
from ...utils.video import ffmpeg_combine_video, opencv_combine_video, ffmpeg_path, FFMPEG_FORMAT_MAPPING, OPENCV_FORMAT_MAPPING

from ... import register_node


@register_node(emoji="📦")
class VideoSerializer:
    """
    Video serializer node.

    Serializes image batch to bytes data for video or animated image.
    """
    @classmethod
    def INPUT_TYPES(cls):
        ffmpeg_formats = []
        if ffmpeg_path is not None:
            ffmpeg_formats = ["video/"+x for x in FFMPEG_FORMAT_MAPPING.keys()]
        opencv_formats = ["video/"+x for x in OPENCV_FORMAT_MAPPING.keys()]

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
                "ffmpeg_format": (animated_image_formats + ffmpeg_formats, {
                    "default": ffmpeg_formats[0],
                }),
                "opencv_format": (animated_image_formats + opencv_formats, {
                    "default": opencv_formats[0],
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

    RETURN_TYPES = ("BYTES", "STRING",)
    RETURN_NAMES = ("video_data", "extension",)
    OUTPUT_NODE = True
    CATEGORY = "EasyToolkit/Serialization"
    FUNCTION = "run"

    def run(
        self,
        image_batch,
        frame_rate: int,
        loop_count: int,
        library: str,
        ffmpeg_format: str,
        opencv_format: str,
        pingpong: bool = False,
        save_metadata: bool = False,
        prompt=None,
        extra_pnginfo=None,
    ):
        """
        Serialize image batch to video bytes data.
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

        temp_path = os.path.join(folder_paths.get_temp_directory(), f"{uuid.uuid4().hex}")
        try:
            if library == "ffmpeg":
                result_path, extension = ffmpeg_combine_video(
                    image_batch=image_batch,
                    output_path=temp_path,
                    frame_rate=frame_rate,
                    video_format=ffmpeg_format,
                    pingpong=pingpong,
                    loop_count=loop_count,
                    video_metadata=video_metadata,
                )
            elif library == "opencv":
                result_path, extension = opencv_combine_video(
                    image_batch=image_batch,
                    output_path=temp_path,
                    frame_rate=frame_rate,
                    video_format=opencv_format,
                    pingpong=pingpong,
                    loop_count=loop_count,
                    video_metadata=video_metadata,
                )
            else:
                raise ValueError(f"Unknown library: {library}")
            
            with open(result_path, "rb") as f:
                video_bytes = f.read()
        finally:
            # Clean up temporary file
            if os.path.exists(result_path):
                try:
                    os.remove(result_path)
                except:
                    pass  # Ignore cleanup errors

        return {"result": (video_bytes, extension,)}
