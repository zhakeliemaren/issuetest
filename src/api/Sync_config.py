import time

from fastapi import (
    Body,
    Path,
    Depends,
    Query,
    Security
)
from typing import Dict
from starlette.requests import Request
from src.utils import base
from src.utils.sync_log import sync_log, LogType, api_log
from src.api.Controller import APIController as Controller
from src.router import SYNC_CONFIG as router
from src.do.sync_config import SyncDirect
from src.dto.sync_config import SyncRepoDTO, SyncBranchDTO, LogDTO, ModifyRepoDTO
from src.service.sync_config import SyncService, LogService
from src.service.cronjob import sync_repo_task, sync_branch_task
from src.base.status_code import Status, SYNCResponse, SYNCException
from src.service.cronjob import GITMSGException


class SyncDirection(Controller):

    def __init__(self, *args, **kwargs):
        self.service = SyncService()
        self.log_service = LogService()
        super().__init__(*args, **kwargs)

    # 提供获取操作人员信息定义接口, 无任何实质性操作
    def user(self):
        return super().user()

    @router.post("/repo", response_model=SYNCResponse, description='配置同步仓库')
    async def create_sync_repo(
            self, request: Request, user: str = Depends(user),
            dto: SyncRepoDTO = Body(..., description="绑定同步仓库信息")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 POST 方法访问接口 {request.url.path} ", user)
        if not base.check_addr(dto.external_repo_address) or not base.check_addr(dto.internal_repo_address):
            return SYNCResponse(
                code_status=Status.REPO_ADDR_ILLEGAL.code,
                msg=Status.REPO_ADDR_ILLEGAL.msg
            )

        if dto.sync_granularity not in [1, 2]:
            return SYNCResponse(code_status=Status.SYNC_GRAN_ILLEGAL.code, msg=Status.SYNC_GRAN_ILLEGAL.msg)

        if dto.sync_direction not in [1, 2]:
            return SYNCResponse(code_status=Status.SYNC_DIRE_ILLEGAL.code, msg=Status.SYNC_DIRE_ILLEGAL.msg)

        if await self.service.same_name_repo(repo_name=dto.repo_name):
            return SYNCResponse(
                code_status=Status.REPO_EXISTS.code,
                msg=Status.REPO_EXISTS.msg
            )

        repo = await self.service.create_repo(dto)
        return SYNCResponse(
            code_status=Status.SUCCESS.code,
            data=repo,
            msg=Status.SUCCESS.msg
        )

    @router.post("/{repo_name}/branch", response_model=SYNCResponse, description='配置同步分支')
    async def create_sync_branch(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            dto: SyncBranchDTO = Body(..., description="绑定同步分支信息")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 POST 方法访问接口 {request.url.path} ", user)
        try:
            repo_id = await self.service.check_status(repo_name, dto)
        except SYNCException as Error:
            return SYNCResponse(
                code_status=Error.code_status,
                msg=Error.status_msg
            )

        branch = await self.service.create_branch(dto, repo_id=repo_id)
        return SYNCResponse(
            code_status=Status.SUCCESS.code,
            data=branch,
            msg=Status.SUCCESS.msg
        )

    @router.get("/repo", response_model=SYNCResponse, description='获取同步仓库信息')
    async def get_sync_repos(
            self, request: Request, user: str = Depends(user),
            page_num: int = Query(1, description="页数"), page_size: int = Query(10, description="条数"),
            create_sort: bool = Query(False, description="创建时间排序， 默认倒序")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 GET 方法访问接口 {request.url.path} ", user)
        repos = await self.service.get_sync_repo(page_num=page_num, page_size=page_size, create_sort=create_sort)
        if repos is None:
            return SYNCResponse(
                code_status=Status.NOT_DATA.code,
                msg=Status.NOT_DATA.msg
            )
        return SYNCResponse(
            code_status=Status.SUCCESS.code,
            data=repos,
            msg=Status.SUCCESS.msg
        )

    @router.get("/{repo_name}/branch", response_model=SYNCResponse, description='获取仓库对应的同步分支信息')
    async def get_sync_branches(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="查询的仓库名称"),
            page_num: int = Query(1, description="页数"), page_size: int = Query(10, description="条数"),
            create_sort: bool = Query(False, description="创建时间排序， 默认倒序")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 GET 方法访问接口 {request.url.path} ", user)
        try:
            repo_id = await self.service.get_repo_id(repo_name=repo_name)
        except SYNCException as Error:
            return SYNCResponse(
                code_status=Error.code_status,
                msg=Error.status_msg
            )

        branches = await self.service.get_sync_branches(repo_id=repo_id, page_num=page_num,
                                                        page_size=page_size, create_sort=create_sort)
        if len(branches) < 1:
            return SYNCResponse(
                code_status=Status.NOT_DATA.code,
                msg=Status.NOT_DATA.msg
            )

        return SYNCResponse(
            code_status=Status.SUCCESS.code,
            data=branches,
            msg=Status.SUCCESS.msg
        )

    @router.post("/repo/{repo_name}", response_model=SYNCResponse, description='执行仓库同步')
    async def sync_repo(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 POST 方法访问接口 {request.url.path} ", user)
        repo = await self.service.get_repo(repo_name=repo_name)
        if repo is None:
            return SYNCResponse(code_status=Status.REPO_NOTFOUND.code, msg=Status.REPO_NOTFOUND.msg)
        if not repo.enable:
            return SYNCResponse(code_status=Status.NOT_ENABLE.code, msg=Status.NOT_ENABLE.msg)

        try:
            await sync_repo_task(repo, user)
        except GITMSGException as GITError:
            return SYNCResponse(
                code_status=GITError.status,
                msg=GITError.msg
            )

        return SYNCResponse(
            code_status=Status.SUCCESS.code,
            msg=Status.SUCCESS.msg
        )

    @router.post("/{repo_name}/branch/{branch_name}", response_model=SYNCResponse, description='执行分支同步')
    async def sync_branch(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            branch_name: str = Path(..., description="分支名称"),
            sync_direct: int = Query(..., description="同步方向: 1 表示内部仓库同步到外部, 2 表示外部仓库同步到内部")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 POST 方法访问接口 {request.url.path} ", user)
        repo = await self.service.get_repo(repo_name=repo_name)
        if not repo.enable:
            return SYNCResponse(code_status=Status.NOT_ENABLE.code, msg=Status.NOT_ENABLE.msg)
        if sync_direct not in [1, 2]:
            return SYNCResponse(code_status=Status.SYNC_DIRE_ILLEGAL.code, msg=Status.SYNC_DIRE_ILLEGAL.msg)

        direct = SyncDirect(sync_direct)
        branches = await self.service.sync_branch(repo_id=repo.id, branch_name=branch_name, dire=direct)
        if len(branches) < 1:
            return SYNCResponse(code_status=Status.NOT_ENABLE.code, msg=Status.NOT_ENABLE.msg)

        try:
            await sync_branch_task(repo, branches, direct, user)
        except GITMSGException as GITError:
            return SYNCResponse(
                code_status=GITError.status,
                msg=GITError.msg
            )

        return SYNCResponse(code_status=Status.SUCCESS.code, msg=Status.SUCCESS.msg)

    @router.delete("/repo/{repo_name}", response_model=SYNCResponse, description='仓库解绑')
    async def delete_repo(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 DELETE 方法访问接口 {request.url.path} ", user)
        data = await self.service.delete_repo(repo_name=repo_name)
        return SYNCResponse(
            code_status=data.code_status,
            msg=data.status_msg
        )

    @router.delete("/{repo_name}/branch/{branch_name}", response_model=SYNCResponse, description='分支解绑')
    async def delete_branch(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            branch_name: str = Path(..., description="分支名称")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 DELETE 方法访问接口 {request.url.path} ", user)
        data = await self.service.delete_branch(repo_name=repo_name, branch_name=branch_name)
        return SYNCResponse(
            code_status=data.code_status,
            msg=data.status_msg
        )

    @router.put("/repo/{repo_name}/repo_addr", response_model=SYNCResponse, description='更新仓库地址')
    async def update_repo_addr(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            dto: ModifyRepoDTO = Body(..., description="更新仓库地址信息")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 PUT 方法访问接口 {request.url.path} ", user)
        data = await self.service.update_repo_addr(repo_name=repo_name, dto=dto)
        return SYNCResponse(
            code_status=data.code_status,
            msg=data.status_msg
        )

    @router.put("/repo/{repo_name}", response_model=SYNCResponse, description='更新仓库同步状态')
    async def update_repo_status(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            enable: bool = Query(..., description="同步启用状态")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 PUT 方法访问接口 {request.url.path} ", user)
        data = await self.service.update_repo(repo_name=repo_name, enable=enable)
        return SYNCResponse(
            code_status=data.code_status,
            msg=data.status_msg
        )

    @router.put("/{repo_name}/branch/{branch_name}", response_model=SYNCResponse, description='更新分支同步状态')
    async def update_branch_status(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            branch_name: str = Path(..., description="分支名称"),
            enable: bool = Query(..., description="同步启用状态")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 PUT 方法访问接口 {request.url.path} ", user)
        data = await self.service.update_branch(repo_name=repo_name, branch_name=branch_name, enable=enable)
        return SYNCResponse(
            code_status=data.code_status,
            msg=data.status_msg
        )

    @router.get("/repo/{repo_name}/logs", response_model=SYNCResponse, description='获取仓库/分支日志')
    async def get_logs(
            self, request: Request, user: str = Depends(user),
            repo_name: str = Path(..., description="仓库名称"),
            branch_id: int = Query(None, description="分支id（仓库粒度无需输入）"),
            page_num: int = Query(1, description="页数"), page_size: int = Query(10, description="条数"),
            create_sort: bool = Query(False, description="创建时间排序， 默认倒序")
    ):
        api_log(LogType.INFO, f"用户 {user} 使用 GET 方法访问接口 {request.url.path} ", user)
        data = await self.log_service.get_logs(repo_name=repo_name, branch_id=branch_id,
                                               page_num=page_num, page_size=page_size, create_sort=create_sort)
        if not data:
            return SYNCResponse(
                code_status=Status.CHECK_IN.code,
                data=data,
                msg=Status.CHECK_IN.msg
            )
        return SYNCResponse(
            code_status=Status.SUCCESS.code,
            data=data,
            msg=Status.SUCCESS.msg
        )

