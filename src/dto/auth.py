from fastapi import Body
from pydantic import BaseModel


class AuthItem(BaseModel):
    type: str = Body(..., description="仓库类型")
    token: str = Body(..., description="账号token")
