from typing import Type, List, Optional, Union

from sqlalchemy.dialects.mysql import insert

from extras.obfastapi.mysql import aiomysql_session, ORMAsyncSession
from src.do.data_object import DataObject
from src.base import config  # 加载配置
from extras.obfastapi.frame import Logger
from sqlalchemy import select, func, text
from datetime import datetime
from typing import Any


class MysqlAO:

    def __init__(self, key: str = config.DB_ENV):
        self._db_key = key
        self.now_time = None
        self.now_time_stamp = 0

    def _async_session(self) -> ORMAsyncSession:
        return aiomysql_session(self._db_key)

    async def _insert_all(self, do: List[DataObject]) -> Optional[List[DataObject]]:
        async with self._async_session() as session:
            async with session.begin():
                try:
                    session.add_all(do)
                    await session.flush()
                    return do
                except:
                    await session.rollback()
                    return None

    async def _insert_one(self, do: DataObject) -> Optional[DataObject]:
        async with self._async_session() as session:
            async with session.begin():
                try:
                    session.add(do)
                    await session.flush()
                    return do
                except Exception as e:
                    await session.rollback()
                    return None

    async def _delete_one(self, clz: Type[DataObject], _id: Union[int, str]) -> Optional[bool]:
        async with self._async_session() as session:
            async with session.begin():
                data = await session.get(clz, _id)
                if data:
                    try:
                        await session.delete(data)
                        return True
                    except:
                        await session.rollback()
                        return None

    async def _count(self, clz: Type[DataObject], cond: Any = None) -> int:
        field = clz.emp_id if hasattr(clz, 'emp_id') else clz.id
        cond = text(cond) if isinstance(cond, str) else cond
        async with self._async_session() as session:
            if cond is not None:
                stmt = select(func.count(field)).where(cond)
            else:
                stmt = select(func.count(field))
            return ((await session.execute(stmt)).scalar_one())

    async def _insert_on_duplicate_key_update(self, clz: Type[DataObject], data: dict, on_duplicate_key_update: list) -> bool:
        update_data = {}
        insert_stmt = insert(clz).values(**data)
        for col in on_duplicate_key_update:
            if col not in data:
                continue
            update_data[col] = getattr(insert_stmt.inserted, col)
        async with self._async_session() as session:
            return (await session.execute(insert_stmt.on_duplicate_key_update(**update_data))).rowcount > 0

    async def get_now_time(self, cache: bool = True) -> datetime:
        if not cache or not self.now_time:
            async with self._async_session() as session:
                async with session.begin():
                    self.now_time = (await session.execute("SELECT now() now")).scalar_one()
        return self.now_time

    async def get_now_time_stamp(self, cache: bool = True) -> int:
        if not cache or not self.now_time_stamp:
            async with self._async_session() as session:
                async with session.begin():
                    self.now_time_stamp = (await session.execute("SELECT unix_timestamp(now()) now")).scalar_one()
        return self.now_time_stamp
