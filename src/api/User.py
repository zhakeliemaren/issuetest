from fastapi import Security, Depends
from src.dto.user import UserInfoDto
from extras.obfastapi.frame import OBResponse as Response

from src.api.Controller import APIController as Controller
from src.router import USER as user


class User(Controller):
    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token=None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @user.get("/info", response_model=Response[UserInfoDto], description="获得用户信息")
    async def get_user_info(
        self,
        user: Security = Depends(get_user)
    ):
        return Response(
            data=UserInfoDto(
                name=user.name,
                nick=user.nick,
                emp_id=user.emp_id,
                email=user.email,
                dept=user.dept
            )
        )
