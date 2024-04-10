from fastapi import (
    Security
)
from pydantic.main import BaseModel
from src.utils.logger import logger

from extras.obfastapi.frame import Trace, DataList
from extras.obfastapi.frame import OBResponse as Response
from src.router import CE_ROBOT as ce_robot
from src.base.code import Code
from src.api.Controller import APIController as Controller


class Answer(BaseModel):
    answer: str


class OBRobot(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @ce_robot.get("", response_model=Response[Answer], description='Reposyncer')
    async def get_ob_robot(
        self
    ):
        answer = Answer(answer="Hello ob-repository-sychronizer")
        logger.info(f"Hello ob-repository-sychronizer")
        return Response(
            code=Code.SUCCESS,
            data=answer
        )
