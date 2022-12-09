import os
import re
import logging
import math

def getPdftkOrder(n):
  rest = 4 - n % 4
  rst = []
  odd = True
  for i in range(1, rest+1):
    if odd:
      rst.append('A1')
      rst.append(i)
    else:
      rst.append(i)
      rst.append('A1')
    odd = not odd
  end = int(math.ceil(n/4) * 4)
  half = int(end / 2)
  for i in range(rest+1, half+1):
    if odd:
      rst.append(end-i+1)
      rst.append(i)
    else:
      rst.append(i)
      rst.append(end-i+1)
    odd = not odd
  out = ''
  for i in rst:
    out += str(i) + " "
  return out

class PrinterControlor(object): 
	def __init__(self, deviceManufact):
		self.getJobIdPat = re.compile("request id is (.+?) ")
		self.logger = logging.getLogger("printer.linker")
		self.manufact = deviceManufact

	def checkPrinter(self):
		with os.popen("lp -p -d") as res:
			text = res.read()
		return text

	def checkPrinterAlive(self):
		with os.popen(f"lsusb | grep '{self.manufact}'") as res:
			text = res.read()
			return True if text else False

	def printFile(self, file, filePath):
		copy_num = file['copy_num']
		page_direction = ""
		page_range = ""
		page_num = file['page_num']
		is_duplex = file['is_duplex']
		is_booklet = file['is_booklet']
		crop_margin = file['crop_margin']
		sides = ""
		booklet = ""

		if file['page_direction']:
			page_direction = f"-o {file['page_direction']}"

		if is_duplex or is_booklet:
			sides = "-o sides=two-sided"
			if is_booklet or file['page_direction']=="landscape":
				sides += "-short-edge"
			else:
				sides += "-long-edge"
		else:
			sides = "-o sides=one-sided"

		if crop_margin:
			croppedPath = filePath[:-4] + "_cropped.pdf"
			cropCommand = f"pdfcropmargins {filePath} -o {croppedPath}"
			with os.popen(cropCommand) as res:
				text = res.read()
			filePath = croppedPath

		if is_booklet:
			booklet = "-o number-up=2"
			pageOrder = getPdftkOrder(page_num)
			convertedPath = filePath[:-4] + "-book.pdf"
			convertCommand = f"pdftk {filePath} A=asset/blank.pdf cat {pageOrder} output {convertedPath}"
			with os.popen(convertCommand) as res:
				text = res.read()
			filePath = convertedPath

		if file['page_range']:
			page_range = f"-o page-ranges={file['page_range']}"

		printing_command = f"lp -n {copy_num} -o fit-to-page {page_direction} {page_range} {booklet} {sides} {filePath}"
		with os.popen(printing_command) as res:
			text = res.read()
		jobid = self.getJobIdPat.search(text).group(1)
		return jobid

	def checkJobIsAlive(self, jobid):
		while True:
			with os.popen("lpstat") as res:
				text = res.read()
			match = re.search(jobid, text)
			if match:
				return True
			else:
				return False

if __name__ == '__main__':
	import json
	file = json.loads('{"copy_num": 4, "file_id": 7, "file_name": "\u5b97\u5ba4\u730e\u67aa.png", "file_size": 149714, "is_duplex": 0, "openid": "oFRIU5DZs9fyvU0-MTwK3emuZ838", "order_id": 9, "page_direction": null, "page_num": 1, "page_range": "", "status": 0, "storage_name": "1643278019787-820340.png", "upload_time": 1643278020}')
	printer = PrinterControlor()
	filePath = f"../orderList/{file['order_id']}/{file['storage_name']}"
	printer.printFile(file, filePath)
