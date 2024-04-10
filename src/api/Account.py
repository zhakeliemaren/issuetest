import time

from fastapi import (
    BackgroundTasks,
    Query,
    Depends,
    Security,
    Body
)
from pydantic.main import BaseModel
from typing import Optional

from src.utils.logger import logger
from extras.obfastapi.frame import Trace, DataList
from extras.obfastapi.frame import OBResponse as Response
from src.base.code import Code
from src.router import ACCOUNT as account
from src.base.error_code import ErrorTemplate, Errors
from src.api.Controller import APIController as Controller
from src.dto.account import GithubAccount as GithubAccountData
from src.service.account import GithubAccountService, GiteeAccountService
from src.dto.account import CreateAccountItem, UpdateAccountItem


class Account(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @account.get("/github_accounts", response_model=Response[DataList[GithubAccountData]], description='展示GitHub账号信息')
    async def list_github_account(
        self,
        search: Optional[str] = Query(None, description='搜索内容'),
        orderby: Optional[str] = Query(None, description='排序选项'),
        pageNum: int = Query(1, description="Page number"),
        pageSize: int = Query(10, description="Page size")
    ):
        account_service = GithubAccountService()
        if search is not None:
            search = search.replace(" ", "")
        count = await account_service.get_count(search=search)
        ans = await account_service.list_github_account(search)
        if ans is None:
            logger.error("Github accounts fetch failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            data=DataList(total=count, list=ans)
        )

    @ account.get("/gitee_accounts", response_model=Response[DataList[GithubAccountData]], description='展示Gitee账号信息')
    async def list_gitee_account(
        self,
        search: Optional[str] = Query(False, description='搜索内容'),
        orderby: Optional[str] = Query(False, description='排序选项'),
        pageNum: int = Query(1, description="Page number"),
        pageSize: int = Query(10, description="Page size")
    ):
        account_service = GiteeAccountService()
        count = await account_service.get_count()
        ans = await account_service.list_gitee_account()
        if ans is None:
            logger.error("Gitee accounts fetch failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            data=DataList(total=count, list=ans)
        )

    @ account.post("/github_accounts", response_model=Response, description='增加一条GitHub账号信息')
    async def add_github_account(
        self,
        item: CreateAccountItem = (...)
    ):
        account_service = GithubAccountService()
        ans = await account_service.insert_github_account(item)
        if ans is None:
            logger.error(f"Insert Github accounts {item.domain} failed")
            raise Errors.INSERT_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="添加账号成功",
        )

    @ account.post("/gitee_accounts", response_model=Response, description='增加一条Gitee账号信息')
    async def add_gitee_account(
        self,
        item: CreateAccountItem = (...)
    ):
        account_service = GiteeAccountService()
        ans = await account_service.insert_gitee_account(item)
        if ans is None:
            logger.error(f"Insert Gitee accounts {item.domain} failed")
            raise Errors.INSERT_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="添加账号成功",
        )

    @ account.delete("/github_accounts", response_model=Response, description='删除一条GitHub账号信息')
    async def delete_github_account(
        self,
        id: int = Query(..., description="账号id")
    ):
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("删除用户账号")
        account_service = GithubAccountService()
        ans = await account_service.delete_github_account(id)
        if not ans:
            logger.error(f"Delete Github accounts failed")
            raise Errors.DELETE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg='删除成功'
        )

    @ account.delete("/gitee_accounts", response_model=Response, description='删除一条Gitee账号信息')
    async def delete_gitee_account(
        self,
        id: int = Query(..., description="账号id")
    ):
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("删除用户账号")
        account_service = GiteeAccountService()
        ans = await account_service.delete_gitee_account(id)
        if not ans:
            logger.error(f"Delete Gitee accounts failed")
            raise Errors.DELETE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg='删除成功'
        )

    @ account.put("/github_accounts", response_model=Response, description='更新一条GitHub账号信息')
    async def update_github_account(
        self,
        item: UpdateAccountItem = (...)
    ):
        account_service = GithubAccountService()
        ans = await account_service.update_github_account(item)
        if not ans:
            raise Errors.UPDATE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg='更新成功'
        )

    @ account.put("/gitee_accounts", response_model=Response, description='更新一条Gitee账号信息')
    async def update_gitee_account(
        self,
        item: UpdateAccountItem = (...)
    ):
        account_service = GiteeAccountService()
        ans = await account_service.update_gitee_account(item)
        if not ans:
            raise Errors.UPDATE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg='更新成功'
        )
