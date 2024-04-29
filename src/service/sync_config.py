import re
from typing import List, Union, Optional, Dict
from .service import Service
from src.utils import base
from datetime import datetime
from src.dao.sync_config import SyncBranchDAO, SyncRepoDAO, LogDAO
from src.dto.sync_config import SyncBranchDTO, SyncRepoDTO, RepoDTO, AllRepoDTO, GetBranchDTO, LogDTO, BranchDTO, ModifyRepoDTO
from src.do.sync_config import SyncDirect, SyncType
from src.base.status_code import Status, SYNCException
from src.utils.sync_log import log_path


class SyncService(Service):
    def __init__(self) -> None:
        self.sync_repo_dao = SyncRepoDAO()
        self.sync_branch_dao = SyncBranchDAO()

    async def same_name_repo(self, repo_name: str) -> bool:
        instances = await self.sync_repo_dao.get(repo_name=repo_name)
        if instances is None:
            return False
        return True

    async def create_repo(self, dto: SyncRepoDTO) -> Optional[RepoDTO]:
        repo = await self.sync_repo_dao.create_repo(dto)
        return repo

    async def check_status(self, repo_name: str, dto: SyncBranchDTO) -> int:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            raise SYNCException(Status.REPO_NOTFOUND)

        stm = {"repo_id": repo.id, "internal_branch_name": dto.internal_branch_name,
               "external_branch_name": dto.external_branch_name}
        branches = await self.sync_branch_dao.get(**stm)
        if repo.sync_granularity == SyncType.all:
            raise SYNCException(Status.GRANULARITY_ERROR)
        if branches is not None:
            raise SYNCException(Status.BRANCH_EXISTS)
        return repo.id

    async def create_branch(self, dto: SyncBranchDTO, repo_id: int) -> Optional[BranchDTO]:
        branch = await self.sync_branch_dao.create_branch(dto, repo_id=repo_id)
        return branch

    async def get_sync_repo(self, page_num: int, page_size: int, create_sort: bool) -> Optional[List[AllRepoDTO]]:
        repos = await self.sync_repo_dao.get_sync_repo(page_number=page_num,
                                                       page_size=page_size, create_sort=create_sort)
        return repos

    async def get_sync_branches(self, repo_id: int, page_num: int,
                                page_size: int, create_sort: bool) -> Optional[List[GetBranchDTO]]:

        branches = await self.sync_branch_dao.get_sync_branch(repo_id=repo_id, page_number=page_num,
                                                              page_size=page_size, create_sort=create_sort)
        return branches

    async def sync_branch(self, repo_id: int, branch_name: str, dire: SyncDirect) -> Optional[List[GetBranchDTO]]:
        branches = await self.sync_branch_dao.get_branch(repo_id=repo_id, branch_name=branch_name, dire=dire)
        return branches

    async def get_repo_id(self, repo_name: str) -> int:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            raise SYNCException(Status.REPO_NOTFOUND)
        if repo.sync_granularity == SyncType.all:
            raise SYNCException(Status.GRANULARITY)
        return repo.id

    async def get_repo(self, repo_name: str):
        instances = await self.sync_repo_dao.get(repo_name=repo_name)
        return instances

    async def get_all_repo(self):
        repos = await self.sync_repo_dao.filter(enable=1)
        return repos

    async def delete_repo(self, repo_name: str) -> SYNCException:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            return SYNCException(Status.REPO_NOTFOUND)
        branches = await self.sync_branch_dao.filter(repo_id=repo.id)
        if len(branches) > 0:
            for branch in branches:
                await self.sync_branch_dao.delete(branch)
        await self.sync_repo_dao.delete(repo)

        return SYNCException(Status.SUCCESS)

    async def delete_branch(self, repo_name: str, branch_name: str) -> SYNCException:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            return SYNCException(Status.REPO_NOTFOUND)
        if repo.sync_granularity == SyncType.all:
            return SYNCException(Status.GRANULARITY_DELETE)

        if repo.sync_direction == SyncDirect.to_outer:
            stm = {"repo_id": repo.id, "internal_branch_name": branch_name}
        else:
            stm = {"repo_id": repo.id, "external_branch_name": branch_name}
        branches = await self.sync_branch_dao.filter(**stm)
        if branches is None:
            return SYNCException(Status.BRANCH_DELETE)

        for branch in branches:
            await self.sync_branch_dao.delete(branch)

        return SYNCException(Status.SUCCESS)

    async def update_repo_addr(self, repo_name: str, dto: ModifyRepoDTO) -> SYNCException:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            return SYNCException(Status.REPO_NOTFOUND)
        update_fields = {}
        if dto.internal_repo_address is not None:
            if not base.check_addr(dto.internal_repo_address):
                return SYNCException(Status.REPO_ADDR_ILLEGAL)
            update_fields['internal_repo_address'] = dto.internal_repo_address
        if dto.external_repo_address is not None:
            if not base.check_addr(dto.external_repo_address):
                return SYNCException(Status.REPO_ADDR_ILLEGAL)
            update_fields['external_repo_address'] = dto.external_repo_address
        if dto.inter_token is not None:
            update_fields['inter_token'] = dto.inter_token
        if dto.exter_token is not None:
            update_fields['exter_token'] = dto.exter_token
        await self.sync_repo_dao.update(repo, **update_fields)
        return SYNCException(Status.SUCCESS)

    async def update_repo(self, repo_name: str, enable: bool) -> SYNCException:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            return SYNCException(Status.REPO_NOTFOUND)
        await self.sync_repo_dao.update(repo, enable=enable)

        return SYNCException(Status.SUCCESS)

    async def update_branch(self, repo_name: str, branch_name: str, enable: bool) -> SYNCException:
        repo = await self.sync_repo_dao.get(repo_name=repo_name)
        if repo is None:
            return SYNCException(Status.REPO_NOTFOUND)

        if repo.sync_direction == SyncDirect.to_outer:
            stm = {"repo_id": repo.id, "internal_branch_name": branch_name}
        else:
            stm = {"repo_id": repo.id, "external_branch_name": branch_name}
        branches = await self.sync_branch_dao.filter(**stm)
        if branches is None:
            return SYNCException(Status.BRANCH_DELETE)
        if repo.enable == 0 and enable:
            await self.sync_repo_dao.update(repo, enable=enable)

        for branch in branches:
            await self.sync_branch_dao.update(branch, enable=enable)

        return SYNCException(Status.SUCCESS)


class LogService(Service):
    def __init__(self) -> None:
        self.sync_log_dao = LogDAO()

    async def insert_repo_log(self, repo_name: str, direct: str):
        addr = f"{log_path}/sync_{repo_name}.log"
        with open(addr, 'r') as fd:
            log_content = fd.read()
        log_history = f"{log_path}/sync_{repo_name}_history.log"
        with open(log_history, 'a') as log_:
            log_.write(log_content)
        # 使用正则表达式匹配所有的日期和时间格式
        timestamps = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', log_content)
        first_time = timestamps[0] if timestamps else datetime.now()
        last_time = timestamps[-1] if timestamps else datetime.now()
        await self.sync_log_dao.insert_sync_repo_log(repo_name=repo_name, direct=direct, log_content=log_content,
                                                     first_time=first_time, last_time=last_time)
        # stm = {"repo_name": repo_name, "branch_id": None, "commit_id": None}
        # log = await self.sync_log_dao.filter(**stm)
        # if len(log) < 1:
        #     await self.sync_log_dao.init_sync_repo_log(repo_name=repo_name, direct=direct, log_content=log_content)
        # else:
        #     await self.sync_log_dao.update_sync_repo_log(repo_name=repo_name, direct=direct, log_content=log_content)

    async def insert_branch_log(self, repo_name: str, direct: str, branch_id: int, commit_id: str):
        addr = f"{log_path}/sync_{repo_name}_{branch_id}.log"
        with open(addr, 'r') as fd:
            log_content = fd.read()
        log_history = f"{log_path}/sync_{repo_name}_{branch_id}_history.log"
        with open(log_history, 'a') as log_:
            log_.write(log_content)
        # 使用正则表达式匹配所有的日期和时间格式
        timestamps = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', log_content)
        first_time = timestamps[0] if timestamps else datetime.now()
        last_time = timestamps[-1] if timestamps else datetime.now()
        await self.sync_log_dao.insert_branch_log(repo_name, direct, branch_id, commit_id,
                                                  log_content, first_time, last_time)
        # stm = {"repo_name": repo_name, "branch_id": branch_id}
        # log = await self.sync_log_dao.filter(**stm)
        # if len(log) < 1:
        #     await self.sync_log_dao.init_branch_log(repo_name, direct, branch_id, commit_id, log_content)
        # else:
        #     await self.sync_log_dao.update_branch_log(repo_name, direct, branch_id, commit_id, log_content)

    async def get_logs(self, repo_name: str, branch_id: int, page_num: int, page_size: int, create_sort: bool) -> Optional[List[LogDTO]]:
        logs = await self.sync_log_dao.get_log(repo_name=repo_name, branch_id=branch_id,
                                               page_number=page_num, page_size=page_size, create_sort=create_sort)
        return logs
