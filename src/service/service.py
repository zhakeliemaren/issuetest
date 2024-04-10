# coding: utf-8
from typing import Union


class Service(object):

    @staticmethod
    def formate_string(s: Union[bytes, str]) -> str:
        return s.decode(errors='replace') if isinstance(s, bytes) else s
