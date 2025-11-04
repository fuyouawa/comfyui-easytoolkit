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
