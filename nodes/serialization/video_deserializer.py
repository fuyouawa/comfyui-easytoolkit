import os
import uuid
import folder_paths

from ...utils.video import ffmpeg_load_video, opencv_load_video
from ... import register_node


@register_node(emoji="📦")
class VideoDeserializer:
    """
    Video deserializer node.

    Deserializes video bytes data to image batch and video information.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_data": ("BYTES", {
                }),
                "mode": (["ffmpeg", "opencv"], {
                    "default": "ffmpeg",
                }),
                "force_rate": ("INT", {
                    "default": 0, "min": 0, "step": 1,
                }),
                "frame_load_cap": ("INT", {
                    "default": 0, "min": 0, "step": 1,
                }),
                "start_time": ("INT", {
                    "default": 0, "min": 0, "step": 1,
                }),
                "select_every_nth": ("INT", {
                    "default": 1, "min": 1, "step": 1,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "EASYTOOLKIT_VIDEOINFO",)
    RETURN_NAMES = ("image_batch", "video_info",)
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Serialization"

    def run(
        self,
        video_data: bytes,
        mode: str,
        force_rate: int = 0,
        frame_load_cap: int = 0,
        start_time: int = 0,
        select_every_nth: int = 1,
    ):
        """
        Deserialize video bytes data to image batch and video information.
        """
        # Create temporary file for video data
        temp_path = os.path.join(folder_paths.get_temp_directory(), f"{uuid.uuid4().hex}")

        try:
            # Write bytes to temporary file
            with open(temp_path, "wb") as f:
                f.write(video_data)

            # Load video based on selected mode
            if mode == "ffmpeg":
                image_batch, video_info = ffmpeg_load_video(
                    video_path=temp_path,
                    force_rate=force_rate,
                    frame_load_cap=frame_load_cap,
                    start_time=start_time,
                    select_every_nth=select_every_nth,
                )
            elif mode == "opencv":
                image_batch, video_info = opencv_load_video(
                    video_path=temp_path,
                    force_rate=force_rate,
                    frame_load_cap=frame_load_cap,
                    start_time=start_time,
                    select_every_nth=select_every_nth,
                )
            else:
                raise ValueError(f"Unknown mode: {mode}")

            return (image_batch, video_info,)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass  # Ignore cleanup errors