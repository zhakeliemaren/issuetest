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
import asyncio

from sqlalchemy.sql.expression import false

from src.base.error_code import ErrorTemplate, Errors
from src.utils.logger import logger
from extras.obfastapi.frame import Trace, DataList
from extras.obfastapi.frame import OBResponse as Response
from extras.obfastapi.frame import OBHTTPException as HTTPException
from src.base.code import Code
from src.router import PROJECT as project
from src.router import JOB as job
from src.api.Controller import APIController as Controller
from src.dto.sync import Project as ProjectData
from src.dto.sync import Job as JobData
from src.dto.log import Log as LogData
from src.dto.sync import SyncType, CreateProjectItem, CreateJobItem
from src.service.sync import ProjectService, JobService
from src.service.pull_request import PullRequestService
from src.service.log import LogService
from src.utils import github, gitlab, gitee, gitcode, gitlink


class Project(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @project.get("", response_model=Response[DataList[ProjectData]], description='通过工程名获取一个同步工程')
    async def get_project(
        self,
        search: Optional[str] = Query(None, description='同步工程搜索内容'),
        orderby: Optional[str] = Query(None, description='排序选项'),
        pageNum: Optional[int] = Query(1, description="Page number"),
        pageSize: Optional[int] = Query(10, description="Page size")
    ):
        # search
        service = ProjectService()
        if search is None:
            count = await service.get_count()
            answer = await service.list_projects(page=pageNum, size=pageSize)
        else:
            count = await service.get_count_by_search(search.replace(" ", ""))
            answer = await service.search_project(name=search.replace(" ", ""))
        if answer is None:
            logger.error(f"The project list fetch failed")
            raise Errors.QUERY_FAILD
        return Response(
            code=Code.SUCCESS,
            data=DataList(total=count, list=answer)
        )

    @ project.post("", response_model=Response[ProjectData], description='创建一个同步工程')
    async def create_project(
        self,
        item: CreateProjectItem = Body(..., description='同步工程属性')
    ):
        # pre check
        if not item:
            raise ErrorTemplate.ARGUMENT_LACK("请求体")
        if not item.name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if item.github_address:
            if not github.check_github_address(item.github_address):
                raise ErrorTemplate.TIP_ARGUMENT_ERROR("GitHub仓库")
        if item.gitlab_address:
            if not gitlab.check_gitlab_address(item.gitlab_address):
                raise ErrorTemplate.TIP_ARGUMENT_ERROR("Gitlab/Antcode仓库")
        if item.gitee_address:
            if not gitee.check_gitee_address(item.gitee_address):
                raise ErrorTemplate.TIP_ARGUMENT_ERROR("Gitee仓库")
        if item.code_china_address:
            if not gitcode.check_gitcode_address(item.code_china_address):
                raise ErrorTemplate.TIP_ARGUMENT_ERROR("CodeChina仓库")
        # if item.gitlink_address:
        #     if not gitlink.check_gitlink_address(item.gitlink_address):
        #         raise ErrorTemplate.ARGUMENT_ERROR("Gitlink仓库")

        service = ProjectService()
        resp = await service.insert_project(item)
        if not resp:
            logger.error(f"The project insert failed")
            raise Errors.INSERT_FAILD
        organization, repo = github.transfer_github_to_name(
            item.github_address)

        if organization and repo:
            pull_request_service = PullRequestService()
            task = asyncio.create_task(
                pull_request_service.sync_pull_request(item.name, organization, repo))
        return Response(
            code=Code.SUCCESS,
            data=resp,
            msg="创建同步工程成功"
        )

    @ project.delete("", response_model=Response, description='通过id删除一个同步工程')
    async def delete_project(
        self,
        id: int = Query(..., description='同步工程id')
    ):
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("id")
        # if delete the project, the front page double check firstly
        project_service = ProjectService()
        project = await project_service.search_project(id=id)
        name = project[0].name
        # delete pull request
        pull_request_service = PullRequestService()
        resp = await pull_request_service.fetch_pull_request(name)
        if resp:
            if len(resp) > 0:
                for pr in resp:
                    await pull_request_service.delete_pull_request(pr.id)
        # delete sync job
        job_service = JobService()
        resp = await job_service.list_jobs(project=name)
        if not resp:
            pass
        else:
            for item in resp:
                await job_service.delete_job(item.id)
        # delete sync project
        resp = await project_service.delete_project(id)
        if not resp:
            logger.error(f"The project #{id} delete failed")
            raise Errors.DELETE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="删除同步工程成功"
        )


class Job(Controller):

    def get_user(self, cookie_key=Security(Controller.API_KEY_BUC_COOKIE), token: str = None):
        return super().get_user(cookie_key=cookie_key, token=token)

    @ job.get("/projects/{name}/jobs", response_model=Response[DataList[JobData]], description='列出所有同步流')
    async def list_jobs(
        self,
        name: str = Query(..., description='同步工程名'),
        search: Optional[str] = Query(None, description='同步工程搜索内容'),
        source: Optional[str] = Query(None, description='分支来源'),
        pageNum: Optional[int] = Query(1, description="Page number"),
        pageSize: Optional[int] = Query(10, description="Page size")
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        service = JobService()
        if search is not None:
            search = search.replace(" ", "")
        answer = await service.list_jobs(project=name, search=search, source=source, page=pageNum, size=pageSize)
        if not answer:
            return Response(
                code=Code.SUCCESS,
                data=DataList(total=0, list=[]),
                msg="没有同步流"
            )
        count = await service.count_job(project=name, search=search, source=source)
        return Response(
            code=Code.SUCCESS,
            data=DataList(total=count, list=answer),
            msg="查询同步流成功"
        )

    @ job.post("/projects/{name}/jobs", response_model=Response[JobData], description='创建一个同步流')
    async def create_job(
        self,
        name: str = Query(..., description='同步工程名'),
        item: CreateJobItem = Body(..., description='同步流属性')
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if not item:
            raise ErrorTemplate.ARGUMENT_LACK("JSON")
        if not item.type:
            raise ErrorTemplate.ARGUMENT_LACK("分支同步类型")

        service = JobService()
        ans = await service.create_job(name, item)
        if not ans:
            logger.error(f"Create a job of project #{name} failed")
            raise Errors.INSERT_FAILD
        return Response(
            code=Code.SUCCESS,
            data=ans,
            msg="创建同步流成功"
        )

    @ job.put("/projects/{name}/jobs/{id}/start", response_model=Response, description='开启一个同步流')
    async def start_job(
        self,
        name: str = Query(..., description='同步工程名'),
        id: int = Query(..., description='同步流id')
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("同步流id")
        service = JobService()
        ans = await service.update_status(id, True)
        if not ans:
            logger.error(f"The job #{id} of project #{name} start failed")
            raise Errors.UPDATE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="开启同步流成功"
        )

    @ job.put("/projects/{name}/jobs/{id}/stop", response_model=Response, description='停止一个同步流')
    async def stop_job(
        self,
        name: str = Query(..., description='同步工程名'),
        id: int = Query(..., description='同步流id')
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("同步流id")
        service = JobService()
        ans = await service.update_status(id, False)
        if not ans:
            logger.error(f"The job #{id} of project #{name} stop failed")
            raise Errors.UPDATE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="关闭同步流成功"
        )

    @ job.delete("/projects/{name}/jobs", response_model=Response, description='通过id删除一个同步流')
    async def delete_job(
        self,
        name: str = Query(..., description='同步工程名'),
        id: int = Query(..., description='同步流id')
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("同步流id")
        service = JobService()
        ans = await service.delete_job(id)
        if not ans:
            logger.error(f"The job #{id} of project #{name} delete failed")
            raise Errors.DELETE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="删除同步流成功"
        )

    @ job.put("/projects/{name}/jobs/{id}/set_commit", response_model=Response, description='通过id设置一个同步流的commit')
    async def set_job_commit(
        self,
        name: str = Query(..., description='同步工程名'),
        id: int = Query(..., description='同步流id'),
        commit: str = Query(..., description='commit'),
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("同步流id")

        service = JobService()
        job = await service.get_job(id)
        if not job:
            logger.error(f"The job #{id} of project #{name} is not exist")
            raise Errors.UPDATE_FAILD
        # only the sync type is oneway can use the commit
        if job.type == SyncType.TwoWay:
            logger.error(f"The job #{id} of project #{name} is two way sync")
            raise HTTPException(Code.OPERATION_FAILED, 'Twoway同步方式无法修改commit值')
        ans = await service.update_job_lateset_commit(id, commit)
        if not ans:
            logger.error(
                f"The job #{id} of project #{name} update latest commit failed")
            raise Errors.UPDATE_FAILD
        return Response(
            code=Code.SUCCESS,
            msg="设置同步流commit成功"
        )

    @ job.get("/projects/{name}/jobs/{id}/logs", response_model=Response[DataList[LogData]], description='列出所有同步流')
    async def get_job_log(
        self,
        name: str = Query(..., description='同步工程名'),
        id: int = Query(..., description='同步流id'),
        pageNum: Optional[int] = Query(1, description="Page number"),
        pageSize: Optional[int] = Query(1000, description="Page size")
    ):
        if not name:
            raise ErrorTemplate.ARGUMENT_LACK("工程名")
        if not id:
            raise ErrorTemplate.ARGUMENT_LACK("同步流id")
        project_service = ProjectService()
        projects = await project_service.search_project(name=name)
        if len(projects) == 0:
            raise ErrorTemplate.ARGUMENT_ERROR("工程名")
        service = LogService()
        log = await service.get_logs_by_job(id, pageNum, pageSize)
        data = []
        for rep_log in log:
            log_str = rep_log.log
            if projects[0].gitee_token:
                log_str = log_str.replace(projects[0].gitee_token, "******")
            if projects[0].github_token:
                log_str = log_str.replace(projects[0].github_token, "******")
            rep_log.log = log_str
            data.append(rep_log)

        if len(log) == 0:
            logger.info(
                f"The job #{id} of project #{name} has no logs")
        count = await service.count_logs(id)
        return Response(
            code=Code.SUCCESS,
            data=DataList(total=count, list=data)
        )
