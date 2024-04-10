from typing import Text
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from .data_object import DataObject


class LogDO(DataObject):
    __tablename__ = 'sync_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_job_id = Column(Integer)
    log_type = Column(String(50))
    log = Column(String(500))
    create_time = Column(DateTime)
