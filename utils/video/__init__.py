try:
    from .ffmpeg import ffmpeg_path, FORMAT_MAPPING as FFMPEG_FORMAT_MAPPING, combine_video as ffmpeg_combine_video, load_video as ffmpeg_load_video
    ffmpeg_available = ffmpeg_path is not None
except ImportError:
    ffmpeg_available = False
    ffmpeg_path = None

try:
    from .opencv import FORMAT_MAPPING as OPENCV_FORMAT_MAPPING, combine_video as opencv_combine_video, load_video as opencv_load_video
    opencv_available = True
except ImportError:
    opencv_available = False

from .common import VideoInfo