from .repo import Repo
from .crawler import Fetch
from src.base import config
from src.dao.pull_request import PullRequestDAO
from src.do.pull_request import PullRequestDO
import shlex
import subprocess
from sqlalchemy import text
from src.utils.logger import logger


class Gitee(Repo):

    organization: str
    name: str
    project: str
    pull_request = []
    token = config.ACCOUNT['gitee_token']

    def __init__(self, project, organization, name):
        super().__init__(project, organization, name)

    def fetch_pull_request(self):
        url = f"{config.GITEE_ENV['gitee_api_address']}/{self.organization}/{self.name}/pulls"
        token = self.token
        qs = {
            'access_token': token}
        data = Fetch(url=url, params=qs, way='Get')

        if data is None or len(data) == 0:
            logger.info(
                f"the gitee repo {self.organization}/{self.name} has no pull request")
        else:
            for pull in data:
                pr = PullRequest(self.organization, self.name, pull['number'])
                pr.project = self.project
                pr.state = 'open'
                pr.commit_url = pull['commits_url']
                pr.inline = False
                pr.comment_url = pull['_links']['comments']
                pr.title = pull['title']
                pr.html_url = pull['html_url']
                pr.target_branch = pull['base']['ref']
                self.pull_request.append(pr)
                logger.info(f"fetch the pull request {pr.id} successfully")

    async def save_pull_request(self):
        if len(self.pull_request) == 0:
            logger.info("no pull request need to save")
            return
        for pr in self.pull_request:
            await pr.save()


class PullRequest(Gitee):

    url: str
    project: str
    html_url: str
    author: str
    review_url: str
    state: str
    commit_url: str
    inline: bool
    comment_url: str
    title: str
    target_branch: str
    latest_commit: str
    token = config.ACCOUNT['gitee_token']

    def __init__(self, organization, name: str, id: int):
        self.url = f"{config.GITEE_ENV['gitee_api_address']}/{organization}/{name}/pulls/{id}"
        self.id = id
        self.type = 'Gitee'
        self.organization = organization
        self.name = name
        self._pull_request_dao = PullRequestDAO()

    @classmethod
    def fetch_commit(self):
        qs = {
            'access_token': self.token}
        resp = Fetch(self.commit_url, params=qs, way='Get')
        self.author = resp[0]['commit']['author']['name']
        self.email = resp[0]['commit']['author']['email']

    @classmethod
    def fetch_comment_url(self):
        qs = {
            'access_token': self.token}
        resp = Fetch(self.url, params=qs, way='Get')
        self.comment_url = resp['comments_url']

    @classmethod
    def fetch_comment(self):
        self.fetch_comment_url()
        qs = {
            'access_token': self.token}
        resp = Fetch(self.comment_url, params=qs, way='Get')
        comments = []
        for item in resp:
            comments.append(item['body'])
        return comments

    def _clone(self):
        dir = "/tmp/" + self.name + "_pr" + str(self.id)
        address = f"git@gitee.com:{self.organization}/{self.name}.git"
        subprocess.run(shlex.split('mkdir ' + dir), cwd='.')
        subprocess.run(shlex.split('git clone ' + address), cwd=dir)
        return dir

    def _apply_diff(self, dir, branch: str):
        subprocess.run(shlex.split('git checkout ' + branch), cwd=dir)
        new_branch = 'pr' + str(self.id)
        subprocess.run(shlex.split('git checkout -b ' + branch), cwd=dir)
        subprocess.run(shlex.split('git apply ' + dir), cwd=dir)
        subprocess.run(shlex.split('git add .'), cwd=dir)
        subprocess.run(shlex.split(
            "git commit -m '" + self.title + "'"), cwd=dir)
        subprocess.run(shlex.split(
            'git push -uv origin' + new_branch), cwd=dir)

    def _get_diff(self, dir: str):
        filename = "/tmp/gitee_pr" + str(self.id) + "_diff"
        baseUrl = f"{config.GITEE_ENV['gitee_api_diff_address']}/{self.organization}/{self.name}/pull/"
        diffUrl = baseUrl + str(self.id) + ".diff"

        cmd = f"curl -X GET {diffUrl}"
        with open(filename, 'w') as outfile:
            subprocess.call(shlex.split(cmd), stdout=outfile)
        return filename

    def _send_merge_request(self):
        url = f"{config.GITEE_ENV['gitee_api_address']}/{self.organization}/{self.name}/issues/{self.id}/merge"
        qs = {
            'access_token': self.token}
        data = {
            "merge_method": "squash"
        }
        resp = Fetch(url, params=qs, data=data, way='Put')
        if resp is None:
            logger.error("send merge request failed")
            return False
        return True

    @classmethod
    def comment(self, comment: str):
        url = f"{config.GITEE_ENV['gitee_api_address']}/{self.organization}/{self.name}/issues/{self.id}/comments"
        qs = {
            'access_token': self.token}
        data = {"body": comment}
        resp = Fetch(url, params=qs, data=data, way='Post')
        if resp is None:
            logger.error("send comment request failed")
            return False
        return True

    @classmethod
    def approve(self):
        url = f"{config.GITEE_ENV['github_api_address']}/{self.organization}/{self.name}/issues/{self.id}/reviews"
        qs = {
            'access_token': self.token}
        data = {"body": "LGTM",
                "event": "APPROVE"}
        resp = Fetch(url, params=qs, data=data, way='Post')
        if resp is None:
            logger.error("send approve request failed")
            return False
        return True

    @classmethod
    def close(self):
        url = f"{config.GITEE_ENV['gitee_api_address']}/{self.organization}/{self.name}/pulls/{self.id}"
        qs = {
            'access_token': self.token}
        data = {"state": "closed"}
        resp = Fetch(url, params=qs, data=data, way='Patch')
        if resp is None:
            logger.error("send close pull request failed")
            return False
        return True

    @classmethod
    def get_latest_commit(self):
        url = f"{config.GITEE_ENV['gitee_api_address']}/{self.organization}/{self.name}/pulls/{self.id}/commits"
        qs = {
            'access_token': self.token}
        data = Fetch(url, params=qs, way='Get')

        if data is None or len(data) == 0:
            logger.info(
                f"the pull request {self.id} of gitee repo {self.organization}/{self.name} has no commits")
        else:
            self.latest_commit = data[0]['sha']

    @classmethod
    async def save(self):
        self.fetch_commit()
        count = await self._pull_request_dao._count(PullRequestDO, text(f"pull_request_id = '{self.id}'"))
        if count == 0:
            # insert pull request repo
            ans = await self._pull_request_dao.insert_pull_request(
                self.id, self.title, self.project, self.type, self.html_url,
                self.author, self.email, self.target_branch, "NULL")
        else:
            # update pull request repo
            await self._pull_request_dao.update_pull_request(
                self.id, self.title, self.project, self.type, self.html_url,
                self.author, self.email, self.target_branch)
            ans = True
        if not ans:
            logger.error(f"save the pull request {self.id} failed")
        else:
            logger.info(f"save the pull request {self.id} successfully")
        return

    @classmethod
    async def sync(self):
        comments = self.fetch_comment()
        if len(comments) == 0:
            logger.info(f"the gitee pull request #{self.id} has no comment")
            return
        merge = False
        cicd = False
        for comment in comments:
            if comment == '/merge':
                logger.info(
                    f"the gitee pull request #{self.id} need to merge")
                merge = True
            if comment == '/cicd':
                logger.info(f"the gitee pull request #{self.id} need to cicd")
                cicd = True
        if cicd:
            pass
        if merge:
            self.merge_to_inter()
        return

    @classmethod
    async def check_if_merge(self):
        comments = self.fetch_comment()
        if len(comments) == 0:
            logger.info(f"the gitee pull request {self.id} has no comment")
            return
        merge = False
        for comment in comments:
            if comment == '/merge':
                logger.info(f"the gitee pull request {self.id} need to merge")
                merge = True
        return merge

    @classmethod
    async def check_if_new_commit(self, origin_latest_commit: str):
        latest_commit = self.get_latest_commit()
        if latest_commit == origin_latest_commit:
            return True
        else:
            return False
