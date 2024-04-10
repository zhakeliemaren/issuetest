import re
import requests
from typing import Optional
from src.base import config
from src.utils.logger import logger

gitee_http_partten = r'https://gitee.com/(.*)/(.*)'
gitee_ssh_partten = r'git@gitee.com:(.*)/(.*).git'


def check_gitee_address(address: str) -> bool:
    try:
        if address.startswith('https'):
            partten = gitee_http_partten
        else:
            partten = gitee_ssh_partten
        matchObj = re.match(partten, address, re.M | re.I)
        if matchObj:
            return True
        else:
            return False
    except:
        return False


def gitee_auth(token: str) -> bool:
    pass


def get_gitee_address_with_token(http_address: str, token: str) -> str:
    try:
        if not http_address.startswith('http'):
            raise Exception('http address is error')
        if token == "":
            raise Exception('token is empty')
        owner_name = http_address[8:].split("/")[1]
        return http_address[:8] + owner_name + ":" + token + '@' + http_address[8:]
    except Exception as e:
        print(e)
