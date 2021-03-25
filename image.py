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
            for i,line in enumerate(t):
                    if(int(HoldStatus("").readFile("_serialrowcount")) < i):
                        HoldStatus("").writeFile(str(i), "_serialrowcount")
                        print('line=',str(i))
                        data = line
                        line = line.replace('"', '')         # i == n-1 for nth line
                        line = line.replace('[', '')
                        line = line.replace(']', '')
                        line = line.split(',')

                        
                        if os.path.isfile("static/uploads/boxER_"+line[0]+".jpg"):
                            image = cv2.imread("static/uploads/boxER_"+line[0]+".jpg")
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            #print ("ffff")
                            text = pytesseract.image_to_string(Image.fromarray(gray))
                            validation = open("static/uploads/_validation.txt", 'r').read()
                            strVal = str(validation)
                            models = json.loads(strVal)
                            #print(text.encode('utf-8'))
                            valid = '1'
                            for key, value in models.items():
                                if key.replace('"', "") in text:
                                    #print(key)
                                    model = key
                                    valid = str(value).replace("'",'"')
                                    jsonArray =json.loads(str(valid))
                                    count = 0
                                    
                                    line.pop(0) 
                                    valid = ModelValidation().validate(
                                        jsonArray["data"], line)
                                    if valid == '0':
                                        print('valid')
                                        d = {"model": string(model)}
                                        for c in range(len(line)):
                                            d[str("Address"+str(c+1))] = line[c].replace("\n","")
                                        response = requests.post('https://deepbluapi.gocontec.com/charter_units/automation', data=json.dumps(str(d)),
                                            headers={'Content-Type': 'application/json', 
                                            'Authorization': 'Bearer {eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE2MTY3Mzg0MTgsInVzZXJuYW1lIjoibW1haGVzaCIsImlkIjoibW1haGVzaCIsImlhdCI6IjE2MTY2NTIwMTgifQ.Fr3hshxp6aFn_u_zkdEllHRxQyZ5o0uU0AnTU49S-0HCKxejCjeIGBxR7c3jP78dtZL1zEHS3SeCrc-FwpGPetjFigO1TkkfaoSy5-T0NZUM6v6aSpxEG4I7Ct_fpLY2fDktog-IE14frXfm0ypDD4ib6yumRmBSFZ9kdsC7HtJIKNWKvOZpsEGTltYMXC2lAAVEUI9PUnYXIwtdHunbUP6xx1aDGgxSnuBUtqgsTaqSuBOr23_S6i49UcwETlIXamLmd-6mRmDlGW1XHIVOdxpxKbnWvzD27TVld2TLxzG5kI56DanJP5i_sYvJtVO01wsAQZrmy_FR5BRiDOAQFmCspvsdjjmgQpkzc7zZ8k8tNiUNjYV1QXczpEK_P1SDqQM-CyHwlrO7ywtZA-nEwWKgmoNnJwQj9DOKIeIZlKyE6fsXx_I_HcbY3Y7veopKLrZSMaLa4Fg-C3Osinqs-vKoBCk7hEu1dfn53myMxiw2-UlMkTRzQ4nH5O_zwhWdmPTXLdZkTbVTrJ-Vo_tFzoe2tahmmtItHGi9ANJ360CWB_z2fwH2s0pVJDNAfJDJMLBqNhxISILPHy7DBRIaIXvXyLgiYFm0ubyAbV18vyzxSl_U2GZz7Ahf64U6AZ7nhtkVrchZ6qgiG2KO1UJ-bDJBtiHCVXLbX9DUmnNG_fA}'}
                                            )
                                        print(response.status_code)
                                        
                                        file1 = open("static/uploads/_goodData.txt", "a")
                                        file1.write("\n")
                                        file1.write(str(d))
                                    else:
                                        print('invalid')
                                        
                                        
                                    break
                                elif key.replace('"', "") not in text:
                                    continue
            

            return 1
