CREATE TABLE `freezers_traindetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `model_id` int(11) NOT NULL,
  `model_path` varchar(200) NOT NULL COMMENT '模型路径',
  `accuracy_rate` float NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `params_config` mediumtext COMMENT '配置参数',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '训练状态',
  `los_time` bigint(20) NOT NULL DEFAULT '0' COMMENT '训练花费时长',
  `val_result` mediumtext COMMENT '验证集上的结果',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

