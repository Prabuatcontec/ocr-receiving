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
import glob

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
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1000)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.video.set(cv2.CAP_PROP_FPS, 30)

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

    def Zoom(self, cv2Object, zoomSize):
        # Resizes the image/video frame to the specified amount of "zoomSize".
        # A zoomSize of "2", for example, will double the canvas size
        cv2Object = imutils.resize(cv2Object, width=(zoomSize * cv2Object.shape[1]))
        # center is simply half of the height & width (y/2,x/2)
        center = (cv2Object.shape[0]/2,cv2Object.shape[1]/2)
        # cropScale represents the top left corner of the cropped frame (y/x)
        cropScale = (center[0]/zoomSize, center[1]/zoomSize)
        # The image/video frame is cropped to the center with a size of the original picture
        # image[y1:y2,x1:x2] is used to iterate and grab a portion of an image
        # (y1,x1) is the top left corner and (y2,x1) is the bottom right corner of new cropped frame.
        cv2Object = cv2Object[int(cropScale[0]):(int(center[0]) + int(cropScale[0])), int(cropScale[1]):(int(center[1]) + int(cropScale[1]))]
        return cv2Object


    def get_Caliberation(self,user):
        filename = 'pattern.png'
 
# Chessboard dimensions
        number_of_squares_X = 10 # Number of chessboard squares along the x-axis
        number_of_squares_Y = 7  # Number of chessboard squares along the y-axis
        nX = number_of_squares_X - 1 # Number of interior corners along x-axis
        nY = number_of_squares_Y - 1 # Number of interior corners along y-axis
        r = HoldStatus("").readFile("_calibrate")
        # Define real world coordinates for points in the 3D coordinate frame
        # Object points are (0,0,0), (1,0,0), (2,0,0) ...., (5,8,0)
        object_points_3D = np.zeros((nX * nY, 3), np.float32)       
        
        # These are the x and y coordinates                                              
        object_points_3D[:,:2] = np.mgrid[0:nY, 0:nX].T.reshape(-1, 2) 

        success, image = self.video.read()
        if(r=='1'):
            fillenameImage = random.randint(100000,999999)
            cv2.imwrite("static/calibration/boxER_%s.jpg" % fillenameImage, image)
            HoldStatus("").writeFile("0", "_calibrate")
        
        #image = self.Zoom(image,2)
        img1 = image
        #image = cv2.imread('1622798624-214896_undistorted.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
        
             
        return [jpeg.tobytes(), 0]


    def get_Singleframe(self, user):
        cv2_version_major = int(cv2.__version__.split('.')[0])

        
        success, image = self.video.read()
        #image = self.Zoom(image,2)
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
        
        calib_result_pickle = pickle.load(open("static/uploads/camera_calib_pickle.p", "rb" ))
        mtx = calib_result_pickle["mtx"]
        optimal_camera_matrix = calib_result_pickle["optimal_camera_matrix"]
        dist = calib_result_pickle["dist"]
        

        image = cv2.undistort(image, mtx, dist, None, 
                                    optimal_camera_matrix)

        
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
