
import json
from time import time
# CREATE TABLE IF NOT EXISTS `myorder`(
#    `order_id` INT UNSIGNED AUTO_INCREMENT,
#    `printer_id` INT UNSIGNED NOT NULL,
#    `openid` VARCHAR(32) NOT NULL,
#    `order_time` TIMESTAMP NOT NULL,
#    `file_num` INT UNSIGNED  NOT NULL,
#    `total_fee` INT NOT NULL,
#    `is_pay` TINYINT(1) NOT NULL DEFAULT 0,
#    `is_ack` TINYINT(1) NOT NULL DEFAULT 0,
#    `status` TINYINT(1) NOT NULL DEFAULT 0,
#    PRIMARY KEY ( `order_id` ),
#    FOREIGN KEY ( `printer_id` ) REFERENCES `myprinter`(`printer_id`)
# )ENGINE=InnoDB DEFAULT CHARSET=utf8;

# 合法的打印类型
class Order(object):
	def __init__(self, order_id=0, printer_id=0, openid="", order_time=0, 
		file_num=0, total_fee=0, is_pay=False, is_ack=False, status=False, dbres=None):
		if dbres:
			self.order_id = dbres[0]
			self.printer_id = dbres[1]
			self.openid = dbres[2]
			self.order_time = int(time.mktime(dbres[3].timetuple()))
			self.file_num = dbres[4]
			self.total_fee = dbres[5]
			self.is_pay = dbres[6]
			self.is_ack = dbres[7]
			self.status = dbres[8]
		else:
			self.order_id = order_id
			self.printer_id = printer_id
			self.openid = openid
			self.order_time = order_time or int(time())
			self.file_num = file_num
			self.total_fee = total_fee
			self.is_pay = is_pay
			self.is_ack = is_ack
			self.status = status
		self.orderLen = self.getOrderLen()

	def getOrderLen(self):
		guessOrderLen = len(json.dumps({
			"order_id": self.order_id,
			"printer_id": self.printer_id,
			"openid": self.openid,
			"order_time": self.order_time,
			"file_num": self.file_num,
			"total_fee": self.total_fee,
			"is_pay": self.is_pay,
			"is_ack": self.is_ack,
			"status": self.status,
			"orderLen": 200 #猜测值，没有什么实际意义
		}))
		if guessOrderLen >= 100:
			return guessOrderLen
		if guessOrderLen<100:
			return guessOrderLen - 1

	def getOrder(self):
		return {
			"order_id": self.order_id,
			"printer_id": self.printer_id,
			"openid": self.openid,
			"order_time": self.order_time,
			"file_num": self.file_num,
			"total_fee": self.total_fee,
			"is_pay": self.is_pay,
			"is_ack": self.is_ack,
			"status": self.status,
			"orderLen": self.orderLen,
		}

	def getOrderString(self):
		return json.dumps(self.getOrder())

	def getOrderBytes(self):
		return bytes(self.getOrderString(),"utf-8")