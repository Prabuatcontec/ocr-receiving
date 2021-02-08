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
        self.validate = self

        
    def validate(self):
        return jpeg.tobytes()