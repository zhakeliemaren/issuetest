ALTER TABLE `github_account`
MODIFY COLUMN `id` bigint unsigned AUTO_INCREMENT,
MODIFY COLUMN `domain` varchar(20) COMMENT '域账号',
MODIFY COLUMN `nickname` varchar(20) COMMENT '花名',
MODIFY COLUMN `account` varchar(50) COMMENT 'GitHub账号',
MODIFY COLUMN `email` varchar(50) COMMENT '邮箱',
MODIFY COLUMN `create_time` DATETIME COMMENT '创建时间',
MODIFY COLUMN `update_time` DATETIME COMMENT '更新时间';

ALTER TABLE `gitee_account`
MODIFY COLUMN `id` bigint unsigned AUTO_INCREMENT,
MODIFY COLUMN `domain` varchar(20) COMMENT '域账号',
MODIFY COLUMN `nickname` varchar(20) COMMENT '花名',
MODIFY COLUMN `account` varchar(20) COMMENT 'GitHub账号',
MODIFY COLUMN `email` varchar(20) COMMENT '邮箱',
MODIFY COLUMN `create_time` DATETIME COMMENT '创建时间',
MODIFY COLUMN `update_time` DATETIME COMMENT '更新时间';

ALTER TABLE `sync_project`
MODIFY COLUMN `id` bigint unsigned AUTO_INCREMENT,
MODIFY COLUMN `name` varchar(50) COMMENT '名称',
MODIFY COLUMN `github` varchar(100) COMMENT 'GitHub地址',
MODIFY COLUMN `gitee` varchar(100) COMMENT 'Gitee地址',
MODIFY COLUMN `gitlab` varchar(100) COMMENT 'Gitlab地址',
MODIFY COLUMN `code_china` varchar(100) COMMENT 'CodeChina地址',
MODIFY COLUMN `gitlink` varchar(100) COMMENT 'Gitlink地址',
MODIFY COLUMN `github_token` varchar(100) COMMENT 'GitHub token',
MODIFY COLUMN `gitee_token` varchar(100) COMMENT 'Gitee token',
MODIFY COLUMN `code_china_token` varchar(100) COMMENT 'CodeChina token',
MODIFY COLUMN `gitlink_token` varchar(100) COMMENT 'Gitlink token',
MODIFY COLUMN `create_time` DATETIME COMMENT '创建时间',
MODIFY COLUMN `update_time` DATETIME COMMENT '更新时间';

ALTER TABLE `sync_job`
MODIFY COLUMN `id` bigint unsigned AUTO_INCREMENT,
MODIFY COLUMN `project` varchar(50) COMMENT '工程名称',
MODIFY COLUMN `type` enum('OneWay','TwoWay') COMMENT '同步类型',
MODIFY COLUMN `status` tinyint(1) COMMENT '同步流状态',
MODIFY COLUMN `github_branch` varchar(50) COMMENT 'GitHub分支',
MODIFY COLUMN `gitee_branch` varchar(50) COMMENT 'Gitee分支',
MODIFY COLUMN `gitlab_branch` varchar(50) COMMENT 'Gitlab分支',
MODIFY COLUMN `code_china_branch` varchar(50) COMMENT 'CodeChina分支',
MODIFY COLUMN `gitlink_branch` varchar(50) COMMENT 'Gitlink分支',
MODIFY COLUMN `create_time` DATETIME COMMENT '创建时间',
MODIFY COLUMN `update_time` DATETIME COMMENT '更新时间',
MODIFY COLUMN `commit` varchar(50) COMMENT '最新commit';

ALTER TABLE `pull_request`
MODIFY COLUMN `id` bigint unsigned AUTO_INCREMENT,
MODIFY COLUMN `pull_request_id` bigint unsigned COMMENT 'pull request id',
MODIFY COLUMN `title` text COMMENT 'title',
MODIFY COLUMN `project` varchar(20) COMMENT '工程名称',
MODIFY COLUMN `type` enum('GitHub','Gitee','Gitlab','Gitcode','Gitlink') COMMENT '仓库类型',
MODIFY COLUMN `address` varchar(100) COMMENT 'pull request详情页地址',
MODIFY COLUMN `author` varchar(20) COMMENT '作者',
MODIFY COLUMN `email` varchar(50) COMMENT '邮箱',
MODIFY COLUMN `target_branch` varchar(50) COMMENT '目标分支',
MODIFY COLUMN `inline` tinyint(1) COMMENT '是否推送内部',
MODIFY COLUMN `latest_commit` varchar(50) COMMENT '最新的commit',
MODIFY COLUMN `create_time` DATETIME COMMENT '创建时间',
MODIFY COLUMN `update_time` DATETIME COMMENT '更新时间';

ALTER TABLE `sync_log`
MODIFY COLUMN `id` bigint unsigned AUTO_INCREMENT,
MODIFY COLUMN `sync_job_id` bigint unsigned COMMENT '同步工程id',
MODIFY COLUMN `log_type` varchar(20) COMMENT '单条日志类型',
MODIFY COLUMN `log` text COMMENT 'title',
MODIFY COLUMN `create_time` DATETIME COMMENT '创建时间';

ALTER TABLE `sync_log` add INDEX idx_sync_log_job_id(sync_job_id);
ALTER TABLE `sync_job` add INDEX idx_sync_job_project(project);