from typing import Type, List, Optional

from sqlalchemy import select, update

from src.dto.account import CreateAccountItem, UpdateAccountItem
from .mysql_ao import MysqlAO
from src.do.account import GithubAccountDO, GiteeAccountDO
from typing import Any
from sqlalchemy import select, func, text


class AccountDAO(MysqlAO):

    _DO_class = None

    async def insert_githubAccount(self, domain, nickname, account, email: str) -> Optional[List[GithubAccountDO]]:
        data = {
            'domain': domain,
            'nickname': nickname,
            'account': account,
            'email': email,
            "create_time": await self.get_now_time(),
            "update_time": await self.get_now_time()
        }
        return await self._insert_one(self._DO_class(**data))

    async def insert_giteeAccount(self, domain, nickname, account, email: str) -> Optional[List[GiteeAccountDO]]:
        data = {
            'domain': domain,
            'nickname': nickname,
            'account': account,
            'email': email,
            "create_time": await self.get_now_time(),
            "update_time": await self.get_now_time()
        }
        return await self._insert_one(self._DO_class(**data))

    async def update_account(self, item: UpdateAccountItem) -> bool:
        stmt = update(self._DO_class).where(
            self._DO_class.id == item.id).values(
                domain=item.domain,
                nickname=item.nickname,
                account=item.account,
                email=item.email,
                update_time=await self.get_now_time()
        )
        print(stmt)
        async with self._async_session() as session:
            async with session.begin():
                return (await session.execute(stmt)).rowcount > 0

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

    async def delete_account(self, id: int) -> bool:
        async with self._async_session() as session:
            async with session.begin():
                account = await session.get(self._DO_class, id)
                if account:
                    try:
                        await session.delete(account)
                        return True
                    except:
                        pass
        return False

    async def _count(self, cond: Any = None) -> int:
        cond = text(cond) if isinstance(cond, str) else cond
        async with self._async_session() as session:
            if cond is not None:
                stmt = select(func.count(self._DO_class.domain)).where(cond)
            else:
                stmt = select(func.count(self._DO_class.domain))
            return ((await session.execute(stmt)).scalar_one())


class GithubAccountDAO(AccountDAO):
    _DO_class = GithubAccountDO


class GiteeAccountDAO(AccountDAO):
    _DO_class = GiteeAccountDO
