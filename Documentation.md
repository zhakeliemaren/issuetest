### 依赖

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

### 如何安装

> [!NOTE]
> 运行代码必须在python 3.9环境下面

`pip3 install -r requirement.txt`

### 部署数据库

- 创建一个自己的database
- 仓库目录下的 sql/20240408.sql 文件已列出需要在数据库中创建的表结构
- 设置自己的数据库连接串在src/base/config.py文件内
DB 变量的 ‘test_env’配置数据库参数

`'host': 数据库服务器的主机名或IP地址。可以通过环境变量 'CEROBOT_MYSQL_HOST' 获取其值，也可以自己设置。`

`'port': 数据库服务器的端口号。可以通过环境变量 'CEROBOT_MYSQL_PORT' 获取其值， 默认端口号‘2883’。`

`'user': 连接数据库的用户名。可以通过环境变量 'CEROBOT_MYSQL_USER' 获取其值，也可以自己设置。`

`'passwd': 连接数据库的密码。可以通过环境变量 'CEROBOT_MYSQL_PWD' 获取其值，也可以自己设置。`

`'dbname': 要连接的数据库的名称。可以通过环境变量 'CEROBOT_MYSQL_DB' 获取其值，也可以自己设置。`


## 启动服务

- python3 main.py
- 服务启动成功后查看API文档 [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)
- 历史日志文件记录在本地的 logs 目录下

## 环境变量说明
```python
# 同步任务执行完成后是否删除同步目录的环境变量
DELETE_SYNC_DIR = ('DELETE_SYNC_DIR', False)
# 是否在日志中详细记录git执行错误信息的环境变量
LOG_DETAIL = ('LOG_DETAIL', True)
# 设置同步目录的环境变量
SYNC_DIR = ("SYNC_DIR", "/tmp/sync_dir/")
```