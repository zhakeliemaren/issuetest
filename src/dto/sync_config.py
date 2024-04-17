from pydantic import BaseModel, Field, validator
from sqlalchemy.sql.sqltypes import Text


class SyncRepoDTO(BaseModel):
    repo_name: str = Field(..., description="仓库名称")
    enable: bool = Field(..., description="同步状态")
    internal_repo_address: str = Field(..., description="内部仓库地址")
    external_repo_address: str = Field(..., description="外部仓库地址")
    sync_granularity: int = Field(..., description="1 为仓库粒度的同步, 2 为分支粒度的同步")
    sync_direction: int = Field(..., description="1 表示内部仓库同步到外部, 2 表示外部仓库同步到内部")


class SyncBranchDTO(BaseModel):
    enable: bool = Field(..., description="是否启用分支同步")
    internal_branch_name: str = Field(..., description="内部仓库分支名")
    external_branch_name: str = Field(..., description="外部仓库分支名")


class BranchDTO(BaseModel):
    id: int = Field(..., description="分支id")
    enable: bool = Field(..., description="是否启用分支同步")
    internal_branch_name: str = Field(..., description="内部仓库分支名")
    external_branch_name: str = Field(..., description="外部仓库分支名")


class RepoDTO(BaseModel):
    enable: bool = Field(..., description="是否启用同步")
    repo_name: str = Field(..., description="仓库名称")
    internal_repo_address: str = Field(..., description="内部仓库地址")
    external_repo_address: str = Field(..., description="外部仓库地址")
    sync_granularity: str = Field(..., description="1 为仓库粒度的同步, 2 为分支粒度的同步")
    sync_direction: str = Field(..., description="1 表示内部仓库同步到外部, 2 表示外部仓库同步到内部")


class AllRepoDTO(BaseModel):
    id: int = Field(..., description="分支id")
    created_at: str = Field('', description="创建时间")
    enable: bool = Field(..., description="是否启用同步")
    repo_name: str = Field(..., description="仓库名称")
    internal_repo_address: str = Field(..., description="内部仓库地址")
    external_repo_address: str = Field(..., description="外部仓库地址")
    sync_granularity: str = Field(..., description="1 为仓库粒度的同步, 2 为分支粒度的同步")
    sync_direction: str = Field(..., description="1 表示内部仓库同步到外部, 2 表示外部仓库同步到内部")


class GetBranchDTO(BaseModel):
    id: int = Field(..., description="分支id")
    created_at: str = Field('', description="创建时间")
    enable: bool = Field(..., description="是否启用分支同步")
    internal_branch_name: str = Field(..., description="内部仓库分支名")
    external_branch_name: str = Field(..., description="外部仓库分支名")


class LogDTO(BaseModel):
    id: int = Field(..., description="日志id")
    branch_id: int = Field(None, description="分支id")
    repo_name: str = Field(..., description="仓库名称")
    commit_id: str = Field(None, description="commit id")
    sync_direct: str = Field(..., description="同步方向")
    log: str
    # log_history: str
    created_at: str = Field('', description="创建时间")
    update_at: str = Field('', description="更新时间")

    class Config:
        arbitrary_types_allowed = True

# class SyncDTO(BaseModel):
#     repo_name: str = Field(..., description="仓库名称")
#     branch_name: str = Field(..., description="分支名称")
#     sync_direct: str = Field(..., description="1 表示内部仓库同步到外部, 2 表示外部仓库同步到内部")


