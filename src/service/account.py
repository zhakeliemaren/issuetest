from itertools import count
from typing import List, Union, Optional, Dict
from typing import Any
from src.utils.logger import logger
from .service import Service
from sqlalchemy import text
from src.dao.account import GithubAccountDAO
from src.dao.account import GiteeAccountDAO
from src.do.account import GithubAccountDO, GiteeAccountDO
from src.dto.account import GithubAccount as GithubAccountDTO
from src.dto.account import GiteeAccount as GiteeAccountDTO
from src.dto.account import CreateAccountItem, UpdateAccountItem
from src.base.error_code import Errors


class GithubAccountService(Service):
    def __init__(self) -> None:
        self.github_account_dao = GithubAccountDAO()

    async def list_github_account(self, search: Optional[str] = None) -> Optional[List[GithubAccountDTO]]:
        if search is not None:
            cond = text(
                f"domain like '%{search}%' or nickname like '%{search}%' or account like '%{search}%' or email like '%{search}%'")
            all = await self.github_account_dao.fetch(cond=cond)
        else:
            all = await self.github_account_dao.fetch()
        data = []
        for account in all:
            data.append(self._do_to_dto(account))
        return data

    async def get_github_account_by_domain(self, domain: str) -> Optional[GithubAccountDTO]:
        if domain == "":
            return None
        cond = text(f"domain = '{domain}'")
        all = await self.github_account_dao.fetch(cond=cond)
        if len(all) == 0:
            return None
        else:
            return self._do_to_dto(all[0])

    async def insert_github_account(self, item: CreateAccountItem) -> Optional[List[GithubAccountDO]]:
        cond = text(f"domain like '%{item.domain}%'")
        all = await self.github_account_dao.fetch(cond=cond)
        if len(all) > 0:
            logger.error(
                f"Can not save the account because there are one Github account about {item.domain}")
            raise Errors.INSERT_FAILD
        return await self.github_account_dao.insert_githubAccount(item.domain, item.nickname, item.account, item.email)

    async def delete_github_account(self, id: int) -> Optional[bool]:
        return await self.github_account_dao.delete_account(id)

    async def update_github_account(self, item: UpdateAccountItem) -> Optional[bool]:
        return await self.github_account_dao.update_account(item)

    async def get_count(self, search: Optional[str] = None) -> int:
        if search is not None:
            cond = text(
                f"domain like '%{search}%' or nickname like '%{search}%' or account like '%{search}%' or email like '%{search}%'")
            return await self.github_account_dao._count(cond)
        else:
            return await self.github_account_dao._count()

    def _do_to_dto(self, account: GithubAccountDO) -> GithubAccountDTO:
        return GithubAccountDTO(
            **{
                'id': account["GithubAccountDO"].id,
                'domain': account["GithubAccountDO"].domain,
                'nickname': account["GithubAccountDO"].nickname,
                'account': account["GithubAccountDO"].account,
                'email': account["GithubAccountDO"].email
            }
        )


class GiteeAccountService(Service):
    def __init__(self) -> None:
        self.gitee_account_dao = GiteeAccountDAO()

    async def list_gitee_account(self) -> Optional[List[GiteeAccountDTO]]:
        all = await self.gitee_account_dao.list_all()
        data = []
        for account in all:
            data.append(self._do_to_dto(account))
        return data

    async def insert_gitee_account(self, item: CreateAccountItem) -> Optional[List[GiteeAccountDO]]:
        return await self.gitee_account_dao.insert_giteeAccount(item.domain, item.nickname, item.account, item.email)

    async def delete_gitee_account(self, domain: str) -> Optional[bool]:
        return await self.gitee_account_dao.delete_account(domain)

    async def update_gitee_account(self, item: UpdateAccountItem) -> Optional[bool]:
        return await self.gitee_account_dao.update_account(item)

    async def get_count(self, cond: Any = None) -> int:
        return await self.gitee_account_dao._count(GiteeAccountDO, cond)

    def _do_to_dto(self, account: GiteeAccountDO) -> GiteeAccountDTO:
        return GiteeAccountDTO(
            **{
                'id': account["GithubAccountDO"].id,
                'domain': account["GiteeAccountDO"].domain,
                'nickname': account["GiteeAccountDO"].nickname,
                'account': account["GiteeAccountDO"].account,
                'email': account["GiteeAccountDO"].email
            }
        )
