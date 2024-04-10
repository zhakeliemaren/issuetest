import os
import time
import logging

basedir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

log_path = os.path.join(basedir, 'logs')

if not os.path.exists(log_path):
    os.mkdir(log_path)

api_log_name = os.path.join(
    log_path, f'{time.strftime("%Y-%m-%d")}_api.log')

sync_log_name = os.path.join(
    log_path, f'{time.strftime("%Y-%m-%d")}_sync.log')


class LogType:
    INFO = 'info'
    ERROR = 'ERROR'
    WARNING = 'warning'
    DEBUG = "debug"


def sync_log(log_type: str, msg: str, log_name: str, user="robot"):
    name = os.path.join(log_path, log_name)
    # 创建一个输出到控制台的handler，并设置日志级别为INFO
    file_handler = logging.FileHandler(name)
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
