from typing import List, Optional

from sqlalchemy import select, update, text
from .mysql_ao import MysqlAO
from src.do.sync import ProjectDO, JobDO
from typing import Any
from src.dto.sync import CreateJobItem, CreateProjectItem


class ProjectDAO(MysqlAO):

    _DO_class = ProjectDO

    async def insert_project(self, item: CreateProjectItem) -> Optional[List[ProjectDO]]:
        data = {
            'name': item.name,
            'github': item.github_address,
            'gitee': item.gitee_address,
            'gitlab': item.gitlab_address,
            'code_china': item.code_china_address,
            'gitlink': item.gitlink_address,
            'github_token': item.github_token,
            'gitee_token': item.gitee_token,
            "create_time": await self.get_now_time(),
            "update_time": await self.get_now_time()
        }
        return await self._insert_one(self._DO_class(**data))

    async def fetch(self, cond: Any = None, limit: int = 0, start: int = 0) -> List[ProjectDO]:
        stmt = select(self._DO_class).order_by(
            self._DO_class.update_time.desc())
        if cond is not None:
            stmt = stmt.where(cond)
        if limit:
            stmt = stmt.limit(limit)
        if start:
            stmt = stmt.offset(start)
        async with self._async_session() as session:
            answer = list((await session.execute(stmt)).all())
            return answer

    async def delete_project(self, emp_id: str) -> Optional[bool]:
        return await self._delete_one(self._DO_class, emp_id)

    async def _get_count(self, cond) -> int:
        return await self._count(self._DO_class, cond)


class JobDAO(MysqlAO):

    _DO_class = JobDO

    async def insert_job(self, project, item: CreateJobItem) -> Optional[List[JobDO]]:
        data = {
            'project': project,
            'type': item.type,
            'status': True,
            'github_branch': item.github_branch,
            'gitee_branch': item.gitee_branch,
            'gitlab_branch': item.gitlab_branch,
            'code_china_branch': item.code_china_branch,
            'gitlink_branch': item.gitlink_branch,
            "create_time": await self.get_now_time(),
            "update_time": await self.get_now_time(),
            "commit": 'no_commit',
            "base": item.base
        }
        return await self._insert_one(self._DO_class(**data))

    async def fetch(self, cond: Any = None, limit: int = 0, start: int = 0) -> List[_DO_class]:
        stmt = select(self._DO_class).order_by(
            self._DO_class.update_time.desc())
        if cond is not None:
            stmt = stmt.where(cond)
        if limit:
            stmt = stmt.limit(limit)
        if start:
            stmt = stmt.offset(start)
        async with self._async_session() as session:
            answer = list((await session.execute(stmt)).all())
            return answer

    async def list_all(self) -> List[_DO_class]:
        stmt = select(self._DO_class).order_by(self._DO_class.id.desc())
        async with self._async_session() as session:
            answer = list((await session.execute(stmt)).all())
            return answer

    async def delete_job(self, emp_id: str) -> Optional[bool]:
        return await self._delete_one(self._DO_class, emp_id)

    async def update_status(self, _id: int, _status: bool) -> bool:
        status = False
        if _status:
            status = True
        stmt = update(self._DO_class).where(
            self._DO_class.id == _id).values(status=status)
        async with self._async_session() as session:
            async with session.begin():
                return (await session.execute(stmt)).rowcount > 0

    async def update_commit(self, _id: int, _commit: str) -> bool:
        if _commit:
            stmt = update(self._DO_class).where(
                self._DO_class.id == _id).values(commit=_commit)
            async with self._async_session() as session:
                async with session.begin():
                    return (await session.execute(stmt)).rowcount > 0
