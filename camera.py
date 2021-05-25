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
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

         
        # th, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

        # ## (2) Morph-op to remove noise
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
        # morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)

        # ## (3) Find the max-area contour
        # cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        # cnt = sorted(cnts, key=cv2.contourArea)[-1]

        # ## This will extract the rotated rect from the contour
        # rot_rect = cv2.minAreaRect(cnt)

        # # Extract useful data
        # cx,cy = (rot_rect[0][0], rot_rect[0][1]) # rect center
        # sx,sy = (rot_rect[1][0], rot_rect[1][1]) # rect size
        # angle = rot_rect[2] # rect angle

        # # Set model points : The original shape
        # model_pts = np.array([[0,sy],[0,0],[sx,0],[sx,sy]]).astype('int')
        # # Set detected points : Points on the image
        # current_pts = cv2.boxPoints(rot_rect).astype('int')

        # # sort the points to ensure match between model points and current points
        # ind_model = np.lexsort((model_pts[:,1],model_pts[:,0]))
        # ind_current = np.lexsort((current_pts[:,1],current_pts[:,0]))

        # model_pts = np.array([model_pts[i] for i in ind_model])
        # current_pts = np.array([current_pts[i] for i in ind_current])

        # # Estimate the transform betwee points
        # M = cv2.estimateRigidTransform(current_pts,model_pts,True)

        # # Wrap the image
        # gmt = time.gmtime()
        # ts = calendar.timegm(gmt)
        # image = cv2.warpAffine(gray, M, (int(sx),int(sy)))

        
        ret, jpeg = cv2.imencode('.jpg', img1)
       
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        barcodes = pyzbar.decode(image)

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
            cv2.imwrite("static/processingImg/boxER_%s.jpg" % fillenameImage, image)
            file1 = open("static/uploads/_serial.txt", "a")
            file1.write(json.dumps([ele for ele in reversed(serials)]))
            file1.write("\n")
        return [jpeg.tobytes(), 0]
