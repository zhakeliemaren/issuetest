from typing import List, Union, Optional, Dict
from typing import Any
from fastapi import (
    Body
)

from src.utils.logger import logger
from pydantic.main import BaseModel
from sqlalchemy import text
from .service import Service
from src.dto.auth import AuthItem
from src.common.repo import RepoType
from src.utils import github, gitee


class AuthService(Service):
    def __init__(self) -> None:
        pass

    def auth(self, item: AuthItem) -> bool:
        if item.type == RepoType.Github:
            return github.github_auth(item.token)
        elif item.type == RepoType.Gitee:
            return gitee.gitee_auth(item.token)
        else:
            return False
