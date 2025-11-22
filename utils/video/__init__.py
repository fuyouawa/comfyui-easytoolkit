try:
    from .ffmpeg import ffmpeg_path, image_batch_to_video_file as ffmpeg_image_batch_to_video_file
    ffmpeg_available = ffmpeg_path is not None
except ImportError:
    ffmpeg_available = False
    ffmpeg_path = None

try:
    from .opencv import image_batch_to_video_file as opencv_image_batch_to_video_file
except ImportError:
    opencv_available = False