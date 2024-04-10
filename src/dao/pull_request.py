from typing import List, Optional

from sqlalchemy import select, update, text
from .mysql_ao import MysqlAO
from src.do.pull_request import PullRequestDO
from typing import Any


class PullRequestDAO(MysqlAO):

    _DO_class = PullRequestDO

    async def insert_pull_request(self, id: int, title, project, repo_type, address, author, email,
                                  target_branch, latest_commit: str) -> Optional[List[PullRequestDO]]:
        data = {
            'pull_request_id': id,
            'project': project,
            'title': title,
            'type': repo_type,
            'address': address,
            'author': author,
            'email': email,
            'target_branch': target_branch,
            'latest_commit': latest_commit,
            'inline': False,
            "create_time": await self.get_now_time(),
            "update_time": await self.get_now_time()
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

    async def delete_pull_request(self, emp_id: str) -> Optional[bool]:
        return await self._delete_one(self._DO_class, emp_id)

    async def update_pull_request(self, id, title, project, repo_type, address, author, email, target_branch: str) -> bool:
        update_time = await self.get_now_time()
        stmt = update(self._DO_class).where(self._DO_class.pull_request_id == id and self._DO_class.project == project).values(
            title=title,
            project=project,
            type=repo_type,
            address=address,
            author=author,
            email=email,
            target_branch=target_branch,
            update_time=update_time
        )
        async with self._async_session() as session:
            return (await session.execute(stmt)).rowcount > 0

    async def update_latest_commit(self, project, id, latest_commit) -> bool:
        update_time = await self.get_now_time()
        stmt = update(self._DO_class).where(self._DO_class.pull_request_id == id and self._DO_class.project == project).values(
            update_time=update_time,
            latest_commit=latest_commit
        )
        async with self._async_session() as session:
            return (await session.execute(stmt)).rowcount > 0

    async def update_inline_status(self, project, id, inline) -> bool:
        update_time = await self.get_now_time()
        stmt = update(self._DO_class).where(
            self._DO_class.pull_request_id == id and self._DO_class.project == project).values(
            inline=inline,
            update_time=update_time)
        async with self._async_session() as session:
            return (await session.execute(stmt)).rowcount > 0
