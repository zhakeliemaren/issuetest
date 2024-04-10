from typing import List, Optional

from sqlalchemy import select, update, text, delete
from .mysql_ao import MysqlAO
from src.do.log import LogDO
from typing import Any


class LogDAO(MysqlAO):

    _DO_class = LogDO

    async def insert_log(self, id, type, msg) -> Optional[List[LogDO]]:
        data = {
            'sync_job_id': id,
            'log_type': type,
            'log': msg,
            "create_time": await self.get_now_time()
        }
        return await self._insert_one(self._DO_class(**data))

    async def fetch(self, cond: Any = None, limit: int = 0, start: int = 0) -> List[LogDO]:
        stmt = select(self._DO_class).order_by(
            self._DO_class.id.desc())
        if cond is not None:
            stmt = stmt.where(cond)
        if limit:
            stmt = stmt.limit(limit)
        if start:
            stmt = stmt.offset(start)
        async with self._async_session() as session:
            answer = list((await session.execute(stmt)).all())
            return answer

    async def delete_log(self, cond: Any = None) -> Optional[bool]:
        stmt = delete(self._DO_class)
        if cond is not None:
            stmt = stmt.where(cond)
        async with self._async_session() as session:
            await session.execute(stmt)
            return

    async def _get_count(self, cond) -> int:
        return await self._count(self._DO_class, cond)
