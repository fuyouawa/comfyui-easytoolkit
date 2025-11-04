import datetime
import re
import time


def format_filename(template: str) -> str:
    """
    Format filename template

    Args:
        template: Filename template supporting the following variables:
            %date:yyyy-MM-dd% - Date
            %date:hh-mm-ss% - Time
            %timestamp% - Timestamp
            %random% - Random number
            %width% - Image width
            %height% - Image height
    """

    # Replace date and time variables
    now = datetime.datetime.now()

    def format_date(match):
        """Convert user-friendly date format to Python strftime format"""
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


def format_file_suffix(suffix: str) -> str:
    """
    Format file suffix
    
    Args:
        suffix: File suffix
        
    Returns:
        Formatted file suffix
    """
    mapping = {
        "png": "image/png",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "txt": "text/plain",
    }
    
    return mapping.get(suffix.lower(), "application/octet-stream")

def file_format_to_suffix(format: str) -> str:
    """
    Convert file format to suffix
    
    Args:
        format: File format
        
    Returns:
        Suffix
    """
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpeg",
        "image/gif": "gif",
        "image/webp": "webp",
        "video/mp4": "mp4",
        "video/webm": "webm",
        "text/plain": "txt",
    }
    return mapping.get(format.lower(), "bin")

static_image_formats = ["image/png", "image/jpeg"]
animated_image_formats = ["image/gif", "image/webp"]
image_formats = static_image_formats + animated_image_formats
video_formats = ["video/mp4", "video/webm"]
all_resource_formats = image_formats + video_formats + ["application/octet-stream"]