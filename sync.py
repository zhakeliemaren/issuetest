import asyncio
import os
import json
from typing import Optional
import requests
import re
from pathlib import Path


from src.service.pull_request import PullRequestService
from src.service.sync import JobService, ProjectService
from src.service.log import LogService
from src.dto.sync import Color, SyncType
from src.dto.sync import Job as JobDTO
from src.dto.pull_request import PullRequest as PullRequestDTO
from src.dto.sync import Project as ProjectDTO
from src.utils import cmd, author, gitlab, github
from src.utils.logger import logger
from src.base import config
from src.utils.logger import Log
from src.base.code import LogType
from src.common.repo import Repo, RepoType


async def apply_diff(project, job, pull: PullRequestDTO, dir):
    organization, repo = github.transfer_github_to_name(project.github_address)

    baseUrl = ""
    if pull.type == RepoType.Github:
        baseUrl = f"{config.GITHUB_ENV['github_api_diff_address']}/{organization}/{repo}/pull/"
    elif pull.type == RepoType.Gitee:
        baseUrl = f"{config.GITEE_ENV['gitee_api_diff_address']}/{organization}/{repo}/pull/"
    elif pull.type == RepoType.Gitcode:
        pass

    diffUrl = baseUrl + str(pull.id) + ".diff"
    tmpfile = dir + "/" + str(pull.id) + "_diff"

    download_diff_cmd = ""
    if pull.type == RepoType.Github:
        download_diff_cmd = f"curl -X GET {diffUrl} -H 'Accept: application/vnd.github.v3.diff'"
    elif pull.type == RepoType.Gitee:
        download_diff_cmd = f"curl -X GET {diffUrl}"
    elif pull.type == RepoType.Gitcode:
        pass

    with open(tmpfile, "w") as diff_file:
        diff, err = await cmd.shell(download_diff_cmd, dir, job)
        diff_file.write(diff)

    # git apply --check first
    out, err = await cmd.shell('git apply --check ' + tmpfile, dir, job)
    if out != "":
        raise ValueError(f"git apply --check failed")
    out, err = await cmd.shell('git apply ' + tmpfile, dir, job)
    if err.startswith("error"):
        await Log(LogType.ERROR, "The git apply operation has some conflict", job.id)
        await cmd.shell('rm -rf ' + dir, '.', job)
        return
    await cmd.shell(f"rm -rf {tmpfile}", dir, job)
    await cmd.shell('git add .', dir, job)


async def sync_common(project, job, pull: PullRequestDTO):
    try:
        await Log(LogType.INFO, f"The project base repo is {project.base}", job.id)

        await Log(LogType.INFO, f"Sync the job code from other repo to base {project.base} repo", job.id)
        dir = f"/tmp/{job.project}_job_inter_{job.id}_pull_{pull.id}"

        await Log(LogType.INFO, f"The pull request dir is {dir}", job.id)
        await cmd.shell('mkdir ' + dir, '.', job)

        await cmd.shell(
            f"git clone -b {job.gitlab_branch} {project.gitlab_address}", dir, job)
        repo_dir = dir + "/" + project.name

        # GitHub pull request
        if project.base != RepoType.Github and project.github_address is not None:
            await cmd.shell('git status', repo_dir, job)
            new_branch = 'github_pr' + str(pull.id)
            await Log(LogType.INFO, f"The new branch is {new_branch}", job.id)
            await cmd.shell('git checkout -b ' + new_branch, repo_dir, job)

            apply_diff(project, job, pull, repo_dir)
            commit_msg = "Github pull request #" + str(pull.id)
            await cmd.shell(f"git commit -m \"{commit_msg}\"", repo_dir, job)
            await cmd.shell(f"git push -uv origin {new_branch}", repo_dir, job)

            inter_type = gitlab.get_inter_repo_type(project.gitlab_address)
            if inter_type is None:
                await Log(LogType.ERROR,
                          f"The {project.gitlab_address} is not belong to gitlab or antcode", job.id)
            else:
                # send a merge request
                if inter_type == 'gitlab':
                    # Alibaba Gitlab repo（Code Aone）
                    await Log(LogType.INFO,
                              f"Merge the pull request to internal Gitlab {project.name}", job.id)
                    repo_id = gitlab.get_repo_id_from_url(
                        project.gitlab_address)
                    if repo_id is None:
                        await Log(LogType.ERROR,
                                  f"We can not get the repo id {repo_id}", job.id)
                    await Log(LogType.INFO,
                              f"The project's gitlab repo id is {repo_id}", job.id)
                    await Log(LogType.INFO,
                              f"send the merge request about the pull request #{pull.id}", job.id)
                    merge_to_code_aone_inter(
                        repo_id, pull.id, new_branch, job.gitlab_branch)
                else:
                    # Alipay Antcode repo
                    await Log(LogType.INFO,
                              f"Merge the pull request to internal Antcode {project.name}", job.id)
                    organization, name = gitlab.get_organization_and_name_from_url(
                        project.gitlab_address)

                    merge_to_antcode_inter(
                        job.id, pull.id, organization, name, new_branch, job.gitlab_branch)

                # update the pull request inline status
                service = PullRequestService()
                await service.update_inline_status(pull, True)
                await service.update_latest_commit(pull)

        # Gitee pull request

        # TODO: Gitcode pull request

    except:
        msg = f"The pull request #{pull.id} sync to the internal failed"
        await Log(LogType.ERROR, msg, job.id)
    finally:
        await cmd.shell('rm -rf ' + dir, '.', job)


def merge_to_code_aone_inter(repo_id: int, pull_id: int, source_branch: str, target_branch: str):
    url = f""
    param = {
        'private_token': config.ACCOUNT['gitlab_token'],
    }
    data = {
        "description": "Merge the pull request #" + str(pull_id),
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": "Merge the pull request #" + str(pull_id)
    }
    response = requests.post(url=url, params=param,
                             data=json.dumps(data)).json()
    return response


async def merge_to_antcode_inter(job_id: int, pull_id: int, organization, name, source_branch, target_branch: str):
    await Log(LogType.INFO,
              "send the merge request about the pull request #{pull_id}", job_id)
    headers = {
        "PRIVATE-TOKEN": config.ACCOUNT['antcode_token']
    }
    mainSiteUrl = ""
    organization = "oceanbase-docs"
    name = "oceanbase-doc"
    path = f"{organization}/{name}"
    req_str = f"{mainSiteUrl}/api/v3/projects/find_with_namespace?path={path}"
    response = requests.get(url=req_str, headers=headers).json()
    projectId = response['id']
    await Log(LogType.INFO, f"The Antcode project ID is {projectId}", job_id)
    # merge request
    merge_req_str = f"{mainSiteUrl}/api/v3/projects/{projectId}/pull_requests"
    param = {
        'source_branch': source_branch,
        'target_branch': target_branch,
        'squash_merge': True
    }
    response = requests.post(
        url=merge_req_str, param=param, headers=headers).json()
    return


async def sync_oceanbase(project, job, pull):
    title = f"Github merge request #{pull.id} {pull.title}"
    # Sync OceanBase code need ob flow
    await Log(LogType.INFO, "Sync the oceanbase code from github to inter", job.id)
    # Create ob task
    create_task_cmd = f"/usr/local/obdev/libexec/ob-task create --subject=\"{title}\" -T bug --branch={job.gitlab_branch} --description=\"{title}\""
    out, err = await cmd.shell(create_task_cmd, '.', job, env=dict(os.environ, AONE_ISSUE_NICK='官明'))
    issue_num = str.splitlines(out)[1].replace("[issue-id]", "").strip()
    await Log(LogType.INFO,
              f"The issue number is {issue_num} about the oceanbase pull request {pull.id}", job.id)
    task_id = issue_num.replace("T", "")
    if task_id != "":
        await Log(LogType.INFO,
                  f"Create the task {task_id} successfully by ob flow", job.id)
    await cmd.shell(
        f"/usr/local/obdev/libexec/ob-flow start T{task_id} {job.gitlab_branch}", '.', job,  env=dict(
            os.environ, OB_FLOW_PROJECT='oceanbase'))
    task_addr = f"/data/1/wangzelin.wzl/task-{task_id}"
    apply_diff(project, job, pull, task_addr)
    await cmd.shell(f"git commit -m \"{title}\"", task_addr, job)

    await cmd.shell("/usr/local/obdev/libexec/ob-flow checkin", task_addr, job)
    service = PullRequestService()
    await service.update_inline_status(pull, True)
    await service.update_latest_commit(pull)


async def sync_pull_request(project, job):
    organization, repo = github.transfer_github_to_name(project.github_address)
    if organization and repo:
        pull_request_service = PullRequestService()
        await pull_request_service.sync_pull_request(project.name, organization, repo)

    pull_request_service = PullRequestService()
    pull_request_list = await pull_request_service.fetch_pull_request(project=job.project)

    if pull_request_list and len(pull_request_list) > 0:
        await Log(LogType.INFO,
                  f"There are {len(pull_request_list)} pull requests in the database", job.id)

        for pull in pull_request_list:
            if pull.target_branch == job.github_branch:
                await Log(LogType.INFO,
                          f"Judge the pull request #{pull.id} of project {project.name} if need to merge", job.id)
                need_merge = await pull_request_service.judge_pull_request_need_merge(project.name, organization, repo, pull.id)
                if need_merge:
                    await Log(LogType.INFO,
                              f"The pull request #{pull.id} of project {project.name} need merge", job.id)
                    if job.project == "oceanbase":
                        # Add a self config to sync the pull request what you want
                        if pull.id in config.OCEANBASE:
                            await sync_oceanbase(project, job, pull)
                    else:
                        await sync_common(project, job, pull)
                else:
                    await Log(LogType.INFO,
                              f"The pull request #{pull.id} of project {project.name} does not need merge", job.id)
        return


async def sync_inter_code(project, job):
    # Judge the repo type
    if job.type == SyncType.OneWay:
        await sync_oneway_inter_code(project, job)
    elif job.type == SyncType.TwoWay:
        await sync_twoway_inter_code(project, job)
    else:
        await Log(LogType.ERROR,
                  "The job {job.github_branch}'s type of project {project.name} is wrong", job.id)
        return


async def sync_oneway_inter_code(project: ProjectDTO, job: JobDTO):
    service = JobService()
    await Log(LogType.INFO, "Sync the job code to outer", job.id)
    dir = f"/data/1/tmp/{job.project}_job_outer_{job.id}"
    await Log(LogType.INFO, f"The sync work dir is {dir}", job.id)

    try:
        await cmd.shell('mkdir ' + dir, '.', job)
        await cmd.shell(
            f"git clone -b {job.gitlab_branch} {project.gitlab_address} --depth=100", dir, job)
        repo_dir = dir + "/" + project.name

        await cmd.shell('git status', repo_dir, job)
        await cmd.shell(
            f"git remote add github {project.github_address}", repo_dir, job)
        await cmd.shell('git fetch github', repo_dir, job)
        await cmd.shell(
            f"git checkout -b out_branch github/{job.github_branch}", repo_dir, job)
        await cmd.shell('git checkout ' + job.gitlab_branch, repo_dir, job)

        if project.gitee_address:
            await cmd.shell(
                f"git remote add gitee {project.gitee_address}", repo_dir, job)
            await cmd.shell('git fetch gitee', repo_dir, job)

        if project.code_china_address:
            await cmd.shell(
                f"git remote add csdn {project.code_china_address}", repo_dir, job)
            result, err = await cmd.shell('git status', repo_dir, job)

        # fetch the latest commit
        latestCommit = await service.get_job_lateset_commit(job.id)
        await Log(LogType.INFO, 'The lastest commit is ' + latestCommit, job.id)

        if latestCommit == 'no_commit':
            result, err = await cmd.shell(
                f"git log HEAD^1..HEAD --oneline --merges", repo_dir, job)
            commit = result.split(" ")[0]
            await Log(LogType.INFO, f"patch the commit {commit}", job.id)
            await patch_every_commit(repo_dir, project, job, commit)
            return
        else:
            result, err = await cmd.shell(
                "git log "+latestCommit + "..HEAD --oneline --merges", repo_dir, job)

            if result == "":
                await Log(LogType.INFO,
                          f"The commit {latestCommit} is the newest commit on the remote branch", job.id)
            else:
                commit_info_list = str.splitlines(result)
                commit_info_list.reverse()
                for commit_info in commit_info_list:
                    commit = commit_info.split(" ")[0]
                    await Log(LogType.INFO, "patch the commit " + commit, job.id)
                    await patch_every_commit(repo_dir, project, job, commit)
    except:
        msg = f"Sync the code from inter to outer of project {project.name} branch {job.github_branch} failed"
        await Log(LogType.ERROR, msg, job.id)
    finally:
        await cmd.shell(f"rm -rf {dir}", '.', job)
        await Log(LogType.INFO, f"remove the temper repo folder {dir}", job.id)
    return


async def sync_twoway_inter_code(project, job):
    service = JobService()
    await Log(LogType.INFO, "Sync the job document to outer", job.id)
    dir = "/tmp/" + job.project+"_job_outer_"+str(job.id)
    await Log(LogType.INFO, f"The sync work dir is {dir}", job.id)

    try:
        await cmd.shell('mkdir ' + dir, '.', job)
        await cmd.shell(
            f"git clone -b {job.gitlab_branch} {project.gitlab_address}", dir, job)
        repo_dir = dir + "/" + project.name

        await cmd.shell('git status', repo_dir, job)
        await cmd.shell('git remote add github ' +
                        project.github_address, repo_dir, job)
        await cmd.shell('git fetch github', repo_dir, job)
        await cmd.shell('git pull -r github ' + job.github_branch, repo_dir, job)
        await cmd.shell(
            f"git push origin {job.gitlab_branch} -f", repo_dir, job)
        await cmd.shell(
            f"git push github {job.github_branch} -f", repo_dir, job)

        if project.gitee_address:
            await cmd.shell('git remote add gitee ' +
                            project.gitee_address, repo_dir, job)
            await cmd.shell('git fetch gitee', repo_dir, job)
            await cmd.shell(
                f"git push gitee {job.gitlab_branch}:{job.gitee_branch}", repo_dir, job)

        if project.code_china_address:
            await cmd.shell('git remote add csdn ' +
                            project.code_china_address, repo_dir, job)
            result, err = await cmd.shell('git status', repo_dir, job)
            await cmd.shell(
                f"git push csdn {job.gitlab_branch}:{job.code_china_branch}", repo_dir, job)

        # update the latest commit hash
        result, err = await cmd.shell(
            "git log HEAD~1..HEAD --oneline", repo_dir, job)
        commit = result.split(" ")[0]
        await service.update_job_lateset_commit(job.id, commit)
    except:
        msg = f"Sync the document from inter to outer of project {project.name} branch {job.github_branch} failed"
        await Log(LogType.Error, msg, job.id)
    finally:
        await cmd.shell(f"rm -rf {dir}", '.', job)
        await Log(LogType.INFO, f"remove the temper repo folder {dir}", job.id)
    return


def get_author_from_oceanbase(author_content: str) -> Optional[str]:
    partten = r'Author : (.*) \((.*)\)'
    matchObj = re.match(partten, author_content, re.M | re.I)
    if matchObj:
        author = matchObj.group(2)
        return author.split('#')[0]
    return None


async def patch_every_commit(dir, project, job, commit):
    service = JobService()

    try:
        await cmd.shell('git status', dir, job)
        await cmd.shell('git checkout ' + job.gitlab_branch, dir, job)
        await cmd.shell('git pull -r origin ' + job.gitlab_branch, dir, job)
        await cmd.shell('git reset --hard ' + commit, dir, job)

        # Get the commit comment
        output, err = await cmd.shell("git log -1", dir, job)

        email, err = await cmd.shell("git log --format='%ae' -1", dir, job)
        if email is None:
            raise ValueError("The commit has no email")
        await Log(LogType.INFO, f"The commit {commit} email is {email}", job.id)

        if project.name == "oceanbase":
            author_string = str.splitlines(output)[8].strip()
            await Log(LogType.INFO,
                      f"The author string is {author_string}", job.id)
            domain = get_author_from_oceanbase(author_string)
        else:
            domain = author.get_author_domain(email)
        if domain is None:
            raise ValueError("The commit author has no ali domain")
        await Log(LogType.INFO, f"The commit author ali domain is {domain}", job.id)

        content = str.splitlines(output)[5].strip()
        await Log(LogType.INFO, f"content is {content}", job.id)
        if content is None or content == "":
            raise ValueError("The commit has no commit content")
        await Log(LogType.INFO, f"The commit {commit} content is {content}", job.id)
        # TODO if find the commit is from github, merge the pull request
        if content.startswith("Github Merge"):
            pr_id = int(content.split()[3].replace('#', ''))
            pr_service = PullRequestService()
            organization, repo = github.transfer_github_to_name(
                project.github_address)
            ans = await pr_service.merge_pull_request_code(organization, repo, pr_id)
            if ans is None:
                return

        # if the repo has .ce file, it means we should do something before merge
        # the code from inter to outer
        ce_file = Path(dir + '/.ce')
        if ce_file.is_file():
            await cmd.shell('bash .ce', dir, job)
        else:
            await Log(LogType.INFO,
                      f"There is no .ce file in the project {project.name}", job.id)

        # TODO check git diff apply --check
        diff, err = await cmd.shell("git diff out_branch", dir, job)
        if diff == "":
            # The diff is empty, save the commit and return
            await cmd.shell('git reset --hard', dir, job)
            await service.update_job_lateset_commit(job.id, commit)
            return

        patch_file = '/tmp/' + job.github_branch + '_patch'
        await cmd.shell('rm -rf ' + patch_file, dir, job)

        with open(patch_file, "w") as diff_file:
            diff, err = await cmd.shell("git diff out_branch", dir, job)
            diff_file.write(diff)

        await cmd.shell('git reset --hard', dir, job)
        await cmd.shell('git checkout out_branch', dir, job)

        # git apply --check first
        # out, err = await cmd.shell('git apply --check ' + patch_file, dir, job)
        if err != "":
            raise ValueError(
                f"The commit {commit} has conflict to the branch {job.github_branch}")

        await cmd.shell('git apply ' + patch_file, dir, job)
        await cmd.shell('git add .', dir, job)
        await cmd.shell(f"git commit -m \"{content}\"", dir, job)

        # TODO:change commit author
        out = await author.get_github_author_and_email(domain)
        if out['author'] is None or out['email'] is None:
            await Log(LogType.ERROR, f"The commit has no correct author or email", job.id)
            raise ValueError("That is not a positive author or email")
        await Log(LogType.INFO,
                  f"Get the commit author {out['author']} and email {out['email']}", job.id)

        author_info = f"{out['author']} <{out['email']}>"
        await cmd.shell(
            f"git commit --amend --no-edit --author=\"{author_info}\"", dir, job)

        await cmd.shell(f"git pull -r github {job.github_branch}", dir, job)
        await cmd.shell(f"git push -u github out_branch:{job.github_branch}", dir, job)

        if job.gitee_branch is not None:
            await cmd.shell(f"git pull -r gitee {job.gitee_branch}", dir, job)
            await cmd.shell(f"git push -u gitee out_branch:{job.gitee_branch}", dir, job)

        if job.code_china_branch is not None:
            await cmd.shell(f"git pull -r csdn {job.code_china_branch}", dir, job)
            await cmd.shell(f"git push -u csdn out_branch:{job.code_china_branch}", dir, job)

        await cmd.shell(f"git checkout {job.gitlab_branch}", dir, job)

        # save the latest commit
        ans = await service.update_job_lateset_commit(job.id, commit)
        if ans:
            await Log(LogType.INFO,
                      f"Update the latest commit {commit} successfully", job.id)
    except:
        msg = f"Sync the commit {commit} of project {project.name} failed"
        await Log(LogType.ERROR, msg, job.id)
    return


async def sync_job(job: JobDTO):
    project_service = ProjectService()
    project = await project_service.search_project(name=job.project)

    if len(project) == 0:
        await Log(LogType.INFO, "There are no projects in the database", job.id)
        return

    # 1. sync the outer pull request into inter
    if job.type == SyncType.OneWay:
        await sync_pull_request(project[0], job)
    # 2. sync the inter code into outer
    await sync_inter_code(project[0], job)


async def sync():
    logger.info("Start syncing ****************************")
    log_service = LogService()
    await log_service.delete_logs()
    # fetch the sync job list
    service = JobService()
    jobs = await service.list_jobs()
    if jobs is None:
        logger.info(f"There are no sync jobs in the database")
        return
    logger.info(f"There are {len(jobs)} sync jobs in the database")

    tasks = []
    for job in jobs:
        # if the job status is green, it means we can sync the job
        if job.status == Color.green:
            await Log(LogType.INFO,
                      f"The github branch {job.github_branch} from {job.project} is now syncing", job.id)
            task = asyncio.create_task(sync_job(job))
            tasks.append(task)
        else:
            await Log(LogType.INFO,
                      f"The github branch {job.github_branch} from {job.project} does not need to sync", job.id)
    for task in tasks:
        await task
    logger.info("End syncing ****************************")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sync())
