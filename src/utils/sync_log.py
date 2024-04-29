import os
import time
import logging
from datetime import datetime, timezone, timedelta

basedir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

log_path = os.path.join(basedir, 'logs')

if not os.path.exists(log_path):
    os.mkdir(log_path)

api_log_name = os.path.join(
    log_path, f'{time.strftime("%Y-%m-%d")}_api.log')

sync_log_name = os.path.join(
    log_path, f'{time.strftime("%Y-%m-%d")}_sync.log')

# 创建一个时区为UTC+8的timezone对象
utc_plus_8_timezone = timezone(timedelta(hours=8))


class LogType:
    INFO = 'info'
    ERROR = 'ERROR'
    WARNING = 'warning'
    DEBUG = "debug"


# 自定义时间格式函数，不依赖于系统时区
def time_formatter(timestamp):
    # 将时间戳转换为UTC+8时区的时间
    utc_time = datetime.fromtimestamp(timestamp, utc_plus_8_timezone)
    # 将datetime对象转换为time.struct_time
    return utc_time.timetuple()


def sync_log(log_type: str, msg: str, log_name: str, user="robot"):
    name = os.path.join(log_path, log_name)
    # 创建一个输出到控制台的handler，并设置日志级别为INFO
    file_handler = logging.FileHandler(name)
    # console_handler = logging.StreamHandler()
    file_handler.setLevel(logging.INFO)
    # 创建一个格式化器，指定日志格式
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(op_name)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    formatter.converter = time_formatter
    file_handler.setFormatter(formatter)

    # 创建一个logger
    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    # 将handler添加到logger
    logger.addHandler(file_handler)
    user = {'op_name': user}
    if log_type == LogType.INFO:
        logger.info(msg, extra=user)
    elif log_type == LogType.ERROR:
        logger.error(msg, extra=user)
    elif log_type == LogType.WARNING:
        logger.warning(msg, extra=user)
    elif log_type == LogType.DEBUG:
        logger.debug(msg, extra=user)
    else:
        pass
    logger.removeHandler(file_handler)
    return


def api_log(log_type: str, msg: str, user="robot"):
    # 创建一个输出到控制台的handler，并设置日志级别为INFO
    file_handler = logging.FileHandler(api_log_name)
    # console_handler = logging.StreamHandler()
    file_handler.setLevel(logging.INFO)
    # 创建一个格式化器，指定日志格式
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(op_name)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    # 创建一个logger
    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    # 将handler添加到logger
    logger.addHandler(file_handler)
    user = {'op_name': user}
    if log_type == LogType.INFO:
        logger.info(msg, extra=user)
    elif log_type == LogType.ERROR:
        logger.error(msg, extra=user)
    elif log_type == LogType.WARNING:
        logger.warning(msg, extra=user)
    else:
        pass
    logger.removeHandler(file_handler)
    return
