import os
import sys
import pytesseract
import argparse
import cv2
import tkinter
import re
from PIL import Image,ImageTk
from pyzbar import pyzbar
from flask import session
import calendar
import time
from mysql import Connection
ds_factor=0.6

class ModelValidation(object):
    def __init__(self):
        self.validation = self

    def checkminmax(self, min, max, regularExp, serial):
        if len(serial) < min:
            return 1
        
        if len(serial) > max:
            return 2

        regCheck = re.match(regularExp, serial)

        if regCheck:
            return 0
        else:
            return 3

        return 0

        
    def validate(self, datas, serials):
        for c in range(len(serials)):
            for data in datas:
                if c  == data['sort']:
                    result = self.checkminmax(data['min'], data['max'], data['regularExp'],serials[c])
                    if result != 0:
                        return 1

        return 0


