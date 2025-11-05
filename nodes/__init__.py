import folder_paths
import os

folder_paths.folder_names_and_paths["video_formats"] = (
    [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "video_formats"),
    ],
    [".json"]
)

from .algorithm import *
from .image import *
from .misc import *
from .video import *
from .encoding import *