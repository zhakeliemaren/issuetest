import os
import time
from loguru import logger
from typing import Optional

from src.base import config
from src.service.log import LogService
from src.base.code import LogType

basedir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# print(f"log basedir{basedir}")  # /xxx/python_code/FastAdmin/backend/app
# locate log file
log_path = os.path.join(basedir, 'logs')

if not os.path.exists(log_path):
    os.mkdir(log_path)

log_path_error = os.path.join(
    log_path, f'{time.strftime("%Y-%m-%d")}_error.log')

# log config
logger.add(log_path_error, rotation="12:00", retention="5 days", enqueue=True)


def JOB_LOG(sync_job: str, log_type: str, msg: str, commit: str = None):
    trace = logger.add(f"{log_path}/sync_job_{sync_job}.log")
    if log_type == LogType.INFO:
        logger.info(msg)
    elif log_type == LogType.ERROR:
        logger.error(msg)
    elif log_type == LogType.WARNING:
        logger.warning(msg)
    elif log_type == LogType.DEBUG:
        logger.debug(msg)
    else:
        pass
    logger.remove(trace)
    return

async def Log(type: str, msg: str, sync_job_id: Optional[int] = None):
    # use the function if you want to save git log to database
    if type == LogType.INFO:
        logger.info(msg)
    elif type == LogType.ERROR:
        logger.error(msg)
    elif type == LogType.WARNING:
        logger.warning(msg)
    else:
        return
    if sync_job_id is None:
        return
    if config.LOG_SAVE:
        service = LogService()
        await service.save_logs(sync_job_id, type, msg)
        return
