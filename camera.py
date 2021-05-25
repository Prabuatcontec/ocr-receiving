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
import re
from scipy.ndimage import interpolation as inter
import math
import time
from requests.auth import HTTPBasicAuth
import requests
from config import Config
import random
import pandas
from datetime import datetime 
import pickle
import imutils

ds_factor = 0.6
path = 'dataset'
image = np.zeros((512,512,3))
drawing = False
ix = 0
iy = 0

import face_recognition

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def delCam(self):
        self.video.release()

    
    def Reverse(lst): 
        return [ele for ele in reversed(lst)] 

    
    def detect_special_characer(self, pass_string):
        regex= re.compile("'") 
        if(regex.search(pass_string) != None): 
            return False
         
        regex= re.compile('[@_!#$%^&*()<>?/\\\|}{~:[\]]"') 
        if(regex.search(pass_string) == None): 
            res = True
        else: 
            res = False
        return(res)

    def get_Singleframe(self, user):
        success, image = self.video.read()
        img1 = image
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

        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        # otherwise, just take the inverse of the angle to make
        # it positive
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        cv2.putText(rotated, "Angle: {:.2f} degrees".format(angle),
	        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        
        ret, jpeg = cv2.imencode('.jpg', image)
       
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        barcodes = pyzbar.decode(rotated)

        if len(barcodes) > 0:
            fillenameImage = str(str(ts)+'-'+str(random.randint(100000,999999)))
            
            serials = []
                    
            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8")
                if(self.detect_special_characer(barcodeData) == True):
                    serials.append(barcodeData)
            
            lastScan = HoldStatus("").readFile("_lastScan")
            lastSerialCount = HoldStatus("").readFile("_lastScanCount")
            # print("last Scan = "+ str(fillenameImage) +"======"+ str(lastScan) +"======"+ str(json.dumps([ele for ele in reversed(serials)])))
            # print("last Scancount = "+ str(lastSerialCount) +"======"+ str(len(serials)))
            if(str(lastScan) == str(json.dumps([ele for ele in reversed(serials)]))):
                return [jpeg.tobytes(), 0]
            if(int(lastSerialCount) > int(len(serials))):
                return [jpeg.tobytes(), 0] 

            HoldStatus("").writeFile(json.dumps([ele for ele in reversed(serials)]), "_lastScan")
            HoldStatus("").writeFile(str(len(serials)), "_lastScanCount")

            serials.append(fillenameImage)
            cv2.imwrite("static/processingImg/boxER_%s.jpg" % fillenameImage, rotated)
            file1 = open("static/uploads/_serial.txt", "a")
            file1.write(json.dumps([ele for ele in reversed(serials)]))
            file1.write("\n")
        return [jpeg.tobytes(), 0]
