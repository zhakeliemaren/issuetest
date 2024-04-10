import re

gitcode_http_partten = r'https://gitcode.net/(.*)/(.*)'
gitcode_ssh_partten = r'git@gitcode.net:(.*)/(.*).git'


def check_gitcode_address(address: str) -> bool:
    try:
        if address.startswith('https'):
            partten = gitcode_http_partten
        else:
            partten = gitcode_ssh_partten
        matchObj = re.match(partten, address, re.M | re.I)
        if matchObj:
            return True
        else:
            return False
    except:
        return False


def gitcode_auth(token: str) -> bool:
    pass


def get_gitcode_address_with_token(http_address: str, token: str) -> str:
    pass
