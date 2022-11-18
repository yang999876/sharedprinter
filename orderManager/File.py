
import json
from time import time,mktime
# CREATE TABLE IF NOT EXISTS `file`(
#    `file_id` INT UNSIGNED AUTO_INCREMENT,
#    `openid` VARCHAR(32)  NOT NULL,
#    `order_id` INT UNSIGNED NOT NULL,
#    `file_name` VARCHAR(255) NOT NULL,
#    `storage_name` VARCHAR(255) NOT NULL,
#    `page_num` INT UNSIGNED NOT NULL,
#    `copy_num` INT UNSIGNED NOT NULL,
#    `is_duplex` TINYINT(1) NOT NULL DEFAULT 0,
#    `page_range` VARCHAR(10),
#    `page_direction` ENUM("landscape", "portrait") DEFAULT "portrait",
#    `status` TINYINT(1) NOT NULL DEFAULT 0,
#    `file_size` INT NOT NULL,
#    `upload_time` TIMESTAMP NOT NULL,
#    PRIMARY KEY ( `file_id` ),
#    FOREIGN KEY (`order_id`) REFERENCES `myorder`(`order_id`)
# )ENGINE=InnoDB DEFAULT CHARSET=utf8;

class File(object):
	def __init__(self, file_id=0, openid="", order_id=0, file_name='', 
		storage_name='', page_num=0, copy_num=0, is_duplex=True, 
		page_range='', page_direction='portrait', 
		status=False, file_size=0, upload_time=0, dbres=None):
		# 从数据库获取的数据
		if dbres:
			self.file_id = dbres[0]
			self.openid = dbres[1]
			self.order_id = dbres[2]
			self.file_name = dbres[3]
			self.storage_name = dbres[4]
			self.page_num = dbres[5]
			self.copy_num = dbres[6]
			self.is_duplex = dbres[7]
			self.page_range = dbres[8]
			self.page_direction = dbres[9]
			self.status = dbres[10]
			self.file_size = dbres[11]
			self.upload_time = int(mktime(dbres[12].timetuple()))
		else:
			self.file_id = file_id
			self.openid = openid
			self.order_id = order_id
			self.file_name = file_name
			self.storage_name = storage_name
			self.page_num = page_num
			self.copy_num = copy_num
			self.is_duplex = is_duplex
			self.page_range = page_range
			self.page_direction = page_direction
			self.status = status
			self.file_size = file_size
			self.upload_time = upload_time or int(time())

	def getFileString(self):
		return self.__dict__

if __name__ == '__main__':
	file = File()