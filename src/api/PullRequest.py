import time

from fastapi import (
    BackgroundTasks,
    Query,
    Depends,
    Security,
    Body
)
from typing import Optional

from starlette.exceptions import HTTPException

from src.utils.logger import logger
from extras.obfastapi.frame import Trace, DataList
from extras.obfastapi.frame import OBResponse as Response
from src.base.code import Code
from src.base.error_code import ErrorTemplate, Errors
from src.router import PULL_REQUEST as pull_request
from src.api.Controller import APIController as Controller
from src.dto.pull_request import PullRequest as PullRequestData
from src.service.pull_request import PullRequestService
from src.service.sync import ProjectService
from src.utils import github


class PullRequest(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @pull_request.get("/projects/{name}/pullrequests", response_model=Response[DataList[PullRequestData]], description='列出pull request')
    async def list_pull_request(
        self,
        name: str = Query(..., description='工程名字'),
        search: Optional[str] = Query(None, description='搜索内容'),
        orderby: Optional[str] = Query(None, description='排序选项')
    ):
        await self._check_project(name)
        pull_request_service = PullRequestService()
        count = await pull_request_service.count_pull_request(name)
        answer = await pull_request_service.fetch_pull_request(name)
        if not answer:
            logger.info(f"The project {name} has no pull request")
            answer = []
        return Response(
            code=Code.SUCCESS,
            data=DataList(total=count, list=answer)
        )

    @pull_request.get("/projects/{name}/pullrequests/sync", response_model=Response, description='列出pull request')
    async def sync_pull_request(
        self,
        name: str = Query(..., description='工程名字')
    ):
        resp = await self._check_project(name)
        organization, repo = github.transfer_github_to_name(
            resp[0].github_address)
        if organization and repo:
            pull_request_service = PullRequestService()
            await pull_request_service.sync_pull_request(name, organization, repo)
        else:
            logger.error(f"The pull rquest of project {name} sync failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="发送同意请求成功"
        )

    @pull_request.get("/projects/{name}/pullrequests/{id}/approve", response_model=Response, description='同意一个pull request')
    async def approve_pull_request(
        self,
        name: str = Query(..., description='同步工程名称'),
        id: int = Query(..., description='pull request id')
    ):
        if not name or not id:
            raise ErrorTemplate.ARGUMENT_LACK()
        resp = await self._check_project(name)
        organization, repo = github.transfer_github_to_name(
            resp[0].github_address)

        if organization and repo:
            pull_request_service = PullRequestService()
            resp = await pull_request_service.approve_pull_request(organization, repo, id)
            if not resp:
                logger.error(
                    f"The pull rquest #{id} of project {name} approve failed")
                raise Errors.QUERY_FAILD
        else:
            logger.error(
                f"Get the project {name} organization and repo failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="发送同意请求成功"
        )

    @pull_request.get("/projects/{name}/pullrequests/{id}/merge", response_model=Response, description='合并一个pull request')
    async def merge_pull_request(
        self,
        name: str = Query(..., description='同步工程名称'),
        id: int = Query(..., description='pull request id')
    ):
        if not name or not id:
            raise ErrorTemplate.ARGUMENT_LACK()
        resp = await self._check_project(name)
        organization, repo = github.transfer_github_to_name(
            resp[0].github_address)

        if organization and repo:
            pull_request_service = PullRequestService()
            resp = await pull_request_service.merge_pull_request(organization, repo, id)
            if not resp:
                logger.error(
                    f"The pull rquest #{id} of project {name} merge failed")
                raise Errors.QUERY_FAILD
        else:
            logger.error(
                f"Get the project {name} organization and repo failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="发送合并请求成功"
        )

    @pull_request.get("/projects/{name}/pullrequests/{id}/close", response_model=Response, description='关闭一个pull request')
    async def close_pull_request(
        self,
        name: str = Query(..., description='同步工程名称'),
        id: int = Query(..., description='pull request id')
    ):
        if not name or not id:
            raise ErrorTemplate.ARGUMENT_LACK()
        resp = await self._check_project(name)
        organization, repo = github.transfer_github_to_name(
            resp[0].github_address)

        if organization and repo:
            pull_request_service = PullRequestService()
            resp = await pull_request_service.close_pull_request(organization, repo, id)
            if not resp:
                logger.error(
                    f"The pull rquest #{id} of project {name} close failed")
                raise Errors.QUERY_FAILD
        else:
            logger.error(
                f"Get the project {name} organization and repo failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="发送关闭请求成功"
        )

    @pull_request.get("/projects/{name}/pullrequests/{id}/press", response_model=Response, description='催促一个pull request')
    async def press_pull_request(
        self,
        name: str = Query(..., description='同步工程名称'),
        id: int = Query(..., description='pull request id')
    ):
        # await self._check_project(name)
        # service = PullRequestService()
        # resp = await service.press_pull_request()
        # if not resp:
        #     code = Code.INVALID_PARAMS
        #     msg = "发送催促请求失败"
        # else:
        #     code = Code.SUCCESS
        #     msg = "发送催促请求成功"
        return Response(
            code=Code.SUCCESS,
            msg="第二期功能，敬请期待"
        )

    async def _check_project(self, name: str):
        project_service = ProjectService()
        resp = await project_service.search_project(name=name)
        if len(resp) == 0:
            logger.error(
                f"The project {name} is not exist")
            raise Errors.QUERY_FAILD
        return resp
