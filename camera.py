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
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 900)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))

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

     ## picture rotation
    def rotate_bound(self, image, angle):
        return imutils.rotate(image, -angle) 
 
    def getImageRotate(self, image):
        
        imageHeight, imageWidth= image.shape[0:2]
        print(imageWidth, ", ", imageHeight)
        swapImage = image.copy()
        templateImageWidth = 0
        templateImageHeight = 0
        toWidth = 500
        
        if imageWidth > toWidth and imageWidth > imageHeight:
            templateImageWidth = toWidth
            templateImageHeight = toWidth / imageWidth * imageHeight
        elif imageHeight > toWidth and imageHeight > imageWidth:
            templateImageHeight = toWidth
            templateImageWidth = toWidth / imageHeight * imageWidth
            # Use Numpy create a black paper
        lastImageWidth = templateImageWidth
        if templateImageWidth < templateImageHeight:
            lastImageWidth = templateImageHeight
        else:
            lastImageWidth = templateImageWidth
        lastImageWidth = int(math.sqrt(lastImageWidth * lastImageWidth * 2))
        templateImage = np.zeros((lastImageWidth, lastImageWidth, 3), np.uint8)
            # Use black fill the picture area
        
        templateImage.fill(0)
        # cv2.imshow("templateImage", templateImage)
        print(templateImageWidth, ", ", templateImageHeight)
        swapImage = cv2.resize(swapImage, (int(templateImageWidth), int(templateImageHeight)))
        # cv2.imshow("swapImage", swapImage)
        grayImage = cv2.cvtColor(swapImage, cv2.COLOR_BGR2GRAY)
        
        # cv2.imshow("grayImage", grayImage)
        # gaussianBlurImage = cv2.GaussianBlur(grayImage, (3, 3), 3)
        binaryImage = cv2.adaptiveThreshold(grayImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 35)
            # Ret, thresh1 = cv2.threshold (binaryImage, 127, 255, cv2.THRESH_BINARY) # is greater than the threshold value is white
        
        swapBinnaryImage = ~binaryImage
        
        # cv2.imshow("swapBinnaryImage", binaryImage)
        width, height = templateImage.shape[0:2]
        center = (height // 2, width // 2)
        print(width, height)
        
        mask = 255 * np.ones(swapBinnaryImage.shape, swapBinnaryImage.dtype)
        
        checkBaseImage = cv2.seamlessClone(swapBinnaryImage, templateImage, mask, center, cv2.NORMAL_CLONE)
        #cv2.imshow("checkBaseImage", checkBaseImage)
        minRotate = 0
        minCount = -100
        maxPixSum = -100
        
        for rotate in range(-35, 35):
            rotateImage = self.rotate_bound(checkBaseImage, rotate)
            rotateImageWidth = len(rotateImage)
            xPixList = []
            pixSum = 0
            for i in range(rotateImageWidth):
                lineCount = 0
                pixSum += cv2.sumElems(rotateImage[i])[0]
                lineCount += cv2.countNonZero(rotateImage[i])
                if lineCount > 0:
                    xPixList.append(lineCount)
            # if pixSum == -100:
            #     maxPixSum = pixSum
            #     minRotate = rotate
            # if pixSum > maxPixSum:
            #     maxPixSum = pixSum
            #     minRotate = rotate
            if minCount == -100:
                minCount = len(xPixList)
                minRotate = rotate
            # print(len(xPixList), ", ", minCount)
            if len(xPixList) < minCount:
                    minCount = len(xPixList)
                    minRotate = rotate
            # print(minRotate)
        print("over: rotate = ", minRotate)
        print("maxPixSum = ", maxPixSum)
        return minRotate

    

    def get_Singleframe(self, user):
        cv2_version_major = int(cv2.__version__.split('.')[0])

        
        success, image = self.video.read()
        # calib_result_pickle = pickle.load(open("static/uploads/camera_calib_pickle.p", "rb" ))
        # mtx = calib_result_pickle["mtx"]
        # optimal_camera_matrix = calib_result_pickle["optimal_camera_matrix"]
        # dist = calib_result_pickle["dist"]
        #image = cv2.undistort(image, mtx, dist, None, 
        #                            optimal_camera_matrix)
        #image = self.Zoom(image,2)
        img1 = image
        ret, jpeg = cv2.imencode('.jpg', img1)
        hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)


        _,contours,h= cv2.findContours(mask_yellow,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if(len(contours)<10):
            return [jpeg.tobytes(), 0] 

        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        
        fillenameImage = str(str(ts)+'-'+str(random.randint(100000,999999)))
        #image = cv2.imread("static/uploads/image.jpg")
        
        rotateAngle = self.getImageRotate(image)
        print("lastAngle = ", rotateAngle)
        image = self.rotate_bound(image, rotateAngle)
        #cv2.imwrite("static/processingImg/PPPRboxER_%s000.jpg" % fillenameImage, image)
        barcodes = pyzbar.decode(image)

        if(len(barcodes) == 0):
            image = self.rotate_bound(image, 90)


        if len(barcodes) > 0 :
            serials = []
   

            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8")
                if(self.detect_special_characer(barcodeData) == True):
                    serials.append(barcodeData)

            lastScan = HoldStatus("").readFile("_lastScan")
            lastSerialCount = HoldStatus("").readFile("_lastScanCount")
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



    def get_Singleframe_gus(self, user):

        
        success, image = self.video.read()
        calib_result_pickle = pickle.load(open("static/uploads/camera_calib_pickle.p", "rb" ))
        mtx = calib_result_pickle["mtx"]
        optimal_camera_matrix = calib_result_pickle["optimal_camera_matrix"]
        dist = calib_result_pickle["dist"]
        #image = cv2.undistort(image, mtx, dist, None, 
         #                           optimal_camera_matrix)
        #image = self.Zoom(image,2)
        img1 = image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        grayGuss = cv2.GaussianBlur(gray, (21, 21), 0)
        diff_frame = cv2.absdiff(gray, grayGuss)
        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        
        fillenameImage = str(str(ts)+'-'+str(random.randint(100000,999999)))

        

        (_, cnts, _) = cv2.findContours(thresh_frame.copy(),  
                            1, 2) 
        ret, jpeg = cv2.imencode('.jpg', image)
        for contour in cnts: 
            if cv2.contourArea(contour) > 10000: 
                # (x, y, w, h) = cv2.boundingRect(contour) 
                # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3) 
                calib_result_pickle = pickle.load(open("static/uploads/filMe.p", "rb" ))
                filMe = calib_result_pickle["filMe"]
                cv2.imwrite("static/processingImg/"+str(filMe)+"_aaaaboxER_%s.jpg" % fillenameImage, image)
                return [jpeg.tobytes(), 0]
        filMe = str(random.randint(100000,999999))
        calib_result_pickle = {}
        calib_result_pickle["filMe"] = filMe
        pickle.dump(calib_result_pickle, open("static/uploads/filMe.p", "wb" ))
        return [jpeg.tobytes(), 0]


