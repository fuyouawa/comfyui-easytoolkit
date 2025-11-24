import datetime
import re
import time


def format_filename(template: str) -> str:
    """
    Format filename template with dynamic variables.
    """

    # Replace date and time variables
    now = datetime.datetime.now()

    def format_date(match):
        user_format = match.group(1)
        # Format mapping: user-friendly format -> Python strftime format
        format_mapping = {
            'yyyy': '%Y',  # Four-digit year
            'yy': '%y',  # Two-digit year
            'MM': '%m',  # Two-digit month
            'dd': '%d',  # Two-digit day
            'HH': '%H',  # 24-hour format hour
            'hh': '%I',  # 12-hour format hour
            'mm': '%M',  # Minutes
            'ss': '%S',  # Seconds
        }

        # Replace format codes
        python_format = user_format
        for user_code, python_code in format_mapping.items():
            python_format = python_format.replace(user_code, python_code)

        return now.strftime(python_format)

    # Date format
    template = re.sub(
        r'%date:(.*?)%',
        format_date,
        template
    )

    # Timestamp
    template = template.replace('%timestamp%', str(int(time.time())))

    # Random number
    if '%random%' in template:
        import random
        template = template.replace('%random%', str(random.randint(1000, 9999)))

    return template


def file_extension_to_mime_type(suffix: str) -> str:
    """
    Convert file suffix to corresponding MIME type.
    """
    mapping = {
        # Image formats
        "png": "image/png",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "ico": "image/x-icon",
        "svg": "image/svg+xml",
        "tiff": "image/tiff",
        "tif": "image/tiff",

        # Video formats
        "mp4": "video/mp4",
        "webm": "video/webm",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "mkv": "video/x-matroska",
        "flv": "video/x-flv",
        "m4v": "video/x-m4v",
        "3gp": "video/3gpp",

        # Audio formats
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "m4a": "audio/mp4",
        "wma": "audio/x-ms-wma",

        # Document formats
        "pdf": "application/pdf",
        "txt": "text/plain",
        "html": "text/html",
        "htm": "text/html",
        "css": "text/css",
        "js": "application/javascript",
        "json": "application/json",
        "xml": "application/xml",

        # Archive formats
        "zip": "application/zip",
        "rar": "application/x-rar-compressed",
        "7z": "application/x-7z-compressed",
        "tar": "application/x-tar",
        "gz": "application/gzip",

        # Other formats
        "bin": "application/octet-stream",
        "exe": "application/x-msdownload",
        "msi": "application/x-msdownload",
    }

    return mapping.get(suffix.lower(), "application/octet-stream")

def mime_type_to_file_extension(format: str) -> str:
    """
    Convert MIME type to file suffix.
    """
    mapping = {
        # Image formats
        "image/png": "png",
        "image/jpeg": "jpeg",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/bmp": "bmp",
        "image/x-icon": "ico",
        "image/svg+xml": "svg",
        "image/tiff": "tiff",

        # Video formats
        "video/mp4": "mp4",
        "video/webm": "webm",
        "video/x-msvideo": "avi",
        "video/quicktime": "mov",
        "video/x-matroska": "mkv",
        "video/x-flv": "flv",
        "video/x-m4v": "m4v",
        "video/3gpp": "3gp",

        # Audio formats
        "audio/mpeg": "mp3",
        "audio/wav": "wav",
        "audio/ogg": "ogg",
        "audio/flac": "flac",
        "audio/aac": "aac",
        "audio/mp4": "m4a",
        "audio/x-ms-wma": "wma",

        # Document formats
        "application/pdf": "pdf",
        "text/plain": "txt",
        "text/html": "html",
        "text/css": "css",
        "application/javascript": "js",
        "application/json": "json",
        "application/xml": "xml",

        # Archive formats
        "application/zip": "zip",
        "application/x-rar-compressed": "rar",
        "application/x-7z-compressed": "7z",
        "application/x-tar": "tar",
        "application/gzip": "gz",

        # Other formats
        "application/octet-stream": "bin",
        "application/x-msdownload": "exe",
    }
    return mapping.get(format.lower(), "bin")

# Image format categories
static_image_formats = ["image/png", "image/jpeg", "image/bmp", "image/tiff"]
animated_image_formats = ["image/gif", "image/webp"]
vector_image_formats = ["image/svg+xml"]
icon_formats = ["image/x-icon"]
image_formats = static_image_formats + animated_image_formats + vector_image_formats + icon_formats

# Video format categories
common_video_formats = ["video/mp4", "video/webm"]
other_video_formats = ["video/x-msvideo", "video/quicktime", "video/x-matroska", "video/x-flv", "video/x-m4v", "video/3gpp"]
video_formats = common_video_formats + other_video_formats

# Audio format categories
audio_formats = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/flac", "audio/aac", "audio/mp4", "audio/x-ms-wma"]

# Document format categories
document_formats = ["application/pdf", "text/plain", "text/html", "text/css", "application/javascript", "application/json", "application/xml"]

# Archive format categories
archive_formats = ["application/zip", "application/x-rar-compressed", "application/x-7z-compressed", "application/x-tar", "application/gzip"]

# Executable format categories
executable_formats = ["application/x-msdownload"]

# All supported formats
all_resource_formats = (
    image_formats +
    video_formats +
    audio_formats +
    document_formats +
    archive_formats +
    executable_formats +
    ["application/octet-stream"]
)

# Data URL prefixes for all supported formats
data_url_prefixes = [f"data:{format};base64," for format in all_resource_formats]

# Helper functions
def is_image_format(mime_type: str) -> bool:
    """Check if MIME type is an image format"""
    return mime_type in image_formats

def is_video_format(mime_type: str) -> bool:
    """Check if MIME type is a video format"""
    return mime_type in video_formats

def is_audio_format(mime_type: str) -> bool:
    """Check if MIME type is an audio format"""
    return mime_type in audio_formats

def is_document_format(mime_type: str) -> bool:
    """Check if MIME type is a document format"""
    return mime_type in document_formats

def get_format_category(mime_type: str) -> str:
    """Get category of MIME type"""
    if mime_type in image_formats:
        return "image"
    elif mime_type in video_formats:
        return "video"
    elif mime_type in audio_formats:
        return "audio"
    elif mime_type in document_formats:
        return "document"
    elif mime_type in archive_formats:
        return "archive"
    elif mime_type in executable_formats:
        return "executable"
    else:
        return "other"