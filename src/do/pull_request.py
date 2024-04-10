from typing import Text
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from .data_object import DataObject


class PullRequestDO(DataObject):
    __tablename__ = 'pull_request'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pull_request_id = Column(Integer)
    title = Column(Text)
    project = Column(String(20))
    type = Column(String(20))
    address = Column(String(50))
    author = Column(String(20))
    email = Column(String(50))
    target_branch = Column(String(50))
    inline = Column(Boolean)
    latest_commit = Column(String(50))
    create_time = Column(DateTime)
    update_time = Column(DateTime)
