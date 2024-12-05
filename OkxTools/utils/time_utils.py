from datetime import datetime

def timestamp_to_datetime(timestamp):
    """
    将时间戳转换为可读时间。
    """
    return datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
