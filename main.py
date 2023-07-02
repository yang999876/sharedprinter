import logging
import sys
from queue import Queue
from threading import Thread
from orderManager.Linker_http import Linker
from orderManager.orderProcessor import OrderProcessor
from printerControler.PrinterControlor import PrinterControlor

server = "https://wwkserver.top/wwkserver/"
deviceID = 2
deviceManufact = 'Brother Industries' # get it from `lsusb`
orderList = "orderList/"
messageQueue = Queue(maxsize=0)

if __name__ == "__main__":
	logging.basicConfig(
		level = logging.INFO,
		format = '[%(levelname)s] %(message)s',
		stream = sys.stdout
	)
	logger = logging.getLogger("priner")
	myControler = PrinterControlor(deviceManufact)
	myOrderProcessor = OrderProcessor(myControler, orderList, messageQueue)
	myLinker = Linker(server, deviceID, myOrderProcessor, messageQueue)
	Thread(target=myLinker.checkloop).start()
	Thread(target=myOrderProcessor.processOrders).start()
	logger.info("printer started")
