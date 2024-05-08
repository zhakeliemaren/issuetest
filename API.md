## 环境变量
```python
# 同步任务执行完成后，是否删除同步目录
DELETE_SYNC_DIR = getenv('DELETE_SYNC_DIR', False)
# 是否在日志中详细记录git执行错误时的信息
LOG_DETAIL = getenv('LOG_DETAIL', True)
# 同步目录环境变量
SYNC_DIR = os.getenv("SYNC_DIR", "/tmp/sync_dir/")
```

## 仓库绑定
允许用户通过此接口绑定仓库信息。

- **URL**：`/cerobot/sync/repo`
- **Method**：`POST`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必填 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |
| enable | bool | true/false | yes | 同步状态 |
| internal_repo_address | string |  | yes | 内部仓库地址 |
| external_repo_address | string |  | yes | 外部仓库地址 |
| sync_granularity | enum('all', 'one') | 1 为仓库粒度的同步<br />2 为分支粒度的同步 | yes | 同步粒度 |
| sync_direction | enum('to_outer', 'to_inter') | 1 表示内部仓库同步到外部<br />2 表示外部仓库同步到内部 | yes | 同步方向 |

### 请求示例
```json
{
  "enable": true,
  "repo_name": "ob-robot-test",
  "internal_repo_address": "",
  "external_repo_address": "",
  "sync_granularity": 2,
  "sync_direction": 1
}
```
## 分支绑定
允许用户通过此接口在对应仓库上绑定分支。

- **URL**：`/cerobot/sync/{repo_name}/branch`
- **Method**：`POST`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |
| enable | bool | true/false | yes | 同步状态 |
| internal_branch_name | string |  | yes | 内部分支名称 |
| external_branch_name | string |  | yes | 外部分支名称 |

### 请求示例
```json
"repo_name": "ob-robot-test"
{
  "enable": true,
  "internal_branch_name": "test",
  "external_branch_name": "test"
}
```
## 仓库粒度同步
允许用户通过此接口执行单个仓库同步。

- **URL**：`/cerobot/sync/repo/{repo_name}`
- **Method**：`POST`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |

### 成功响应
**条件**：同步执行成功。<br />**状态码：**`0 操作成功`<br />**响应示例**：
```json
{
  "code_status": 0,
  "data": null,
  "msg": "操作成功"
}
```
### 错误响应
**条件**：同步执行未成功。<br />**状态码：**`2xxxx 表示git异常错误`<br />**响应示例**：
```json
{
  "code_status": 20009,
  "data": null,
  "msg": "分支不存在"
}
```
## 分支粒度同步
允许用户通过此接口执行单个分支同步。

- **URL**：`/cerobot/sync/{repo_name}/branch/{branch_name}`
- **Method**：`POST`
### 请求参数（body）
| 参数          | 类型 | 示例输入 | 是否必须 | 说明    |
|-------------| --- | --- | --- |-------|
| repo_name   | string |  | yes | 仓库名称  |
| sync_direct | int | 1/2 | yes | 同步方向:<br/>1 表示内部仓库同步到外部<br />2 表示外部仓库同步到内部 |
| branch_name | string |  | yes | 分支名称  |

注: 仓库由内到外同步时，分支输入内部仓库分支名；仓库由外到内同步时，分支输入外部仓库分支名；
### 成功响应
**条件**：同步执行成功。<br />**状态码：**`0 操作成功`<br />**响应示例**：
```json
{
  "code_status": 0,
  "data": null,
  "msg": "操作成功"
}
```
### 错误响应
**条件**：同步执行未成功。<br />**状态码：**`2xxxx 表示git异常错误`<br />**响应示例**：
```json
{
  "code_status": 20009,
  "data": null,
  "msg": "分支不存在"
}
```
## 获取仓库信息
允许用户通过此接口分页获取仓库信息。

- **URL**：`/cerobot/sync/repo`
- **Method**：`GET`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| page_num | int |  | no | 页数 |
| page_size | int |  | no | 条数 |
| create_sort | bool |  | no | 创建时间排序， 默认倒序 |

## 获取分支信息
允许用户通过此接口分页获取仓库信息。

- **URL**：`/cerobot/sync/{repo_name}/branch`
- **Method**：`GET`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |
| page_num | int |  | no | 页数 |
| page_size | int |  | no | 条数 |
| create_sort | bool |  | no | 创建时间排序， 默认倒序 |

## 仓库解绑
允许用户通过此接口解绑对应仓库信息，该仓库下的分支也全部解绑。

- **URL**：`/cerobot/sync/repo/{repo_name}`
- **Method**：`DELETE`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |

## 分支解绑
允许用户通过此接口解绑对应仓库的分支信息。

- **URL**：`/cerobot/sync/{repo_name}/branch/{branch_name}`
- **Method**：`DELETE`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |
| branch_name | string | <br /> | yes | 分支名称 |

注: 仓库由内到外同步时，分支输入内部仓库分支名；仓库由外到内同步时，分支输入外部仓库分支名；
## 仓库同步状态更新
允许用户通过此接口更新仓库的同步状态。

- **URL**：`/cerobot/sync/repo/{repo_name}`
- **Method**：`PUT`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |
| enable | bool | true/false | yes | 分支名称 |

## 分支同步状态更新
允许用户通过此接口更新对应仓库的分支同步状态。

- **URL**：`/cerobot/sync/{repo_name}/branch/{branch_name}`
- **Method**：`PUT`
### 请求参数（body）
| 参数 | 类型 | 示例输入 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| repo_name | string |  | yes | 仓库名称 |
| branch_name | string |  | yes | 分支名称 |
| enable | bool | true/false | yes | 分支名称 |

注: 仓库由内到外同步时，分支输入内部仓库分支名；仓库由外到内同步时，分支输入外部仓库分支名；

## 日志信息获取
允许用户通过此接口分页、使用多个分支ID，获取仓库/分支的同步日志。

- **URL**：`/cerobot/sync/repo/{repo_name}/logs`
- **Method**：`GET`
### 请求参数（body）
| 参数           | 类型     | 示例输入    | 是否必须 | 说明 |
|--------------|--------|---------|------| --- |
| repo_name    | string |         | yes  | 仓库名称 |
| branch_id    | string | 1,2,3   | no   | 分支id |
| page_num     | int    | 默认1     | no   | 页数 |
| page_size    | int    | 默认10    | no   | 条数   |
| create_sort  | bool   | 默认False | no   |创建时间排序， 默认倒序|

注: 获取仓库粒度的同步日志时无需输入分支id；
