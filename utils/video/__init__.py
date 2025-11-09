try:
    from .ffmpeg import ffmpeg_path, image_batch_to_video_bytes as ffmpeg_image_batch_to_video_bytes
    ffmpeg_available = ffmpeg_path is not None
except ImportError:
    ffmpeg_available = False
    ffmpeg_path = None
    ffmpeg_image_batch_to_video_bytes = None

try:
    from .opencv import image_batch_to_video_bytes as opencv_image_batch_to_video_bytes, is_opencv_available
    opencv_available = is_opencv_available()
except ImportError:
    opencv_available = False
    opencv_image_batch_to_video_bytes = None
    is_opencv_available = lambda: False