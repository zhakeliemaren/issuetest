import time
from typing import List, Union, Optional, Dict
from typing import Any
from unicodedata import name

from sqlalchemy.sql.expression import false
from .service import Service
from sqlalchemy import text

from src.utils.logger import logger
from src.dto.pull_request import PullRequest as PullRequestDTO
from src.dao.pull_request import PullRequestDAO
from src.do.pull_request import PullRequestDO
from src.common.repo_factory import RepoFactory, PullRequestFactory
from src.common.github import PullRequest


class PullRequestService(Service):

    def __init__(self) -> None:
        self.pull_request_dao = PullRequestDAO()

    async def fetch_pull_request(self, project: str, search: Optional[str] = None) -> Optional[List[PullRequestDTO]]:
        if search:
            cond = f"project = '{project}' and (title like '%{search}%' or pull_request_id = {search})"
        else:
            cond = f"project = '{project}'"
        all = await self.pull_request_dao.fetch(text(cond))
        if not all:
            return None
        data = []
        for pr in all:
            data.append(self._do_to_dto(pr))
        return data

    async def delete_pull_request(self, id: str) -> Optional[bool]:
        return await self.pull_request_dao.delete_pull_request(id)

    async def count_pull_request(self, project: str, search: Optional[str] = None) -> int:
        if search is not None:
            cond = f"project = '{project}' and (title like '%{search}%' or pull_request_id = {search})"
        else:
            cond = f"project = '{project}'"
        return await self.pull_request_dao._count(PullRequestDO, text(cond))

    async def sync_pull_request(self, project, organization, repo: str) -> int:
        logger.info(f"sync the repo {repo} of {organization}")
        github = RepoFactory.create('Github', project, organization, repo)
        if github is None:
            logger.error(f"create repo object failed")
            return None
        github.fetch_pull_request()
        await github.save_pull_request()

    async def merge_pull_request(self, organization, repo: str, id: int) -> Optional[bool]:
        pull_request = PullRequestFactory.create(
            'Github', organization, repo, id)
        if pull_request is None:
            logger.error(f"create pull request object failed")
            return None
        return pull_request.comment("/merge")

    async def merge_pull_request_code(self, organization, repo: str, id: int) -> Optional[bool]:
        pull_request = PullRequestFactory.create(
            'Github', organization, repo, id)
        if pull_request is None:
            logger.error(f"create pull request object failed")
            return None
        return pull_request._send_merge_request()

    async def approve_pull_request(self, organization, repo: str, id: int) -> Optional[bool]:
        pull_request = PullRequestFactory.create(
            'Github', organization, repo, id)
        if pull_request is None:
            logger.error(f"create pull request object failed")
            return None
        return pull_request.approve()

    async def press_pull_request(self, organization, repo: str, id: int) -> Optional[bool]:
        # TODO
        pull_request = PullRequestFactory.create(
            'Github', organization, repo, id)
        if pull_request is None:
            logger.error(f"create pull request object failed")
            return None
        pass

    async def close_pull_request(self, organization, repo: str, id: int) -> Optional[bool]:
        pull_request = PullRequestFactory.create(
            'Github', organization, repo, id)
        if pull_request is None:
            logger.error(f"create pull request object failed")
            return None
        return pull_request.close()

    async def get_count(self, cond: Any = None) -> int:
        return await self.pull_request_dao._count(PullRequestDO, cond)

    async def judge_pull_request_need_merge(self, project, organization, repo: str, id: int) -> Optional[bool]:
        cond = f"project = '{project}' and pull_request_id = {id}"
        all = await self.pull_request_dao.fetch(text(cond))
        if all is None or len(all) == 0:
            return false
        pull_request = PullRequestFactory.create(
            'Github', organization, repo, id)
        if pull_request is None:
            logger.error(f"create pull request object failed")
            return None
        comment_merge = await pull_request.check_if_merge()

        if not comment_merge:
            return False
        elif not all[0]["PullRequestDO"].inline and comment_merge:
            return True
        else:
            # check if the pull request has new commit
            ans = await self.judge_pull_request_has_newer_commit(project, id, pull_request)
            return ans

    async def judge_pull_request_has_newer_commit(self, project, id, pull_request: PullRequest) -> Optional[bool]:
        cond = f"project = '{project}' and pull_request_id = {id}"
        ans = await self.pull_request_dao.fetch(text(cond))
        if ans is None or len(ans) == 0:
            return false
        else:
            origin_latest_commit = ans[0]["PullRequestDO"].latest_commit
            latest_commit = pull_request.get_latest_commit()
            if origin_latest_commit == latest_commit:
                return True
            else:
                return False

    async def update_latest_commit(self, pull: PullRequestDTO):
        return await self.pull_request_dao.update_latest_commit(pull.project, pull.id, pull.latest_commit)

    async def update_inline_status(self, pull: PullRequestDTO, inline: bool) -> Optional[bool]:
        return await self.pull_request_dao.update_inline_status(pull.project, pull.id, inline)

    def _do_to_dto(self, pr: PullRequestDO) -> PullRequestDTO:
        return PullRequestDTO(
            **{
                'id': pr["PullRequestDO"].pull_request_id,
                'title': pr["PullRequestDO"].title,
                'project': pr["PullRequestDO"].project,
                'type': pr["PullRequestDO"].type,
                'address': pr["PullRequestDO"].address,
                'author': pr["PullRequestDO"].author,
                'email': pr["PullRequestDO"].email,
                'target_branch': pr["PullRequestDO"].target_branch,
                'latest_commit': pr["PullRequestDO"].latest_commit
            }
        )
