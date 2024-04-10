from typing import Union
from pydantic import BaseModel
from pydantic.fields import Field


class UserInfoDto(BaseModel):
    name: str = Field(..., description="用户登录名")
    nick: str = Field(..., description="花名")
    emp_id: Union[int, str] = Field(..., description="工号")
    email: str = Field("", description="用户邮箱")
    dept: str = Field("", description="用户部门")
