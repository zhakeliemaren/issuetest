import re
import requests
from typing import Optional
from src.base import config
from src.utils.logger import logger

gitlink_http_partten = r'https://gitlink.org.cn/(.*)/(.*)'
gitlink_ssh_partten = r'git@code.gitlink.org.cn:(.*)/(.*).git'


def check_gitlink_address(address: str) -> bool:
    try:
        if address.startswith('https'):
            partten = gitlink_http_partten
        else:
            partten = gitlink_ssh_partten
        matchObj = re.match(partten, address, re.M | re.I)
        if matchObj:
            return True
        else:
            return False
    except:
        return False


def gitlink_auth(token: str) -> bool:
    pass


def get_gitlink_address_with_token(http_address: str, token: str) -> str:
    pass