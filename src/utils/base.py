import re

GIT_HTTPS_PATTERN = r'https://.*.com/(.*)/(.*).git'
GIT_HTTP_PATTERN = r'http://.*.com/(.*)/(.*).git'
GIT_SSH_PATTERN = r'git@.*.com:(.*)/(.*).git'


def check_addr(repo_address: str) -> bool:
    try:
        if repo_address.startswith('https'):
            pattern = GIT_HTTPS_PATTERN
        elif repo_address.startswith('http'):
            pattern = GIT_HTTP_PATTERN
        else:
            pattern = GIT_SSH_PATTERN
        match_obj = re.match(pattern, repo_address, re.M | re.I)
        if match_obj:
            return True
        else:
            return False
    except:
        return False


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
