from ... import register_node

from ...utils.video import VideoInfo


@register_node(emoji="🎬")
class VideoInfoParser:
    """
    Video info parser node.

    Parses EASYTOOLKIT_VIDEOINFO object and outputs individual VideoInfo fields.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_info": ("EASYTOOLKIT_VIDEOINFO", {
                }),
            },
        }

    RETURN_TYPES = (
        "FLOAT", "INT", "INT", "INT",
        "FLOAT", "INT", "INT", "INT", "INT",
        "STRING", "STRING", "FLOAT", "FLOAT", "FLOAT", "STRING"
    )
    RETURN_NAMES = (
        "source_fps", "source_frame_count","source_width", "source_height", 
        "loaded_fps", "loaded_frame_count", "loaded_width", "loaded_height", "loaded_channels",
        "generator", "resolution", "aspect_ratio", "total_duration", "estimated_duration", "repr"
    )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Video"

    def run(self, video_info: VideoInfo):
        """
        Parse VideoInfo object and return individual fields.
        """
        return (
            video_info.source_fps,
            video_info.source_frame_count,
            video_info.source_width,
            video_info.source_height,
            video_info.loaded_fps,
            video_info.loaded_frame_count,
            video_info.loaded_width,
            video_info.loaded_height,
            video_info.loaded_channels,
            video_info.generator,
            video_info.resolution,
            video_info.aspect_ratio,
            video_info.total_duration,
            video_info.estimated_duration,
            repr(video_info),
        )


@register_node(emoji="🎬")
class VideoInfoSimpleParser:
    """
    Simple video info parser node.

    Parses EASYTOOLKIT_VIDEOINFO object and outputs only commonly used fields.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_info": ("EASYTOOLKIT_VIDEOINFO", {
                }),
            },
        }

    RETURN_TYPES = (
        "FLOAT", "INT", "INT", "INT"
    )
    RETURN_NAMES = (
        "loaded_fps", "loaded_frame_count", "loaded_width", "loaded_height"
    )
    FUNCTION = "run"
    CATEGORY = "EasyToolkit/Video"

    def run(self, video_info: VideoInfo):
        """
        Parse VideoInfo object and return only commonly used fields.
        """
        return (
            video_info.loaded_fps,
            video_info.loaded_frame_count,
            video_info.loaded_width,
            video_info.loaded_height,
        )