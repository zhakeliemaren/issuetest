class Repo(object):

    def __init__(self, project, organization, name):
        self.project = project
        self.organization = organization
        self.name = name


class RepoType:
    Github = 'GitHub'
    Gitee = 'Gitee'
    Gitlab = 'Gitlab'
    Gitcode = 'Gitcode'
    Gitlink = 'Gitlink'
