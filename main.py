import logging
from queue import Queue
from threading import Thread
from orderManager.Linker_http import Linker
from orderManager.orderProcessor import OrderProcessor

server = "https://wwkserver.top/wwkserver/"
deviceID = 1
orderList = "orderList/"
messageQueue = Queue(maxsize=0)

if __name__ == "__main__":
	logging.basicConfig(
		level = logging.INFO,
		# format = '[%(asctime)s] %(name)s - %(funcName)s - line%(lineno)d - %(levelname)s - %(message)s',
		format = '[%(asctime)s] [%(levelname)s] (%(funcName)s) %(message)s',
		filename = 'log/run.log',
		filemode = 'a'
	)
	logger = logging.getLogger("priner")
	logger.info("Start printer!")
	# try:
	myOrderProcessor = OrderProcessor(orderList, messageQueue)
	myLinker = Linker(server, deviceID, myOrderProcessor, messageQueue)
	# myLinker = Linker(deviceID, myOrderProcessor, messageQueue)
	Thread(target=myLinker.checkloop).start()
	Thread(target=myOrderProcessor.processOrders).start()
	# except Exception as e:
	# 	# 访问异常的错误编号和详细信息
	# 	print(e.args)
	# 	print(str(e))
	# 	print(repr(e))
	# 	exit() 