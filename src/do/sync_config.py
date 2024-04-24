from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, text, Enum, Text
from .data_object import DataObject
import enum


class SyncType(enum.Enum):
    """
    仓库级别同步 -> all -> 1
    分支级别同步 -> one -> 2
    """
    all = 1
    one = 2


class SyncDirect(enum.Enum):
    """
    仓库/分支由内向外同步 -> to_outer -> 1
    仓库/分支由外向内同步 -> to_inter -> 2
    """
    to_outer = 1
    to_inter = 2


class SyncRepoMapping(DataObject):
    __tablename__ = 'sync_repo_mapping'

    id = Column(Integer, primary_key=True)
    repo_name = Column(String(128), unique=True, nullable=False, comment="仓库名称")
    enable = Column(Boolean, default=True, comment="是否启用同步")
    internal_repo_address = Column(String, nullable=False, comment="内部仓库地址")
    inter_token = Column(String, nullable=True, comment="内部仓库token")
    external_repo_address = Column(String, nullable=False, comment="外部仓库地址")
    exter_token = Column(String, nullable=True, comment="外部仓库token")
    sync_granularity = Column(Enum(SyncType), comment="同步类型")
    sync_direction = Column(Enum(SyncDirect), comment="首次同步方向")
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")


class SyncBranchMapping(DataObject):
    __tablename__ = 'sync_branch_mapping'

    id = Column(Integer, primary_key=True)
    enable = Column(Boolean, default=True, comment="是否启用同步")
    repo_id = Column(Integer, nullable=False, comment="关联的仓库id")
    internal_branch_name = Column(String, nullable=False, comment="内部仓库分支名")
    external_branch_name = Column(String, nullable=False, comment="外部仓库分支名")
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")


class LogDO(DataObject):
    __tablename__ = 'repo_sync_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, nullable=True, comment="分支id")
    repo_name = Column(String(128), unique=True, nullable=False, comment="仓库名称")
    commit_id = Column(String(128), nullable=True, comment="commit id")
    sync_direct = Column(Enum(SyncDirect), comment="同步方向")
    log = Column(Text, comment="同步日志")
    # log_history = Column(Text, comment="历史日志")
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    update_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")


