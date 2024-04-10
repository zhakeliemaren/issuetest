import re
import requests
from typing import Optional
from src.base import config
from src.utils.logger import logger

# TODO
gitlab_http_partten = r''
gitlab_ssh_partten = r''

antcode_http_partten = r''
antcode_ssh_partten = r''

gitlab_api_address = config.GITLAB_ENV['gitlab_api_address']
token = config.ACCOUNT['gitlab_token']


def get_inter_repo_type(address: str) -> Optional[str]:
    if address.startswith('http://gitlab') or address.startswith('git@gitlab'):
        return 'gitlab'
    elif address.startswith('https://code') or address.startswith('git@code'):
        return 'antcode'
    else:
        return None


def get_organization_and_name_from_url(url: str):
    try:
        if url.startswith('http://gitlab'):
            partten = gitlab_http_partten
        elif url.startswith('git@gitlab'):
            partten = gitlab_ssh_partten
        elif url.startswith('https://code'):
            partten = antcode_http_partten
        elif url.startswith('git@code'):
            partten = antcode_ssh_partten
        else:
            partten = None
        if partten is not None:
            matchObj = re.match(partten, url, re.M | re.I)
            if matchObj:
                organization = matchObj.group(1)
                repo = matchObj.group(2)
                return organization, repo
        else:
            return None, None
    except:
        return None, None


def check_gitlab_address(url: str) -> bool:
    try:
        if url.startswith('http://gitlab'):
            partten = gitlab_http_partten
        elif url.startswith('git@gitlab'):
            partten = gitlab_ssh_partten
        elif url.startswith('https://code'):
            partten = antcode_http_partten
        elif url.startswith('git@code'):
            partten = antcode_ssh_partten
        else:
            partten = None
        if partten is not None:
            matchObj = re.match(partten, url, re.M | re.I)
            if matchObj:
                return True
        else:
            return False
    except:
        return False


def get_repo_id_from_url(url: str) -> Optional[int]:
    if url == "":
        return None

    organization, repo = get_organization_and_name_from_url(url)
    if organization is None or repo is None:
        logger.info("The url has no organization or repo")
        return None
    logger.info(f"The url's organization is {organization}")
    logger.info(f"The url's repo is {repo}")
    expect_namespace = organization + " / " + repo

    param = {
        'private_token': token,
        'url': url
    }
    response = requests.get(url=gitlab_api_address, params=param).json()
    if response is None or len(response) == 0:
        logger.info("There is no data from the gitlab request")
        return None
    for repo_info in response:
        if repo_info['name_with_namespace'] == expect_namespace:
            return repo_info['id']
    return None


def get_gitlab_address_with_token(http_address: str, token: str) -> str:
    pass
