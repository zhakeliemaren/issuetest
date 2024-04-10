from fastapi.datastructures import Default
from pydantic import BaseModel
from src.common.repo import RepoType


class PullRequest(BaseModel):
    id: int
    title: str
    project: str
    type: str
    address: str
    author: str
    email: str
    target_branch: str
    latest_commit: str


class GithubPullRequest(PullRequest):
    type = RepoType.Github


class GiteePullRequest(PullRequest):
    type = RepoType.Gitee


class GitlabPullRequest(PullRequest):
    type = RepoType.Gitlab


class GitcodePullRequest(PullRequest):
    type = RepoType.Gitcode
