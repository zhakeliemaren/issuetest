from typing import Optional
from src.dto.account import GithubAccount
from src.service.account import GithubAccountService


def get_author_domain(aliemail: str):
    # for example ali email
    if aliemail == "":
        return None
    domain = aliemail.split("@", 1)[0]
    return domain


async def get_github_author_and_email(domain: str) -> Optional[GithubAccount]:
    service = GithubAccountService()
    ans = await service.get_github_account_by_domain(domain)
    if ans is None:
        # return the author short name and oceanbase.com eamil
        return {
            'author': 'obdev',
            'email': 'obdev'
        }
    else:
        return {
            'author': ans.account,
            'email': ans.email
        }
