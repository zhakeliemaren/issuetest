from fastapi import (
    Security
)
from pydantic.main import BaseModel
from src.utils.logger import logger

from extras.obfastapi.frame import OBResponse as Response
from src.router import LOG as log
from src.base.code import Code
from src.api.Controller import APIController as Controller
from src.service.log import LogService


class Log(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @log.delete("/log/delete", response_model=Response, description='删除日志')
    async def delete_sync_logs(
        self
    ):
        service = LogService()
        await service.delete_logs()
        return Response(
            code=Code.SUCCESS
        )
