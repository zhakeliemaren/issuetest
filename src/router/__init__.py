from extras.obfastapi.frame import OBAPIRouter

__all__ = ("CE_ROBOT", "PROJECT", "JOB",
           "PULL_REQUEST", "ACCOUNT", "USER", "LOG", "AUTH", "SYNC_CONFIG")

CE_ROBOT = OBAPIRouter(prefix='/cerobot/hirobot', tags=['Robot'])
PROJECT = OBAPIRouter(prefix='/cerobot/projects', tags=['Projects'])
JOB = OBAPIRouter(prefix='/cerobot', tags=['Jobs'])
PULL_REQUEST = OBAPIRouter(prefix='/cerobot', tags=['Pullrequests'])
ACCOUNT = OBAPIRouter(prefix='/cerobot/account', tags=['Account'])
USER = OBAPIRouter(prefix="/cerobot/users", tags=["Users"])
LOG = OBAPIRouter(prefix="/cerobot/log", tags=["Log"])
AUTH = OBAPIRouter(prefix="/cerobot/auth", tags=["Auth"])
SYNC_CONFIG = OBAPIRouter(prefix='/cerobot/sync', tags=['Sync'])
