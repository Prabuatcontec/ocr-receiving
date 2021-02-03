import os
import sys
import pytesseract
import argparse
import cv2
import Tkinter as tkinter
import re
from PIL import Image,ImageTk

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
        count = 0
        while True:
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
        self.video.release()
        success, image = self.video.read()
        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
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
