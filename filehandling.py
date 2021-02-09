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
import json
import calendar
import time
from mysql import Connection
from modelunitvalidation import ModelValidation
from config import Config

ds_factor=0.6

class HoldStatus(object):
    def __init__(self):
        self.file = file = open(Config.UPLOAD_FOLDER+str(session['user'])+ "_scan.txt", "w+")

    def readFile(self, count):
        self.file.write(str(count))
        self.file.close()
