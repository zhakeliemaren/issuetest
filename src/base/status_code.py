from enum import Enum, unique
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, Dict, Any

Data = TypeVar('Data')


@unique
class Status(Enum):
    # 成功返回
    SUCCESS = (0, "操作成功")
    # 请求异常
    REPO_ADDR_ILLEGAL = (10001, "仓库地址格式有误，请检查")
    REPO_EXISTS = (10002, "仓库已存在，请勿重复创建。如果同步方向不同，请更换易识别名称再次创建")
    BRANCH_EXISTS = (10003, "分支已存在，请勿重复绑定")
    GRANULARITY_ERROR = (10004, "仓库粒度同步，无需添加分支信息")
    NOT_FOUND = (10005, "分支信息获取为空")
    NOT_ENABLE = (10006, "仓库/分支未启用同步，请检查更新同步启用状态")
    SYNC_GRAN_ILLEGAL = (10007, "sync_granularity: 1 表示仓库粒度的同步, 2 表示分支粒度的同步")
    SYNC_DIRE_ILLEGAL = (10008, "sync_direction: 1 表示内部仓库同步到外部, 2 表示外部仓库同步到内部")
    REPO_NULL = (10009, "仓库未绑定，请先绑定仓库，再绑定分支")
    REPO_NOTFOUND = (10010, "未查找到仓库")
    GRANULARITY_DELETE = (10011, "仓库粒度同步，没有分支可解绑")
    BRANCH_DELETE = (10012, "仓库中不存在此分支")
    NOT_DATA = (10013, "没有数据")
    GRANULARITY = (10014, "仓库粒度同步，没有分支信息")
    # git执行异常
    PERMISSION_DENIED = (20001, "SSH 密钥未授权或未添加")
    REPO_NOT_FOUND = (20002, "仓库不存在或私有仓库访问权限不足")
    RESOLVE_HOST_FAIL = (20003, "无法解析主机")
    CONNECT_TIME_OUT = (20004, "连接超时")
    AUTH_FAIL = (20005, "认证失败 (用户名和密码、个人访问令牌、SSH 密钥等)")
    CREATE_WORK_TREE_FAIL = (20006, "没有权限在指定的本地目录创建文件或目录")
    DIRECTORY_EXIST = (20007, "本地目录冲突 (本地已存在同名目录，无法创建新的工作树目录)")
    NOT_REPO = (20008, "当前的工作目录不是一个git仓库")
    NOT_BRANCH = (20009, "分支不存在")
    PUST_REJECT = (20010, "推送冲突")
    REFUSE_PUST = (20011, "推送到受保护的分支被拒绝")
    UNKNOWN_ERROR = (20012, "Unknown git error.")

    @property
    def code(self) -> int:
        # 返回状态码信息
        return self.value[0]

    @property
    def msg(self) -> str:
        # 返回状态码说明信息
        return self.value[1]


git_error_mapping = {
    "Permission denied": Status.PERMISSION_DENIED,
    "Repository not found": Status.REPO_NOT_FOUND,
    "not a git repository": Status.REPO_NOT_FOUND,
    "Could not resolve host": Status.RESOLVE_HOST_FAIL,
    "Connection timed out": Status.CONNECT_TIME_OUT,
    "Could not read from remote repository.": Status.REPO_NOT_FOUND,
    "Authentication failed": Status.AUTH_FAIL,
    "could not create work tree": Status.CREATE_WORK_TREE_FAIL,
    "already exists and is not an empty directory": Status.DIRECTORY_EXIST,
    "The current directory is not a git repository": Status.NOT_REPO,
    "couldn't find remote ref": Status.NOT_BRANCH,
    "is not a commit and a branch": Status.NOT_BRANCH,
    "[rejected]": Status.PUST_REJECT,
    "refusing to update": Status.REFUSE_PUST
}


class SYNCException(Exception):
    def __init__(self, status: Status):
        self.code_status = status.code
        self.status_msg = status.msg


class SYNCResponse(BaseModel):
    code_status: Optional[int] = 0
    data: Optional[Data] = None
    msg: Optional[str] = ''


class GITMSGException(Exception):
    def __init__(self, status: Status, repo='', branch=''):
        self.status = status.code
        self.msg = status.msg

# class SYNCResponse(GenericModel, Generic[Data]):
#     code_status: int = 200
#     data: Optional[Data] = None
#     msg: str = ''
#     success: bool = True
#     finished: bool = True

