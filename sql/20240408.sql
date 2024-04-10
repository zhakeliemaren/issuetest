--同步仓库信息映射表

CREATE TABLE IF NOT EXISTS `sync_repo_mapping` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `repo_name` varchar(255) NOT NULL COMMENT '仓库名称',
  `enable` tinyint(1) NOT NULL COMMENT '同步状态',
  `internal_repo_address` varchar(255) NOT NULL COMMENT '内部仓库地址',
  `external_repo_address` varchar(255) NOT NULL COMMENT '外部仓库地址',
  `sync_granularity` enum('all', 'one') NOT NULL COMMENT '同步粒度',
  `sync_direction` enum('to_outer', 'to_inter') NOT NULL COMMENT '首次同步方向',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '仓库绑定时间',
   PRIMARY KEY (`id`),
   UNIQUE KEY (`repo_name`)
) DEFAULT CHARACTER SET = utf8mb4 COMMENT = '同步仓库映射表';

--同步分支信息映射表

CREATE TABLE IF NOT EXISTS `sync_branch_mapping`(
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `repo_id` bigint unsigned NOT NULL COMMENT '仓库ID',
  `enable` tinyint(1) NOT NULL COMMENT '同步状态',
  `internal_branch_name` varchar(255) NOT NULL COMMENT '内部仓库分支名称',
  `external_branch_name` varchar(255) NOT NULL COMMENT '外部仓库分支名称',
  `sync_direction` enum('to_outer', 'to_inter') NOT NULL COMMENT '首次同步方向',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '分支绑定时间',
   PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET = utf8mb4 COMMENT = '同步分支映射表';

--日志信息表

CREATE TABLE IF NOT EXISTS `repo_sync_log`(
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `branch_id` bigint unsigned COMMENT '分支id',
  `repo_name` varchar(255) NOT NULL COMMENT '仓库名称',
  `commit_id` varchar(255) COMMENT 'commit ID',
  `log` longtext COMMENT '同步日志',
  `sync_direct` enum('to_outer', 'to_inter') NOT NULL COMMENT '同步方向',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
   PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET = utf8mb4 COMMENT = '同步日志';