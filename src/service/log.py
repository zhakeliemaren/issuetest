from typing import List, Union, Optional, Dict
from typing import Any
from fastapi import (
    Body
)

from src.utils.logger import logger
from pydantic.main import BaseModel
from sqlalchemy import text
from .service import Service
from src.dao.log import LogDAO
from src.do.log import LogDO
from src.dto.log import Log as LogDTO


class LogService(Service):
    def __init__(self) -> None:
        self._log_dao = LogDAO()

    async def get_logs_by_job(self, id, page: int = 1, size: int = 10) -> Optional[List[LogDTO]]:
        cond = text(f"sync_job_id = {id}")
        start = (page - 1) * size
        all = await self._log_dao.fetch(cond=cond, start=start, limit=size)
        data = []
        for log in all:
            data.append(self._do_to_dto(log))
        return data

    async def save_logs(self, id, type, msg) -> Optional[LogDTO]:
        return await self._log_dao.insert_log(id, type, msg)

    async def delete_logs(self) -> Optional[bool]:
        return await self._log_dao.delete_log()

    async def count_logs(self, id) -> int:
        cond = text(f"sync_job_id = {id}")
        return await self._log_dao._get_count(cond=cond)

    def _do_to_dto(self, log: LogDO) -> LogDTO:
        return LogDTO(
            **{
                'id': log[LogDO].id,
                'sync_job_id': log[LogDO].sync_job_id,
                'log_type': log[LogDO].log_type,
                'log': log[LogDO].log,
                'create_time': log[LogDO].create_time
            }
        )
