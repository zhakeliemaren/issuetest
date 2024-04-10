from src.common.github import Github
from src.common.github import PullRequest as GithubPullRequest
from src.common.gitee import Gitee, PullRequest as GiteePullRequest
from src.common.gitcode import Gitcode, PullRequest as GitcodePullRequest
from src.common.gitlink import Gitlink, PullRequest as GitlinkPullRequest


class RepoFactory(object):
    @staticmethod
    def create(type, project: str, organization: str, name: str):
        if type == 'Github':
            return Github(project, organization, name)
        elif type == 'Gitee':
            return Gitee(project, organization, name)
        elif type == 'Gitcode':
            return Gitcode(project, organization, name)
        elif type == 'Gitlink':
            return Gitlink(project, organization, name)
        else:
            return None


class PullRequestFactory(object):
    @staticmethod
    def create(type: str, organization: str, name: str, id: int):
        if type == 'Github':
            return GithubPullRequest(organization, name, id)
        elif type == 'Gitee':
            return GiteePullRequest(organization, name, id)
        elif type == 'Gitcode':
            return GitcodePullRequest(organization, name, id)
        elif type == 'Gitlink':
            return GitlinkPullRequest(organization, name, id)
        else:
            return None
