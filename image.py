import os, shutil
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
import time
from requests.auth import HTTPBasicAuth
import requests
from config import Config
import random
import os.path
ds_factor = 0.6

os.environ['OMP_THREAD_LIMIT'] = '1'
class ImageProcess(object):
    def readData(self):
        
        with open("static/uploads/_serial.txt", 'r') as t:
            num_lines = sum(1 for line in open("static/uploads/_serial.txt"))
            if(int(HoldStatus("").readFile("_serialrowcount")) == int(num_lines)):
                self.updateFile("0","_processing")

            if(num_lines==0):
                self.updateFile("0","_serialrowcount")

            for i,line in enumerate(t):
                if(int(HoldStatus("").readFile("_serialrowcount")) <i):
                    if(i>2):
                        self.updateFile("1","_processing")
                    self.updateFile(str(i),"_serialrowcount")
                    line = self.trimValue(line)
                    self.processImage(line)
                    

            return 1

    def trimValue(self, line):
        line = line.replace('"', '')         # i == n-1 for nth line
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.split(',')
        return line

    def updateFile(self, value, filename):
        HoldStatus("").writeFile(value, filename)

    def processImage(self, line):
        if os.path.isfile("static/processingImg/boxER_"+line[0]+".jpg"):
                imName = line[0]
                image = cv2.imread("static/processingImg/boxER_"+line[0]+".jpg")
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(Image.fromarray(gray))
                validation = open("static/uploads/_validation.txt", 'r').read()
                strVal = str(validation)
                models = json.loads(strVal)
                self.processValidation(models, text, line, imName)

    def processValidation(self, models, text, line, imName):
        for key, value in models.items():
            if key.replace('"', "") in text:
                model = key
                valid = str(value).replace("'",'"')
                jsonArray =json.loads(str(valid))
                count = 0
                
                line.pop(0)
                valid = ModelValidation().validate(
                    jsonArray["data"], line)
                if valid == '0':
                    dict = {}
                    p = 0
                    for c in range(len(line)):
                        r = open("static/uploads/_goodData.txt", "r")
                        newline = line[c].replace("\n","")
                        newline = newline.replace(" ","")
                        
                        r = str(r.read())
                        HoldStatus("").writeFile("0", "_scan")
                        if(r.find(newline) != -1):
                            p = 1
                            break
                        if(c == 0):
                            mdict1 = {"serial": newline}
                            dict.update(mdict1)
                            oldSerial = newline
                            if newline.strip() in r:
                                p = 1
                                HoldStatus("").writeFile("1", "_scan")
                                break
                        else:
                            mdict1 = {str("address"+str(c)): newline}
                            dict.update(mdict1)
                            if newline.strip() in r:
                                p = 1
                                HoldStatus("").writeFile("1", "_scan")
                                break

                    if(p == 0):
                        mdict1 = {"model": str(model)}
                        dict.update(mdict1)
                        
                        if(oldSerial in r):
                            break
                        else:
                            file1 = open("static/uploads/_goodData.txt", "a")
                            file1.write("\n")
                            file1.write(str(dict))
                            HoldStatus("").writeFile("1", "_scan")
                            data=json.dumps(dict)
                            self.postToDeepblu('/autoreceive/automation', data)
                            shutil.copy("static/processingImg/boxER_"+imName+".jpg","static/s3Bucket/boxER_"+imName+".jpg")
                            for file in os.scandir("static/processingImg"):
                                if file.name.endswith(".jpg"):
                                    os.unlink(file.path)
                            HoldStatus("").writeFile("0", "_processing")
                            HoldStatus("").writeFile("0", "_serialrowcount")
                            HoldStatus("").writeFile("", "_serial")
                            break
                else:
                    print('invalid')
                break
            elif key.replace('"', "") not in text:
                continue
    
    def postToDeepblu(self, url, data):
        response = requests.post(Config.DEEPBLU_URL + url, data,
                                headers={'Content-Type': 'application/json', 
                                'Authorization': 'Basic QVVUT1JFQ0VJVkU6YXV0b0AxMjM=' }
                                )
        
