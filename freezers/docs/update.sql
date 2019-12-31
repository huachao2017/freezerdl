CREATE TABLE `freezers_traindetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `model_id` int(11) NOT NULL,
  `model_path` varchar(200) NOT NULL COMMENT '模型路径',
  `accuracy_rate` float NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;