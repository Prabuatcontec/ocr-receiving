import os
import sys
import pytesseract
import argparse
import cv2
import tkinter
import re
from PIL import Image,ImageTk
from pyzbar import pyzbar

import calendar
import time
ds_factor=0.6

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()

    def delCam(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        word = text.encode('utf-8').split()
        if ret:
            if text.find('Model') >= 0:
                gmt = time.gmtime()
                ts = calendar.timegm(gmt)
                cv2.imwrite("static/uploads/box_%d.jpg" % ts, image)
                # print("Test:")
                # barcodeImage = cv2.imread("static/uploads/box_%d.jpg" % ts)
                # barcodes = pyzbar.decode(barcodeImage)
                # for barcode in barcodes:
                #     # extract the bounding box location of the barcode and draw the
                #     # bounding box surrounding the barcode on the image
                #     (x, y, w, h) = barcode.rect 
                #     cv2.rectangle(barcodeImage, (x, y), (x + w, y + h), (0, 0, 255), 2)
                #     # the barcode data is a bytes object so if we want to draw it on
                #     # our output image we need to convert it to a string first
                #     barcodeData = barcode.data.decode("utf-8") 
                #     barcodeType = barcode.type 
                #     # draw the barcode data and barcode type on the image
                #     text = "{} ({})".format(barcodeData, barcodeType)
                #     cv2.putText(barcodeImage, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                #         0.5, (0, 0, 255), 2)
                    
                #         # save frame as JPEG file time.sleep(2.0)
                #     # print the barcode type and data to the terminal
                #     print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
        return jpeg.tobytes()
    
    def get_ocr(self):
        count = 0
        while self.video.isOpened():
            ret, frame = self.video.read()
            img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            text = pytesseract.image_to_string(Image.fromarray(img1))
            gmt = time.gmtime() 
            ts = calendar.timegm(gmt)
            print("Extracted eeText: ", text)
            if ret:
                if text.upper().strip() != "":
                    cv2.imwrite("static/uploads/box_%d.jpg" % ts, frame)     # save frame as JPEG file
                    count += 1
                else:
                    count = 0

            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
            print("Extracted Text: ", text)
        return frame
