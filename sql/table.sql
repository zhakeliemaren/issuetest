CREATE TABLE `github_account` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `domain` varchar(20) NOT NULL COMMENT '域账号',
    `nickname` varchar(20) DEFAULT NULL COMMENT '花名',
    `account` varchar(50) DEFAULT NULL COMMENT 'GitHub账号',
    `email` varchar(50) DEFAULT NULL COMMENT '邮箱',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
);

CREATE TABLE `gitee_account` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `domain` varchar(20) NOT NULL COMMENT '域账号',
    `nickname` varchar(20) DEFAULT NULL COMMENT '花名',
    `account` varchar(20) DEFAULT NULL COMMENT 'GitHub账号',
    `email` varchar(20) DEFAULT NULL COMMENT '邮箱',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
);

CREATE TABLE `sync_project` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL COMMENT '名称',
    `github` varchar(100) DEFAULT NULL COMMENT 'GitHub地址',
    `gitlab` varchar(100) DEFAULT NULL COMMENT 'Gitlab地址',
    `gitee` varchar(100) DEFAULT NULL COMMENT 'Gitee地址',
    `code_china` varchar(100) DEFAULT NULL COMMENT 'CodeChina地址',
    `gitlink` varchar(100) DEFAULT NULL COMMENT 'Gitlink地址',
    `github_token` varchar(100) DEFAULT NULL COMMENT 'GitHub token',
    `gitee_token` varchar(100) DEFAULT NULL COMMENT 'Gitee token',
    `code_china_token` varchar(100) DEFAULT NULL COMMENT 'CodeChina token',
    `gitlink_token` varchar(100) DEFAULT NULL COMMENT 'Gitlink token',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
);

CREATE TABLE `sync_job` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `project` varchar(50) NOT NULL COMMENT '工程名称',
    `type` enum('OneWay','TwoWay') NOT NULL COMMENT '同步类型',
    `status` tinyint(1) NOT NULL DEFAULT FALSE COMMENT '同步流状态',
    `github_branch` varchar(50) DEFAULT NULL COMMENT 'GitHub分支',
    `gitee_branch` varchar(50) DEFAULT NULL COMMENT 'Gitee分支',
    `gitlab_branch` varchar(50) DEFAULT NULL COMMENT 'Gitlab分支',
    `code_china_branch` varchar(50) DEFAULT NULL COMMENT 'CodeChina分支',
    `gitlink_branch` varchar(50) DEFAULT NULL COMMENT 'Gitlink分支',
    `base` enum('GitHub','Gitee','Gitlab','Gitcode','Gitlink') DEFAULT NULL COMMENT '基础仓库',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    `commit` varchar(50) NOT NULL COMMENT '最新commit',
    PRIMARY KEY (`id`)
);

CREATE TABLE `pull_request` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `pull_request_id` bigint unsigned NOT NULL COMMENT 'pull request id',
    `title` text NOT NULL COMMENT 'title',
    `project` varchar(20) NOT NULL COMMENT '工程名称',
    `type` enum('GitHub','Gitee','Gitlab','Gitcode','Gitlink') NOT NULL COMMENT '仓库类型',
    `address` varchar(100) NOT NULL COMMENT 'pull request详情页地址',
    `author` varchar(20) NOT NULL COMMENT '作者',
    `email` varchar(50) NOT NULL COMMENT '邮箱',
    `target_branch` varchar(50) NOT NULL COMMENT '目标分支',
    `inline` tinyint(1) NOT NULL DEFAULT FALSE COMMENT '是否推送内部',
    `latest_commit` varchar(50) NOT NULL COMMENT '最新的commit',
    -- `code_review_address` varchar(50) COMMENT 'code review地址',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
);

CREATE TABLE `sync_log` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `sync_job_id` bigint unsigned NOT NULL COMMENT '同步工程id',
    `commit` varchar(50) DEFAULT NULL COMMENT 'commit',
    `pull_request_id` bigint unsigned DEFAULT NULL COMMENT 'pull request id',
    `log_type` varchar(20) NOT NULL COMMENT '单条日志类型',
    `log` text NOT NULL COMMENT '单条日志',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`)
);