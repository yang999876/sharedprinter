import json
import logging
import requests
from time import sleep
from threading import Thread

class Linker(object):
    def __init__(self, server, printer_id, orderProcessor, messageQueue):
        self.messageQueue = messageQueue
        self.server = server
        self.printer_id = printer_id
        self.orderProcessor = orderProcessor
        self.order_list = []
        self.order_files = {}
        self.timeoutCnt = 0
        self.logger = logging.getLogger("printer.linker")

    def mark_printer_awake(self):
        try:
            res = requests.get(f"{self.server}markawake/?printerid={self.printer_id}")
            if res.status_code==200:
                return res.text
            else:
                self.logger.error(f"error marking printer awake {res.status_code} {res.reason}")
        except Exception as e:
            self.logger.error("error marking printer awake")
            return False

    def mark_printer_sleep(self):
        try:
            res = requests.get(f"{self.server}marksleep/?printerid={self.printer_id}")
            if res.status_code==200:
                return res.text
            else:
                self.logger.error(f"error marking printer sleep {res.status_code} {res.reason}")
        except Exception as e:
            self.logger.error("error marking printer sleep")
            return False

    # 根据设备编号获取未完成订单
    def get_my_orders(self):
        args = "".join([f"&orders={i}" for i in self.order_list])
        url = f"{self.server}checkmyorder/?printerid={self.printer_id}{args}"
        # data = {"orders": self.order_list}
        try:
            response = requests.get(url, timeout=(2, 5))
            content = json.loads(response.content)
            return content
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, TimeoutError):
            self.timeoutCnt += 1
            if (self.timeoutCnt > 10):
                self.logger.error("timeout accumulates to 10")
                self.timeoutCnt = 0
        except Exception as e:
            self.logger.error("error occur while fetching new orders")
            return False

    # 根据订单号获得文件信息
    def get_order_files(self, orderid):
        try:
            res = requests.get(f"{self.server}getorderfiles/?orderid={orderid}")
            if res.status_code==200:
                return json.loads(res.content)
            else:
                self.logger.error(f"error getorderfile {res.status_code} {res.reason}")
                return None
        except Exception as e:
            self.logger.error(f"error occur while getting file info: {e}")
            return None

    # 返回订单完成的消息
    def orderok(self, order_id, file_id):
        try:
            res = requests.get(f"{self.server}fileok/?fileid={file_id}")
            if res.status_code==200:
                return res.text
            else:
                self.logger.error(f"error fileok {res.status_code} {res.reason}")
        except Exception as e:
            self.logger.error("error occur while sending fileok signal")
            return False

    # 根据文件名下载文件
    def getfile(self, file_name):
        try:
            res = requests.get(f"{self.server}getfiles/?filename={file_name}")
            if res.status_code==200:
                return res.content
            else:
                self.logger.error(f"error getfile {res.status_code} {res.reason}")
        except:
            self.logger.error("error occur while downloading file")
            return self.getfile(file_name)

    def check_order(self):
        while True:
            orders = self.get_my_orders()
            if orders:
                for i in orders:
                    order = json.loads(i)
                    orderid = order["order_id"]
                    self.order_list.append(orderid)
                    # 获取订单的文件
                    file_list = self.get_order_files(orderid)
                    if file_list == None:
                        continue

                    self.order_files[orderid] = []
                    for file in file_list:
                        if not file["status"]: 
                            self.order_files[orderid].append(file["file_id"])
                            
                    self.orderProcessor.addOrder(order)

                    # 已经不需要手动双面打印了！！！
                    for file in file_list:
                        download = self.orderProcessor.is_file_download(file)
                        if not download:
                            file_buffer = self.getfile(file["storage_name"])
                            saved = self.orderProcessor.saveFile(file, file_buffer)
                            if not saved:
                                self.logger.error(f"error download file #{orderid}")
                        else:
                            self.orderProcessor.file_list.put(file)
            sleep(10)
    
    def order_complete(self): 
        while True:
            message = self.messageQueue.get()
            if message["complete"]:
                orderid = message["order_id"]
                fileid = message["file_id"]
                ack = self.orderok(orderid, fileid)
                if ack == "ok":
                    # 删除文件
                    try:
                        self.order_files[orderid].remove(fileid)
                        if not self.order_files[orderid]:
                            del self.order_files[orderid]
                            self.order_list.remove(orderid)
                            self.logger.info(f"#{orderid} done")
                    except Exception as e:
                        # 删除文件失败
                        self.logger.error("Error occur!!!",exc_info = True)

    def check_printer(self):
        while(True):
            if self.orderProcessor.printer.checkPrinterAlive():
                self.mark_printer_awake()
            else:
                self.mark_printer_sleep()
            sleep(60)

    def checkloop(self):
        Thread(target=self.order_complete).start()
        Thread(target=self.check_order).start()
        Thread(target=self.check_printer).start()

if __name__=="__main__":
    from queue import Queue
    messageQueue = Queue(maxsize=0)
    linker = Linker("https://wwkserver.top/wwkserver/", 1, 'orderProcessor', messageQueue)
    Thread(target=linker.checkloop).start()
