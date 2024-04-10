import re
from src.common import crawler

github_http_partten = r'https://github.com/(.*)/(.*)'
github_ssh_partten = r'git@github.com:(.*)/(.*).git'


def transfer_github_to_name(address: str):
    try:
        if address.startswith('https'):
            partten = github_http_partten
        else:
            partten = github_ssh_partten
        matchObj = re.match(partten, address, re.M | re.I)
        if matchObj:
            organization = matchObj.group(1)
            repo = matchObj.group(2)
            return organization, repo
        else:
            return None, None
    except:
        return None, None


def check_github_address(address: str) -> bool:
    try:
        if address.startswith('https'):
            partten = github_http_partten
        else:
            partten = github_ssh_partten
        matchObj = re.match(partten, address, re.M | re.I)
        if matchObj:
            return True
        else:
            return False
    except:
        return False


def github_auth(token: str) -> bool:
    if token is None:
        return False

    url = "https://api.github.com/user"

    header = {
        'Authorization': 'token ' + token}
    resp = crawler.Fetch(url, header=header, way='Get')

    if "message" in resp.keys():
        return False
    else:
        return True


def get_github_address_with_token(http_address: str, token: str) -> str:
    try:
        if not http_address.startswith('http'):
            raise Exception('http address is error')
        if token == "":
            raise Exception('token is empty')
        owner_name = http_address[8:].split("/")[1]
        return http_address[:8] + owner_name + ":" + token + '@' + http_address[8:]
    except Exception as e:
        print(e)
