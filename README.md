# ob-repository-synchronize

## Description

ob-repository-synchronize is a small tool which can help engineer to master their open source production's code synchronization between GitHub, Gitee, CodeChina, internal repository and so on.

## Principle

### Base on git rebase

<img src="doc/rebase.png" width="500" height="400">

### Base on git diff

<img src="doc/diff.png" width="500" height="400">

## backend

### requirement

name|version|necessity
--|:--:|--:
python|3.9|True
uvicorn|0.14.0|True
SQLAlchemy|1.4.21|True
fastapi|0.66.0|True
aiohttp|3.7.4|True
pydantic|1.8.2|True
starlette|0.14.2|True
aiomysql|0.0.21|True
requests|2.25.1|True
loguru|0.6.0|True
typing-extensions|4.1.1|True
aiofiles|0.8.0|True

### how to install

> [!NOTE]
> Run the code in python 3.9

`pip3 install -r requirement.txt`

`python3 main.py`

### run the sync script locally

`python3 sync.py`

## frontend

[Refer the web readme](web/README.md)

## docker

`docker pull XXX:latest`

`docker run -p 8000:8000 -d XXX bash start.sh -s backend`

## How to use it

1. Config your database

- Run the table.sql script in sql folder
- Config the database connection string in src/base/config.py

2. Config your repo address, branch, (todo token) by website

<img src="doc/website.png" width="500" height="400">

3. DIY yourself sync script (Refer the two example in sync folder) and run the sync script under a cronjob
you should consider:

- http address or ssh address (how to add your ssh key)
- rebase logic or diff logic
- which cronjob (maybe the k8s cronjob or linux system crontab)
