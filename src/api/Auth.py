from xmlrpc.client import Boolean
from fastapi import (
    BackgroundTasks,
    Query,
    Depends,
    Security,
    Body
)
from pydantic.main import BaseModel
from src.utils.logger import logger

from extras.obfastapi.frame import Trace, DataList
from extras.obfastapi.frame import OBResponse as Response
from src.router import AUTH as auth
from src.base.code import Code
from src.api.Controller import APIController as Controller
from src.dto.auth import AuthItem
from src.base.error_code import ErrorTemplate, Errors
from src.common.repo import RepoType
from src.service.auth import AuthService


class Auth(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @auth.post("/repo/auth", response_model=Response[Boolean], description='认证账号权限')
    async def auth(
        self,
        item: AuthItem = Body(..., description='账号验证属性')
    ):
        if not item:
            raise ErrorTemplate.ARGUMENT_LACK("请求体")
        if not item.type:
            raise ErrorTemplate.ARGUMENT_LACK("账户类型")
        if not item.token:
            raise ErrorTemplate.ARGUMENT_LACK("账户token")

        service = AuthService()
        ans = service.auth(item)
        if not ans:
            return Response(
                code=Code.SUCCESS,
                data=False,
                msg="账户认证失败"
            )
        return Response(
            code=Code.SUCCESS,
            data=True,
            msg="账户认证成功"
        )
