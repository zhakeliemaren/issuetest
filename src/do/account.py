from sqlalchemy import Column, String, Integer, DateTime
from .data_object import DataObject


class GithubAccountDO(DataObject):
    __tablename__ = 'github_account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(20))
    nickname = Column(String(20))
    account = Column(String(20))
    email = Column(String(20))
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class GiteeAccountDO(DataObject):
    __tablename__ = 'gitee_account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(20))
    nickname = Column(String(20))
    account = Column(String(20))
    email = Column(String(20))
    create_time = Column(DateTime)
    update_time = Column(DateTime)
