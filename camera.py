import os
import sys
import pytesseract
import argparse
import cv2
import tkinter
import re
from PIL import Image,ImageTk
from pyzbar import pyzbar
from flask import session
import json
import calendar
import time
from mysql import Connection
from modelunitvalidation import ModelValidation
from filehandling import HoldStatus
ds_factor=0.6

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()

    def delCam(self):
        self.video.release()


    def on_off(self, model):
        img = Image.open("static/img/off.png" , mode='r')
        roi_img = img.crop(box)

        img_byte_arr = io.BytesIO()
        roi_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr
    
    def get_frame(self, model, validation, user):
        success, image = self.video.read()
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        if ret:
            if text.find('Model') >= 0:
                #time.sleep(1.0) 
                text = pytesseract.image_to_string(Image.fromarray(gray))
                #text = pytesseract.image_to_string(Image.open("static/uploads/box_111.jpg"))
                text = text.replace('\n','')
                gmt = time.gmtime()
                counts = 0
                if text.find(model) >=0:
                    jsonArray = json.loads(str(validation))
                    counts = jsonArray["dcCount"]
 
                ts = calendar.timegm(gmt) 
                cv2.imwrite("static/uploads/box_%d.jpg" % ts, image)
                barcodeImage = cv2.imread("static/uploads/box_%d.jpg" % ts)
                barcodes = pyzbar.decode(barcodeImage)
                if counts > 0 and counts != len(barcodes):
                    HoldStatus(user).writeFile("1", "_scan")
                count = 0 
                serials = []
                for barcode in barcodes:      
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(barcodeImage, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    barcodeData = barcode.data.decode("utf-8")  
                    serials.append(barcodeData)
                    count = count + 1
                    barcodeType = barcode.type
                    text = "{} ({})".format(barcodeData, barcodeType)
                    cv2.putText(barcodeImage, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 0, 255), 2)
                HoldStatus(user).writeFile(json.dumps(serials), "_serial")
        return [jpeg.tobytes(), 0]
    
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
