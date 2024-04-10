from sqlalchemy import Column, String, Integer, Boolean, DateTime
from .data_object import DataObject


class ProjectDO(DataObject):
    __tablename__ = 'sync_project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    github = Column(String(50))
    gitee = Column(String(50))
    gitlab = Column(String(50))
    gitlink = Column(String(50))
    code_china = Column(String(50))
    github_token = Column(String(50))
    gitee_token = Column(String(50))
    code_china_token = Column(String(50))
    gitlink_token = Column(String(50))
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class JobDO(DataObject):
    __tablename__ = 'sync_job'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project = Column(String(20))
    status = Column(Boolean)
    type = Column(String(20))
    github_branch = Column(String(50))
    gitee_branch = Column(String(50))
    gitlab_branch = Column(String(50))
    code_china_branch = Column(String(50))
    gitlink_branch = Column(String(50))
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    commit = Column(String(50))
    base = Column(String(20))
