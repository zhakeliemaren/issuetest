from typing import List, Union, Optional, Dict
from typing import Any
from fastapi import (
    Body
)

from src.utils.logger import logger
from pydantic.main import BaseModel
from sqlalchemy import text
from .service import Service
from src.dao.sync import ProjectDAO, JobDAO
from src.do.sync import ProjectDO, JobDO
from src.dto.sync import Project as ProjectDTO
from src.dto.sync import Job as JobDTO
from src.dto.sync import CreateProjectItem, CreateJobItem


class ProjectService(Service):
    def __init__(self) -> None:
        self._project_dao = ProjectDAO()

    async def list_projects(self, page: int = 1, size: int = 10) -> Optional[List[ProjectDTO]]:
        start = (page - 1) * size
        all = await self._project_dao.fetch(start=start, limit=size)
        data = []
        for project in all:
            data.append(self._do_to_dto(project))
        return data

    async def insert_project(self, item: CreateProjectItem) -> Optional[ProjectDTO]:
        # we need to send request to check the input if illegal
        count = await self.get_count(text(f"name='{item.name}'"))
        if count > 0:
            logger.info(f"the project {item.name} is exist in the database")
            return None
        return await self._project_dao.insert_project(item)

    async def delete_project(self, id: str) -> Optional[bool]:
        return await self._project_dao.delete_project(id)

    async def search_project(self, id: Optional[int] = None, name: Optional[str] = None) -> Optional[List[ProjectDTO]]:
        limit = None
        start = 0
        if name:
            all = await self._project_dao.fetch(text(f"name like '%{name}%'"), limit, start)
        elif id:
            all = await self._project_dao.fetch(text(f"id='{id}'"), limit, start)
        else:
            all = []
        data = []
        if len(all) > 0:
            for project in all:
                data.append(self._do_to_dto(project))
        return data

    async def get_count(self, cond: Any = None) -> int:
        return await self._project_dao._get_count(cond)

    async def get_count_by_search(self, name: str) -> int:
        return await self.get_count(text(f"name like '%{name}%'"))

    def _do_to_dto(self, project) -> ProjectDTO:
        return ProjectDTO(
            **{
                'id': project["ProjectDO"].id,
                'name': project["ProjectDO"].name,
                'github_address': project["ProjectDO"].github,
                'gitee_address': project["ProjectDO"].gitee,
                'gitlab_address': project["ProjectDO"].gitlab,
                'code_china_address': project["ProjectDO"].code_china,
                'gitlink_address': project["ProjectDO"].gitlink,
                'github_token': project["ProjectDO"].github_token,
                'gitee_token': project["ProjectDO"].gitee_token
            }
        )


class JobService(Service):
    def __init__(self) -> None:
        self._job_dao = JobDAO()

    async def list_jobs(self, project: Optional[str] = None, search: Optional[str] = None,  source: Optional[str] = None, page: int = 1, size: int = 20) -> Optional[List[JobDTO]]:
        cond = None
        start = (page - 1) * size
        if project is None:
            all = await self._job_dao.fetch()
        else:
            cond = text(f"project = '{project}'")
            if search is not None:
                cond = text(
                    f"project = '{project}' and github_branch like '%{search}%'")
            if source is not None:
                cond = text(
                    f"project = '{project}' and LENGTH({source}) !=0")
            all = await self._job_dao.fetch(cond, start=start, limit=size)
        if not all:
            return None
        data = []
        for job in all:
            data.append(self._do_to_dto(job))
        return data

    async def source_list_jobs(self, source: Optional[str] = None) -> Optional[List[JobDTO]]:
        cond = None
        if source is not None:
            cond = text(f"status = 1 and LENGTH({source}) !=0")
        all = await self._job_dao.fetch(cond)
        data = []
        for job in all:
            data.append(self._do_to_dto(job))
        return data

    async def get_job(self, id: int) -> Optional[JobDTO]:
        job = await self._job_dao.fetch(text(f"id = {id}"))
        if not job:
            return None
        return self._do_to_dto(job[0])

    async def create_job(self, project, item: CreateJobItem) -> Optional[List[JobDO]]:
        # we do not need to check if exist the same github branch
        # we can sync a branch to different branches
        return await self._job_dao.insert_job(project, item)

    async def delete_job(self, id: int) -> Optional[bool]:
        return await self._job_dao.delete_job(id)

    async def get_count(self, cond: Any = None) -> int:
        return await self._job_dao._count(JobDO, cond)

    async def count_job(self, project: Optional[str] = None, search: Optional[str] = None, source: Optional[str] = None) -> int:
        if not project:
            return await self.get_count()
        else:
            cond = text(f"project = '{project}'")
            if search is not None:
                cond = text(
                    f"project = '{project}' and github_branch like '%{search}%'")
            if source is not None:
                cond = text(
                    f"project = '{project}' and LENGTH({source}) !=0")
            return await self.get_count(cond, )

    async def update_status(self, _id: int, _status: bool) -> bool:
        return await self._job_dao.update_status(_id, _status)

    async def get_job_lateset_commit(self, id: int) -> Optional[str]:
        job = await self.get_job(id)
        if job:
            return job.commit
        else:
            return None

    async def update_job_lateset_commit(self,  _id: int, _commit: str) -> bool:
        return await self._job_dao.update_commit(_id, _commit)

    def _do_to_dto(self, job) -> JobDTO:
        return JobDTO(
            **{
                'id': job["JobDO"].id,
                'project': job["JobDO"].project,
                'status': job["JobDO"].status,
                'type': job["JobDO"].type,
                'github_branch': job["JobDO"].github_branch,
                'gitee_branch': job["JobDO"].gitee_branch,
                'gitlab_branch': job["JobDO"].gitlab_branch,
                'code_china_branch': job["JobDO"].code_china_branch,
                'gitlink_branch': job["JobDO"].gitlink_branch,
                'commit': job["JobDO"].commit,
                'base': job["JobDO"].base,
                'create_time': job["JobDO"].create_time,
                'update_time': job["JobDO"].update_time
            }
        )
