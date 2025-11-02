import datetime
import re
import time

def format_filename(template: str) -> str:
    """
    格式化文件名模板

    Args:
        template: 文件名模板，支持以下变量：
            %date:yyyy-MM-dd% - 日期
            %date:hh-mm-ss% - 时间
            %timestamp% - 时间戳
            %random% - 随机数
            %width% - 图像宽度
            %height% - 图像高度
    """

    # 替换日期和时间变量
    now = datetime.datetime.now()

    def format_date(match):
        """将用户友好的日期格式转换为Python strftime格式"""
        user_format = match.group(1)
        # 格式映射：用户友好格式 -> Python strftime格式
        format_mapping = {
            'yyyy': '%Y',  # 四位年份
            'yy': '%y',    # 两位年份
            'MM': '%m',    # 两位月份
            'dd': '%d',    # 两位日期
            'HH': '%H',    # 24小时制小时
            'hh': '%I',    # 12小时制小时
            'mm': '%M',    # 分钟
            'ss': '%S',    # 秒
        }

        # 替换格式代码
        python_format = user_format
        for user_code, python_code in format_mapping.items():
            python_format = python_format.replace(user_code, python_code)

        return now.strftime(python_format)

    # 日期格式
    template = re.sub(
        r'%date:(.*?)%',
        format_date,
        template
    )

    # 时间戳
    template = template.replace('%timestamp%', str(int(time.time())))

    # 随机数
    if '%random%' in template:
        import random
        template = template.replace('%random%', str(random.randint(1000, 9999)))

    return template
