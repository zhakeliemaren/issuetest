import json
import base64
from typing import Optional

from fastapi import Security

from src.base.config import TOKEN_KEY
from extras.obfastapi.frame import Controller, User


class APIController(Controller):

    def decode_token(self, token: str) -> Optional[dict]:
        s = ''
        try:
            for _s in token:
                s += chr((ord(_s) - TOKEN_KEY) % 128)
            s = base64.urlsafe_b64decode(s).decode('utf-8')
            return json.loads(s)
        except:
            return None

    def get_user(
        self,
        cookie_key: str = Security(Controller.API_KEY_BUC_COOKIE),
        token: Optional[str] = None,
    ):
        if token:
            user = self.decode_token(token)
            if user:
                user = User(**user)
                if user.emp_id:
                    self._user = user
        if not self._user:
            return super().get_user(cookie_key)
        return self._user

    def user(self):
        user = "robot"
        return user
