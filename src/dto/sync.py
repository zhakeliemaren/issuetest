from fastapi import Body
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class Color(Enum):
    red = 0
    green = 1


class SyncType:
    OneWay = "OneWay"
    TwoWay = "TwoWay"


class Project(BaseModel):
    id: int
    name: str
    github_address: Optional[str]
    gitee_address: Optional[str]
    gitlab_address: Optional[str]
    code_china_address: Optional[str]
    gitlink_address: Optional[str]
    github_token: Optional[str]
    gitee_token: Optional[str]
    code_china_token: Optional[str]
    gitlink_token: Optional[str]


class CreateProjectItem(BaseModel):
    name: str = Body(..., description="合并工程名字")
    github_address: str = Body(None, description="GitHub地址")
    gitlab_address: str = Body(None, description="Gitlab地址")
    gitee_address: str = Body(None, description="Gitee地址")
    code_china_address: str = Body(None, description="CodeChina地址")
    gitlink_address: str = Body(None, description="Gitlink地址")
    github_token: str = Body(None, description="GitHub账户token")
    gitee_token: str = Body(None, description="Gitee账户token")
    code_china_token: str = Body(None, description="CodeChina账户token")
    gitlink_token: str = Body(None, description="Gitlink账户token")


class Job(BaseModel):
    id: int
    project: str
    status: Color
    type: str
    github_branch: Optional[str]
    gitee_branch: Optional[str]
    gitlab_branch: Optional[str]
    code_china_branch: Optional[str]
    gitlink_branch: Optional[str]
    commit: str
    base: Optional[str]
    create_time: datetime
    update_time: datetime


class CreateJobItem(BaseModel):
    github_branch: str = Body(None, description="GitHub分支名")
    gitlab_branch: str = Body(None, description="Gitlab分支名")
    gitee_branch: str = Body(None, description="Gitee分支名")
    code_china_branch: str = Body(None, description="CodeChina分支名")
    gitlink_branch: str = Body(None, description="Gitlink分支名")
    type: str = Body(..., description="分支同步类型")
    base: str = Body(None, description="基础仓库")
