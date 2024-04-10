# coding: utf-8
import os
from extras.obfastapi.config import ConfigsUtil, MysqlConfig, RedisConfig


def getenv(key, default=None, _type=None):
    value = os.getenv(key)
    if value:
        if _type == bool:
            return value.lower() == 'true'
        else:
            return _type(value) if _type else value
    else:
        return default


LOCAL_ENV = 'LOCAL'
DEV_ENV = 'DEV'
PORD_ENV = 'PROD'

SYS_ENV = getenv('SYS_ENV', LOCAL_ENV)
LOG_PATH = getenv('LOG_PATH')
LOG_LEVEL = getenv('LOG_LV', 'DEBUG')
LOG_SAVE = getenv('LOG_SAVE', True)

DELETE_SYNC_DIR = getenv('DELETE_SYNC_DIR', False)
LOG_DETAIL = getenv('LOG_DETAIL', True)
SYNC_DIR = os.getenv("SYNC_DIR", "/tmp/sync_dir/")

buc_key = getenv('BUC_KEY', "OBRDE_DEV_USER_SIGN")
buc_key and ConfigsUtil.set_obfastapi_config('buc_key', buc_key)

DB_ENV = getenv('DB_ENV', 'test_env')
DB = {
    'test_env': {
        'host': getenv('CEROBOT_MYSQL_HOST', ''),
        'port': getenv('CEROBOT_MYSQL_PORT', 2883, int),
        'user': getenv('CEROBOT_MYSQL_USER', ''),
        'passwd': getenv('CEROBOT_MYSQL_PWD', ''),
        'dbname': getenv('CEROBOT_MYSQL_DB', '')
    },
    'local': {
        'host': getenv('CEROBOT_MYSQL_HOST', ''),
        'port': getenv('CEROBOT_MYSQL_PORT', 2881, int),
        'user': getenv('CEROBOT_MYSQL_USER', ''),
        'passwd': getenv('CEROBOT_MYSQL_PWD', ''),
        'dbname': getenv('CEROBOT_MYSQL_DB', '')
    }
}

for key in DB:
    conf = MysqlConfig(**DB[key])
    ConfigsUtil.set_mysql_config(key, conf)

SERVER_HOST = getenv('SERVER_HOST', '')

TOKEN_KEY = int(getenv("TOKEN_KEY", 1))

ACCOUNT = {
    'username': getenv('OB_ROBOT_USERNAME', ''),
    'email': getenv('OB_ROBOT_USERNAME', ''),
    'github_token': getenv('GITHUB_TOKEN', ''),
    'gitee_token': getenv('GITEE_TOKEN', ''),
    'gitlab_token': getenv('GITLAB_TOKEN', ''),  # 暂时还是我的token，待替代为一个内部账号
    'antcode_token': getenv('ANTCODE_TOKEN', ''),  # 暂时还是我的token，待替代为一个内部账号
    'gitcode_token': getenv('GITCODE_TOKEN', ''),  # 暂时还是我的token，待替代为ob-robot账号
    'robot_code_token': getenv('ROBOT_CODE_TOKEN', ''),
    'robot_antcode_token': getenv('ROBOT_ANTCODE_TOKEN', '')
}

GITLAB_ENV = {
    'gitlab_api_address': getenv('GITLAB_API_HOST', ''),
    'gitlab_api_pullrequest_address': getenv('GITLAB_API_PULLREQUEST_HOST', '')
}

GITHUB_ENV = {
    'github_api_address': getenv('GITHUB_API_HOST', ''),
    'github_api_diff_address': getenv('GITHUB_API_DIFF_HOST', ''),
}

GITEE_ENV = {
    'gitee_api_address': getenv('GITEE_API_HOST', 'https://api.gitee.com/repos'),
    'gitee_api_diff_address': getenv('GITEE_API_DIFF_HOST', 'https://gitee.com'),
}

GITLINK_ENV = {
    'gitlink_api_address': getenv('GITLINK_API_HOST', ''),
    'gitlink_api_diff_address': getenv('GITLINK_API_DIFF_HOST', ''),
}

GITCODE_ENV = {
    'gitcode_api_address': getenv('GITCODE_API_HOST', ''),
    'gitcode_api_diff_address': getenv('GITCODE_API_DIFF_HOST', ''),
}

DOCKER_ENV = {
    'el7': getenv('EL7_DOCKER_IMAGE'),
    'el8': getenv('EL8_DOCKER_IMAGE')
}

ERROR_REPORT_EMAIL = getenv('EORROR_TO', '')
DEFAULT_DK_RECEIVERS = getenv('DF_DK_TO', '')
DEFAULT_EMAIL_RECEIVERS = getenv('DF_EMAIL_TO', '')

NOTIFY = {
    # todo yaml当中配置新的生产环境host
    'host': getenv('NOTIFY_HOST', ''),
    'user': getenv('NOTIFY_USER', ''),  # 一般当前项目的项目名
    'report_sender': getenv('NOTIFY_REPORT_SENDER', ''),
    'email_sender': getenv('EMAIL_NOTIFY_SENDER'),
    'dk_sender': getenv('DK_NOTIFY_SENDER', ''),
    'dd_sender': getenv('DD_NOTIFY_SENDER', ''),
    'dd_sender_issue': getenv('DD_NOTIFY_SENDER_ISSUE', ''),
    'dd_sender_log': getenv('DD_NOTIFY_SENDER_LOG', ''),
    'dd_sender_ghpr': getenv('DD_NOTIFY_SENDER_PR', ''),
}

# log level
ConfigsUtil.set_obfastapi_config('log_level', 'WARN')
# ConfigsUtil.set_obfastapi_config('log_name', 'mysql_test')
# ConfigsUtil.set_obfastapi_config('log_path', 'test.log')

SECRET_SCAN = getenv('SECRET_SCAN', True)

# Symmetric encryption key
DATA_ENCRYPT_KEY = getenv('DATA_ENCRYPT_KEY', '')

# web base_url
base_url = getenv('OB_ROBOT_BASE_URL', '')

CACHE_DB = {
    "cerobot": {
        "host": getenv("CEROBOT_REDIS_HOST", ""),
        "port": getenv("CEROBOT_REDIS_PORT", 6379, int),
        "password": getenv("CEROBOT_REDIS_PWD", "")
    }
}
for key in CACHE_DB:
    conf = RedisConfig(**CACHE_DB[key])
    ConfigsUtil.set_redis_config(key, conf)

GIT_DEPTH = getenv('GIT_DEPTH', 100, int)

SECRET_SCAN_THREAD = getenv('SECRET_SCAN_THREAD', 4, int)
OCEANBASE = getenv('OCEANBASE', 'ob-mirror')
OBProjectIdInAone = getenv('OB_PROJECT_ID_AONE', 2015510, int)
strip_name = getenv("STRIP_NAME", "/.ce")

# observer repo cache
OCEANBASE_REPO_BASE_DIR = getenv('OCEANBASE_REPO_BASE_DIR', '')
# oceanbase internal repo, create github feature branch
OCEANBASE_REPO = getenv('OCEANBASE_REPO', '')
# oceanbase ce publish repo, the ob backup repo
# it need origin(oceanbase-ce-publish oceanbase) and github(github oceanbase) git configration
OCEANBASE_BACKUP_REPO = getenv('OCEANBASE_BACKUP_REPO', '')
# github repo
OCEANBASE_GITHUB_REPO = getenv('OCEANBASE_GITHUB_REPO', '')

ROLE_CHECK = getenv('ROLE_CHECK', True, bool)

# oss config
OSS_CONFIG = {
    "id": getenv("OSSIV", ""),
    "secret": getenv("OSSKEY", ""),
    "bucket": getenv("OSSBUCKET", ""),
    "endpoint": getenv("OSSENDPOINT", ""),
    "download_base": getenv("DOWNLOAD_BASE", "")
}
