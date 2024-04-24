ALTER TABLE `sync_repo_mapping`
ADD COLUMN `inter_token` VARCHAR(100) COMMENT '内部仓库token',
ADD COLUMN `exter_token` VARCHAR(100) COMMENT '外部仓库token';

ALTER TABLE `sync_branch_mapping`
MODIFY COLUMN `sync_direction` enum('to_outer', 'to_inter') COMMENT '首次同步方向';
