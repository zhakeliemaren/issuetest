from fastapi.datastructures import Default
from pydantic import BaseModel
from fastapi import Body


class Account(BaseModel):
    id: int
    domain: str
    nickname: str


class GithubAccount(Account):
    account: str
    email: str


class GiteeAccount(Account):
    account: str
    email: str


class CreateAccountItem(BaseModel):
    domain: str
    nickname: str
    account: str
    email: str


class UpdateAccountItem(CreateAccountItem):
    id: int
