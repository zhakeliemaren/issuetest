# The document.py script is used to sync the document project from oceanbase
import asyncio
import sys
import json
import time
sys.path.append('..')  # NOQA: E402

from src.service.sync import JobService, ProjectService
from src.service.log import LogService
from src.dto.sync import Color, SyncType
from src.dto.sync import Job as JobDTO
from src.dto.sync import Project as ProjectDTO
from src.utils import cmd, github
from src.utils import cmd, gitee
from src.utils import cmd, gitlink
from src.utils.logger import logger
from src.base import config
from src.utils.logger import Log
from src.base.code import LogType



async def sync_inter_code(project, job):
    if job.type == SyncType.TwoWay:
        await sync_inter_code_by_rabase(project, job)
    else:
        await Log(LogType.ERROR,
                  "The job {job.github_branch}'s type of project {project.name} is wrong", job.id)
        return


async def sync_inter_code_by_rabase(project: ProjectDTO, job: JobDTO):
    service = JobService()
    await Log(LogType.INFO, "Sync the job document to outer", job.id)
    dir = "/tmp/" + job.project+"_job_outer_"+str(job.id)
    await Log(LogType.INFO, f"The sync work dir is {dir}", job.id)

    try:
        await cmd.shell('mkdir ' + dir, '.', job)
        # base on the github new authentication rules
        # provide only two ways to clone and push code
        # 1. ssh key and ssh address
        # 2. http address with token
        #
        await cmd.shell(
            f"git clone -b {job.gitlink_branch} {project.gitlink_address} {project.name}", dir, job)
        repo_dir = dir + "/" + project.name
        # if you need http address with token
        # github_address = github.get_github_address_with_token(project.github_address, project.github_token)

        await cmd.shell('git status', repo_dir, job)
        # if github is not null, sync it
        if project.github_address and job.github_branch:
            github_address = github.get_github_address_with_token(project.github_address, project.github_token)
            await cmd.shell('git remote add github ' +
                            github_address, repo_dir, job)
            await cmd.shell('git fetch github', repo_dir, job)
            await cmd.shell(f"git pull github {job.github_branch} --no-edit", repo_dir, job)
        # if gitee is not null, sync it
        if project.gitee_address and job.gitee_branch:
            # gitee
            gitee_address = gitee.get_gitee_address_with_token(project.gitee_address, project.gitee_token)
            await cmd.shell('git remote add gitee ' +
                            gitee_address, repo_dir, job)
            await cmd.shell('git fetch gitee', repo_dir, job)
            await cmd.shell(f"git pull gitee {job.gitee_branch} --no-edit", repo_dir, job)

        # # if gitcode is not null, sync it
        # if project.code_china_address:
        #     await cmd.shell('git remote add csdn ' +
        #                     project.code_china_address, repo_dir, job)
        #     await cmd.shell('git fetch csdn', repo_dir, job)
        #     await cmd.shell(f"git pull csdn {job.code_china_branch} --no-edit", repo_dir, job)

        await cmd.shell(
            f"git push origin {job.gitlink_branch}", repo_dir, job)
        if project.github_address and job.github_branch:
            await cmd.shell(
                f"git push github {job.gitlink_branch}:{job.github_branch}", repo_dir, job)
        if project.gitee_address and job.gitee_branch:
            await cmd.shell(
                f"git push gitee {job.gitlink_branch}:{job.gitee_branch}", repo_dir, job)
        if project.code_china_address:
            await cmd.shell(
                f"git push csdn {job.github_branch}:{job.code_china_branch}", repo_dir, job)

        # update the latest commit hash
        # for rebase logic maybe is not useful
        result, err = await cmd.shell(
            "git log HEAD~1..HEAD --oneline", repo_dir, job)
        commit = result.split(" ")[0]
        await service.update_job_lateset_commit(job.id, commit)
    except Exception as e:
        msg = f"Sync the code from inter to outer of project {project.name} branch {job.github_branch} failed {e}"
        await Log(LogType.ERROR, msg, job.id)
    finally:
        await cmd.shell(f"rm -rf {dir}", '.', job)
        await Log(LogType.INFO, f"remove the temper repo folder {dir}", job.id)
    return


async def sync_job(job: JobDTO):
    project_service = ProjectService()
    project = await project_service.search_project(name=job.project)

    if len(project) == 0:
        await Log(LogType.INFO, "There are no projects in the database", job.id)
        return

    # 1. The git rabase logic does not need to fetch pull request.
    # 2. sync the inter code into outer
    await sync_inter_code(project[0], job)


async def sync():
    logger.info("Start syncing ****************************")
    log_service = LogService()
    await log_service.delete_logs()
    # fetch the sync job list
    service = JobService()
    # jobs = await service.list_jobs()
    # if jobs is None:
    #     logger.info(f"There are no sync jobs in the database")
    #     return
    # logger.info(f"There are {len(jobs)} sync jobs in the database")
    #
    # tasks = []
    # for job in jobs:
    #     # if the job status is green, it means we can sync the job
    #     if job.status == Color.green:
    #         await Log(LogType.INFO,
    #                   f"The gitlink branch {job.gitlink_branch} from {job.project} is now syncing", job.id)
    #         task = asyncio.create_task(sync_job(job))
    #         tasks.append(task)
    #     else:
    #         await Log(LogType.INFO,
    #                   f"The gitlink branch {job.gitlink_branch} from {job.project} does not need to sync", job.id)
    gitee_jobs = await service.source_list_jobs("gitee_branch")
    github_jobs = await service.source_list_jobs("github_branch")
    if gitee_jobs is None and github_jobs is None:
        logger.info(f"There are no sync jobs in the database")
        return
    logger.info(f"There are {len(gitee_jobs) + len(github_jobs)} sync jobs in the database")

    tasks = []
    for job in gitee_jobs:
        await Log(LogType.INFO,
                  f"The gitlink branch {job.gitlink_branch} from {job.project} is now syncing...", job.id)
        task = asyncio.create_task(sync_job(job))
        tasks.append(task)

    for task in tasks:
        await task

    time.sleep(10)
    logger.info("step 2 syncing.................")
    tasks2 = []
    for job in github_jobs:
        await Log(LogType.INFO,
                  f"The gitlink branch {job.gitlink_branch} from {job.project} is now syncing", job.id)
        task = asyncio.create_task(sync_job(job))
        tasks2.append(task)

    for task in tasks2:
        await task
    logger.info("End syncing ****************************")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sync())
