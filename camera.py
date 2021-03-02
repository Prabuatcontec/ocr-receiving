import os
import sys
import pytesseract
import argparse
import cv2
import numpy as np
import tkinter
import re
from PIL import Image, ImageTk, ImageEnhance
from pyzbar import pyzbar
from flask import session
import json
import calendar
import asyncio
import time
from mysql import Connection
from modelunitvalidation import ModelValidation
from filehandling import HoldStatus
import playsound
from scipy.ndimage import interpolation as inter
import math
ds_factor = 0.6


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def delCam(self):
        self.video.release()
    
    def Reverse(lst): 
        return [ele for ele in reversed(lst)] 

    def on_off(self, model):
        img = Image.open("static/img/off.png", mode='r')
        roi_img = img.crop(box)

        img_byte_arr = io.BytesIO()
        roi_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr



    def get_frame(self, validation, user):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        
        if ret:
            if text.find('Model') >= 0:
                #time.sleep(1.0)
                models = json.loads(validation)
                #text = pytesseract.image_to_string(Image.open("static/uploads/box_111.jpg"))
                text = text.replace('\n', '')
                gmt = time.gmtime()
                counts = 0
                
                valid = 0
                model = ''
                valid = ''
                for key, value in models.items():
                    if key.replace('"', "") in text:
                        model = key
                        valid = str(value).replace("'",'"')
                        print(model, '->', valid)
                        jsonArray =json.loads(str(valid))
                        print("counter", jsonArray)
                        counts = int(jsonArray["dcCount"])
                        ts = calendar.timegm(gmt)
                        cv2.imwrite("static/uploads/box_%d.jpg" % ts, image)
                        barcodeImage = cv2.imread("static/uploads/box_%d.jpg" % ts)
                        barcodes = pyzbar.decode(barcodeImage)
                        
                        #if counts > 0 and counts != len(barcodes):
                        if counts == 0:
                            HoldStatus(user).writeFile("1", "_scan")
                        else:
                            count = 0
                            serials = []
                            for barcode in barcodes:
                                (x, y, w, h) = barcode.rect
                                cv2.rectangle(barcodeImage, (x, y),
                                            (x + w, y + h), (0, 0, 255), 2)
                                barcodeData = barcode.data.decode("utf-8")
                                serials.append(barcodeData)
                                count = count + 1
                                barcodeType = barcode.type
                                text = "{} ({})".format(barcodeData, barcodeType)
                                cv2.putText(barcodeImage, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                            0.5, (0, 0, 255), 2)
                            HoldStatus(user).writeFile(
                                json.dumps([ele for ele in reversed(serials)]), "_serial")

                            valid = ModelValidation().validate(
                                jsonArray["data"], [ele for ele in reversed(serials)])
                            if valid == 1:
                                HoldStatus(user).writeFile("1", "_scan")
                        break
                    elif key.replace('"', "") not in text:
                        continue
                    
        return [jpeg.tobytes(), 0]

    def rotate(image, angle):
        # Obtain the dimensions of the image
        (height, width) = image.shape[:2]
        (cX, cY) = (width / 2, height / 2)

        # Grab the rotation components of the matrix
        matrix = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])

        # Find the new bounding dimensions of the image
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))

        # Adjust the rotation matrix to take into account translation
        matrix[0, 2] += (new_width / 2) - cX
        matrix[1, 2] += (new_height / 2) - cY

        # Perform the actual rotation and return the image
        return cv2.warpAffine(image, matrix, (new_width, new_height))

 
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
                    cv2.imwrite("static/uploads/box_%d.jpg" %
                                ts, frame)     # save frame as JPEG file
                    count += 1
                else:
                    count = 0

            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
            print("Extracted Text: ", text)
        return frame
