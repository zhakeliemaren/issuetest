import os
import re
import shlex
import subprocess
from typing import List
from src.base import config
from src.base.status_code import GITMSGException, Status, git_error_mapping
from src.base.config import SYNC_DIR
from src.dao.sync_config import SyncRepoDAO, SyncBranchDAO
from src.do.sync_config import SyncDirect, SyncType
from src.dto.sync_config import SyncBranchDTO
from src.utils.sync_log import sync_log, LogType, log_path, api_log
from src.service.sync_config import LogService

sync_repo_dao = SyncRepoDAO()
sync_branch_dao = SyncBranchDAO()
log_service = LogService()


# 根据错误码获取枚举实例
def get_git_error(stderr: str):
    for error_str, git_error in git_error_mapping.items():
        if re.search(error_str, stderr):
            return GITMSGException(git_error)
    return GITMSGException(Status.UNKNOWN_ERROR)


def get_repo_address_with_token(address: str, token: str) -> str:
    if token is None or token == "":
        return address
    try:
        if not address.startswith('https') and not address.startswith('http'):
            raise Exception('address is error')

        if address.startswith('https'):
            owner_name = address[8:].split("/")[1]
            return address[:8] + owner_name + ":" + token + '@' + address[8:]
        elif address.startswith('http'):
            owner_name = address[7:].split("/")[1]
            return address[:7] + owner_name + ":" + token + '@' + address[7:]
    except Exception as e:
        print(e)


def shell(cmd, dire: str, log_name: str, user: str):
    log = f'Execute cmd: ' + cmd
    if 'git clone' in log:
        sync_log(LogType.INFO, 'Execute cmd: git clone', log_name, user)
    elif 'git remote' in log:
        sync_log(LogType.INFO, '添加/更新仓库信息', log_name, user)
    elif 'git ls-remote' in log:
        sync_log(LogType.INFO, '获取仓库分支信息', log_name, user)
    else:
        sync_log(LogType.INFO, log, log_name, user)
    output = subprocess.run(shlex.split(cmd), cwd=dire, capture_output=True, text=True)
    if output.returncode != 0:
        git_error = get_git_error(output.stderr)
        if config.LOG_DETAIL:
            sync_log(LogType.ERROR, output.stderr, log_name, user)
        raise git_error
    return output


def init_repos(repo, log_name: str, user: str):
    not os.path.exists(SYNC_DIR) and os.makedirs(SYNC_DIR)
    repo_dir = os.path.join(SYNC_DIR, repo.repo_name)
    if not os.path.exists(repo_dir):
        sync_log(LogType.INFO, "初始化仓库 *********", log_name, user)
        inter_repo_addr = get_repo_address_with_token(repo.internal_repo_address, repo.inter_token)
        exter_repo_addr = get_repo_address_with_token(repo.external_repo_address, repo.exter_token)
        if repo.sync_direction == SyncDirect.to_outer:
            # 克隆内部仓库到同步目录下
            shell(f'git clone -b master {inter_repo_addr} {repo_dir}', SYNC_DIR, log_name, user)
        else:
            # 克隆外部仓库到同步目录下
            shell(f'git clone -b master {exter_repo_addr} {repo_dir}', SYNC_DIR, log_name, user)
        # 添加internal远程仓库，并强制使用
        shell(f'git remote add -f internal {inter_repo_addr}', repo_dir, log_name, user)
        # 添加external远程仓库，并强制使用
        shell(f'git remote add -f external {exter_repo_addr}', repo_dir, log_name, user)


def inter_to_outer(repo, branch, log_name: str, user: str):
    repo_dir = os.path.join(SYNC_DIR, repo.repo_name)
    inter_name = branch.internal_branch_name
    outer_name = branch.external_branch_name
    try:
        # 从internal仓库的指定分支inter_name中获取代码，更新远程分支的信息到本地仓库
        shell(f"git fetch internal {inter_name}", repo_dir, log_name, user)
        # 切换到inter_name分支，并将internal仓库的分支强制 checkout 到当前分支。
        shell(f"git checkout -B {inter_name} internal/{inter_name}", repo_dir, log_name, user)
        # 将本地仓库的inter_name分支推送到external仓库的outer_name分支上。
        shell(f"git push external {inter_name}:{outer_name}", repo_dir, log_name, user)
        # commit id
        # result = shell(f"git log HEAD~1..HEAD --oneline", repo_dir, log_name, user)
        # commit_id = result.stdout.split(" ")[0]
        result = shell(f'git log -1 --format="%H"', repo_dir, log_name, user)
        commit_id = result.stdout[0:7]
        sync_log(LogType.INFO, f'[COMMIT ID: {commit_id}]', log_name, user)
        return commit_id
    except Exception as e:
        raise


def outer_to_inter(repo, branch, log_name: str, user: str):
    repo_dir = os.path.join(SYNC_DIR, repo.repo_name)
    inter_name = branch.internal_branch_name
    outer_name = branch.external_branch_name
    try:
        # 从external仓库的指定分支outer_name中获取代码，更新远程分支的信息到本地仓库
        shell(f"git fetch external {outer_name}", repo_dir, log_name, user)
        # 切换到本地仓库的outer_name分支，并将origin仓库的outer_name分支强制 checkout 到当前分支。
        shell(f"git checkout -B {outer_name} external/{outer_name}", repo_dir, log_name, user)
        # 将本地仓库的outer_name分支推送到internal仓库的inter_name分支上。
        shell(f"git push internal {outer_name}:{inter_name}", repo_dir, log_name, user)
        # commit id
        # result = shell(f"git log HEAD~1..HEAD --oneline", repo_dir, log_name, user)
        # commit_id = result.stdout.split(" ")[0]
        result = shell(f'git log -1 --format=%h', repo_dir, log_name, user)
        commit_id = result.stdout[0:7]
        sync_log(LogType.INFO, f'[COMMIT ID: {commit_id}]', log_name, user)
        return commit_id
    except Exception as e:
        raise


async def sync_repo_task(repo, user):
    if repo.sync_granularity == SyncType.one:
        branches = await sync_branch_dao.sync_branch(repo_id=repo.id)
        await sync_branch_task(repo, branches, repo.sync_direction, user)
    else:
        log_name = f'sync_{repo.repo_name}.log'
        init_repos(repo, log_name, user)
        sync_log(LogType.INFO, f'************ 执行{repo.repo_name}仓库同步 ************', log_name, user)
        try:
            if repo.sync_direction == SyncDirect.to_outer:
                inter_repo_addr = get_repo_address_with_token(repo.internal_repo_address, repo.inter_token)
                stm = shell(f"git ls-remote --heads {inter_repo_addr}", SYNC_DIR, log_name, user)
                branch_list_output = stm.stdout.split('\n')
                for branch in branch_list_output:
                    if branch:
                        branch_name = branch.split('/')[-1].strip()
                        branch = SyncBranchDTO(enable=1, internal_branch_name=branch_name, external_branch_name=branch_name)
                        sync_log(LogType.INFO, f'Execute inter to outer {branch_name} branch Sync', log_name, user)
                        inter_to_outer(repo, branch, log_name, user)
            else:
                exter_repo_addr = get_repo_address_with_token(repo.external_repo_address, repo.exter_token)
                stm = shell(f"git ls-remote --heads {exter_repo_addr}", SYNC_DIR, log_name, user)
                branch_list_output = stm.stdout.split('\n')
                for branch in branch_list_output:
                    if branch:
                        branch_name = branch.split('/')[-1].strip()
                        branch = SyncBranchDTO(enable=1, internal_branch_name=branch_name, external_branch_name=branch_name)
                        sync_log(LogType.INFO, f'Execute outer to inter {branch_name} branch Sync', log_name, user)
                        outer_to_inter(repo, branch, log_name, user)
            sync_log(LogType.INFO, f'************ {repo.repo_name}仓库同步完成 ************', log_name, user)
        finally:
            if config.DELETE_SYNC_DIR:
                os.path.exists(SYNC_DIR) and os.removedirs(SYNC_DIR)
                sync_log(LogType.INFO, f'删除同步工作目录: {SYNC_DIR}', log_name, user)

            await log_service.insert_repo_log(repo_name=repo.repo_name, direct=repo.sync_direction)
            os.remove(os.path.join(log_path, log_name))


async def sync_branch_task(repo, branches, direct, user):

    for branch in branches:
        log_name = f'sync_{repo.repo_name}_{branch.id}.log'
        init_repos(repo, log_name, user)
        sync_log(LogType.INFO, f'************ 执行分支同步 ************', log_name, user)
        commit_id = ''
        try:
            if direct == SyncDirect.to_inter:
                sync_log(LogType.INFO, f'Execute outer to inter {branch.external_branch_name} branch Sync', log_name, user)
                commit_id = outer_to_inter(repo, branch, log_name, user)
            else:
                sync_log(LogType.INFO, f'Execute inter to outer {branch.internal_branch_name} branch Sync', log_name, user)
                commit_id = inter_to_outer(repo, branch, log_name, user)
            sync_log(LogType.INFO, f'************ 分支同步完成 ************', log_name, user)
        finally:
            if config.DELETE_SYNC_DIR:
                os.path.exists(SYNC_DIR) and os.removedirs(SYNC_DIR)
                sync_log(LogType.INFO, f'删除同步工作目录: {SYNC_DIR}', log_name, user)

            await log_service.insert_branch_log(repo.repo_name, direct, branch.id, commit_id)
            os.remove(os.path.join(log_path, log_name))


async def modify_repos(repo_name, user: str):
    repo = await sync_repo_dao.get(repo_name=repo_name)
    not os.path.exists(SYNC_DIR) and os.makedirs(SYNC_DIR)
    repo_dir = os.path.join(SYNC_DIR, repo.repo_name)
    log_name = f'update_{repo.repo_name}.log'
    if os.path.exists(repo_dir):
        inter_repo_addr = get_repo_address_with_token(repo.internal_repo_address, repo.inter_token)
        exter_repo_addr = get_repo_address_with_token(repo.external_repo_address, repo.exter_token)
        # 更新internal远程仓库
        shell(f'git remote set-url internal {inter_repo_addr}', repo_dir, log_name, user)
        # 更新external远程仓库
        shell(f'git remote set-url external {exter_repo_addr}', repo_dir, log_name, user)
