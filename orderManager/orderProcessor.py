# import sys
# sys.path.append("..")
import os
import logging
import shutil
from threading import Thread
import json
from time import sleep
from time import time
from queue import Queue
from printerControler.PrinterControlor import PrinterControlor

class OrderProcessor(object):
    def __init__(self, order_list_path, messageQueue):
        self.messageQueue = messageQueue
        self.order_list_path = order_list_path
        self.file_list = Queue(maxsize=0)
        Thread(target=self.auto_delete).start()
        self.printer = PrinterControlor()
        self.logger = logging.getLogger("printer.linker")

    # 自动删除一天前的文件
    def auto_delete(self):
        while True:
            orderList = os.listdir(self.order_list_path)
            now = int(time())
            for order_id in orderList:
                orderDir = f"{self.order_list_path}{order_id}"
                orderConfig = self.readOrderConfig(orderDir)
                if (now - orderConfig["order_time"])>3600*24:
                    # 把一天前的订单自动删除
                    shutil.rmtree(orderDir)
            sleep(3600)

    # 检测文件是否下载
    def is_file_download(self, file):
        orderid = str(file['order_id'])
        storage_name = str(file['storage_name'])
        if orderid in os.listdir(self.order_list_path):
            if storage_name in os.listdir(f"{self.order_list_path}{orderid}"):
                # 文件已下载
                self.logger.info(f"one file of #{orderid} saved")
                return True
        return False

    # 根据订单路径读取订单配置信息
    def readOrderConfig(self, orderDir):
        with open(f"{orderDir}/config", "rt") as file:
            configText = file.read()
        return json.loads(configText)

    # 保存文件
    def saveFile(self, file, fileBuffer):
        if not fileBuffer:
            self.logger.error("file not exist")
            return False
        self.logger.info(f"saving file '{file['file_name']}' of #{file[orderid]}")
        orderid = file['order_id']
        while "config" in os.listdir(f"{self.order_list_path}{orderid}"):
            # 当配置文件在订单文件夹内时
            with open(f"{self.order_list_path}{orderid}/{file['file_id']}.fconf", "wt") as f:
                f.write(json.dumps(file))
            # with open(f"{self.order_list_path}{order['order_id']}/config", "rt") as file:
            #     order = json.loads(file.read())
                # print(order)
            # for i in range(len(order["file_list"])):
            # print(len(fileBuffer), int(order["file_size"]))
            # if len(fileBuffer) == int(order["file_size"]):
            path = f"{self.order_list_path}{orderid}/{file['storage_name']}" 
            with open(path, "wb") as f:
                f.write(fileBuffer)
            self.file_list.put(file)
            return True
            break

    # 检测打印任务是否完成
    def observePrintingJob(self, jobid, order_id, file_id):
        while self.printer.checkJobIsAlive(jobid):
            sleep(10)
        self.messageQueue.put({
            "order_id":order_id, 
            "complete": True,
            "file_id": file_id
        })

    # order字典
    def addOrder(self, order):
        # TODO
        workDir = self.order_list_path+str(order["order_id"])
        try:
            os.mkdir(workDir)
        except:
            pass
        with open(f"{workDir}/config", "wt") as f:
            f.write(json.dumps(order))

    # 主线程，持续处理未完成订单
    def processOrders(self):
        while True:
            file = self.file_list.get()
            if file['status']:
                # 如果文件已完成
                continue
            orderDir = f"{self.order_list_path}{file['order_id']}"
            filename = file['storage_name']
            file_id = file['file_id']
            order_id = file['order_id']
            have_file = self.is_file_download(file)
            if have_file:
                self.logger.info(f"now printing #{order_id}'s {filename}")
                jobid = self.printer.printFile(file, f"{orderDir}/{filename}")
                self.observePrintingJob(jobid, order_id, file_id)
            # self.file_list.task_done()

if __name__ == '__main__':
    messageQueue = Queue(maxsize=0)
    op = OrderProcessor("../orderList/", messageQueue)
    file = {"copy_num": 2, "file_id": 2, "file_name": "10\u9875\u7a7a\u6587\u6863.docx", "file_size": 12424, "is_duplex": 0, "openid": "ouxJc44BiGJEO_U4pSN7NTkUxzOc", "order_id": 2, "page_direction": "portrait", "page_num": 11, "page_range": "", "status": 0, "storage_name": "1643012642102-82637.pdf", "upload_time": 1643012646}
    op.is_file_download(file)