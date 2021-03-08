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
import imutils
import time
from requests.auth import HTTPBasicAuth
import requests
from config import Config
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

    def detect(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # compute the Scharr gradient magnitude representation of the images
        # in both the x and y direction using OpenCV 2.4
        ddepth = cv2.cv.CV_32F if imutils.is_cv2() else cv2.CV_32F
        gradX = cv2.Sobel(gray, ddepth=ddepth, dx=1, dy=0, ksize=-1)
        gradY = cv2.Sobel(gray, ddepth=ddepth, dx=0, dy=1, ksize=-1)
        # subtract the y-gradient from the x-gradient
        gradient = cv2.subtract(gradX, gradY)
        gradient = cv2.convertScaleAbs(gradient)
        # blur and threshold the image
        blurred = cv2.blur(gradient, (9, 9))
        (_, thresh) = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)
        # construct a closing kernel and apply it to the thresholded image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        # perform a series of erosions and dilations
        closed = cv2.erode(closed, None, iterations=4)
        closed = cv2.dilate(closed, None, iterations=4)
        # find the contours in the thresholded image
        cnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # if no contours were found, return None
        
        if len(cnts) == 0:
            return None
        
        # otherwise, sort the contours by area and compute the rotated
        # bounding box of the largest contour
        c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
        rect = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(rect) if imutils.is_cv2() else cv2.boxPoints(rect)
        box = np.int0(box)
        # return the bounding box of the barcode
        return box



    def get_frame(self, user):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
       
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        barcodes = pyzbar.decode(image)
        start_time = time.time()

        if len(barcodes) > 0:
            text = pytesseract.image_to_string(Image.fromarray(gray))
            validation = HoldStatus(user).readFile("_validation")
            strVal = str(validation)
            print("text-------------------", strVal)
            models = json.loads(strVal)
            text = text.replace('\n', ' ')
            
            counts = 0
            valid = 0
            model = ''
            valid = ''
            for key, value in models.items():
                if key.replace('"', "") in text:
                    model = key
                    valid = str(value).replace("'",'"')
                    jsonArray =json.loads(str(valid))
                    count = 0
                    serials = []
                    barcodes = pyzbar.decode(Image.open("static/uploads/box_123.jpg"))

                    print("textintssss", str(len(barcodes)))
                    for barcode in barcodes:
                        barcodeData = barcode.data.decode("utf-8")
                        serials.append(barcodeData)
                        count = count + 1
                    HoldStatus(user).writeFile(
                        json.dumps([ele for ele in reversed(serials)]), "_serial")

                    valid = ModelValidation().validate(
                        jsonArray["data"], [ele for ele in reversed(serials)])

                    if valid == '0':
                        cv2.imwrite("static/uploads/boxER_%d.jpg" % ts, image)
                    HoldStatus(user).writeFile(valid, "_scan")
                        
                    break
                elif key.replace('"', "") not in text:
                    continue
        #print("--- %s seconds ---" % (time.time() - start_time))
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
