# coding: utf-8
import uvicorn

import src.api.Cerobot
import src.api.Sync
import src.api.Account
import src.api.PullRequest
import src.api.User
import src.api.Log
import src.api.Auth
import src.api.Sync_config
from extras.obfastapi.frame import OBFastAPI
from src.router import CE_ROBOT, PROJECT, JOB, ACCOUNT, PULL_REQUEST, USER, LOG, AUTH, SYNC_CONFIG
from fastapi.staticfiles import StaticFiles

app = OBFastAPI()

app.include_router(CE_ROBOT)
app.include_router(PROJECT)
app.include_router(JOB)
app.include_router(ACCOUNT)
app.include_router(PULL_REQUEST)
app.include_router(USER)
app.include_router(LOG)
app.include_router(AUTH)
app.include_router(SYNC_CONFIG)

# app.mount("/", StaticFiles(directory="web/dist"), name="static")

if __name__ == '__main__':
    # workers 参数仅在命令行使用uvicorn启动时有效 或使用环境变量 WEB_CONCURRENCY
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000,
                reload=True, debug=True, workers=2)
