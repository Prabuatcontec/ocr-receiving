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

    def get_frame(self, model, validation, user):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        if ret:
            if text.find('Model') >= 0:
                # time.sleep(1.0)
                text = pytesseract.image_to_string(Image.fromarray(gray))
                text = pytesseract.image_to_string(Image.open("static/uploads/box_111.jpg"))
                #self.deskew("static/uploads/box_111.jpg")
                text = text.replace('\n', '')
                gmt = time.gmtime()
                counts = 0
                print("count", int(text.find(model)))
                if int(text.find(model)) >=-1:
                    jsonArray = json.loads(str(validation))
                    jsonArray =json.loads(jsonArray)
                    print("counter", jsonArray)
                    counts = int(jsonArray["dcCount"])
                    ts = calendar.timegm(gmt)
                    cv2.imwrite("static/uploads/box_%d.jpg" % ts, image)
                    barcodeImage = cv2.imread("static/uploads/box_111.jpg")
                    barcodes = pyzbar.decode(barcodeImage)
                    print("count33", len(barcodes))
                    #if counts > 0 and counts != len(barcodes):
                    if counts == 0:
                        HoldStatus(user).writeFile("1", "_scan")
                        # pattern = '^a...s$'   
                        # test_string = 'abyss'
                        # result = re.match(pattern, test_string)
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

    def deskew(image, delta=1, limit=5):
        image = cv2.imread(image)
        original_image = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY_INV)[1]
        #cv2.imshow("thresh", thresh)

        x, y, w, h = 0, 0, image.shape[1], image.shape[0]

        top_half = ((x,y), (x+w, y+h/2))
        bottom_half = ((x,y+h/2), (x+w, y+h))

        top_x1,top_y1 = top_half[0]
        top_x2,top_y2 = top_half[1]
        bottom_x1,bottom_y1 = bottom_half[0]
        bottom_x2,bottom_y2 = bottom_half[1]

        # Split into top/bottom ROIs
        top_image = thresh[top_y1:top_y2, top_x1:top_x2]
        bottom_image = thresh[bottom_y1:bottom_y2, bottom_x1:bottom_x2]

        #cv2.imshow("top_image", top_image)
        #cv2.imshow("bottom_image", bottom_image)

        # Count non-zero array elements
        top_pixels = cv2.countNonZero(top_image)
        bottom_pixels = cv2.countNonZero(bottom_image)

        print('top', top_pixels)
        print('bottom', bottom_pixels)

        # Rotate if upside down
        if top_pixels > bottom_pixels:
            rotated = rotate(original_image, 180)
            cv2.imwrite("static/uploads/1.jpg" % ts, rotated)
            #cv2.imshow("rotated", rotated)
        # def determine_score(arr, angle):
        #     data = inter.rotate(arr, angle, reshape=False, order=0)
        #     histogram = np.sum(data, axis=1)
        #     score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
        #     return histogram, score
        # image = cv2.imread("static/uploads/box_111.jpg")
         
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # scores = []
        # angles = np.arange(-1, 1 + 5, 5)
        # for angle in angles:
        #     histogram, score = determine_score(thresh, angle)
        #     scores.append(score)

        # best_angle = angles[scores.index(max(scores))]

        # (h, w) = image.shape[:2]
        # center = (w // 2, h // 2)
        # M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
        # rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
        #         borderMode=cv2.BORDER_REPLICATE)
        # print("ADDEDDD", rotated)
        # cv2.imwrite('rotated.png', rotated)
        # img_before = cv2.imread("static/uploads/box_111.jpg")
        # print("ADDEDDD", "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        # #cv2.imshow("Before", img_before)
        # key = cv2.waitKey(0)

        # img_gray = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
        # img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
        # lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

        # angles = []

        # for [[x1, y1, x2, y2]] in lines:
        #     cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
        #     angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        #     angles.append(angle)

        # #cv2.imshow("Detected lines", img_before)
        # key = cv2.waitKey(0)

        # median_angle = np.median(angles)
        # img_rotated = ndimage.rotate(img_before, median_angle)
        # gmt = time.gmtime()
        # ts = calendar.timegm(gmt)
        # cv2.imwrite("static/uploads/box_%d.jpg" % ts, img_rotated)
        # print("ADDSSSSSSSSSSSSSSsEDDD", "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        # print(f"Angle is {median_angle:.04f}")

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
