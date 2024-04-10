## clone 仓库

- pip3 install -r requirement.txt

## 部署数据库

- 创建一个自己的database
- 仓库目录下的 sql/20240408.sql 文件已列出需要在数据库中创建的表结构
- 设置自己的数据库连接串在src/base/config.py文件内，DB 变量的 'test_env'

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