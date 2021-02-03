from flask import Flask, render_template, request, Response, session
from werkzeug import secure_filename
import os
import sys
import pytesseract
import argparse
import cv2
import Tkinter as tkinter
import re
from PIL import Image,ImageTk
from camera import VideoCamera
import requests
import json
import login

__author__ = 'Prabu <mprabu@gocontec.com>'
__source__ = ''

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
API_URL = 'http://api.vulcan.contecprod.com/api/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['API_URL'] = API_URL 
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/video", methods = ['GET', 'POST'])
def about():
  return render_template("ocr.html")

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def ocr(camera):
    while True:
        camera.delCam()
        frame1 = camera.get_ocr()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n\r\n')

@app.route('/ocr', methods = ['GET', 'POST'])
def video_ocr():
  return Response(ocr(VideoCamera()),
                  mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/login", methods=['GET',"POST"])
def login():
  if request.method == 'POST':
    response = requests.post(
            API_URL + 'users/login', data=json.dumps({"username":"rsenthil","password":"Demo@123","Site":"Matamoros"}),
            headers={'Content-Type': 'application/json'}
        )
    a = response.json()
    session['token'] = a['user']['jwtToken']
    return  render_template("ocr.html", value=session['token'])
  if request.method == 'GET':
    return render_template("index.html")


@app.route('/video_feed')
def video_feed():
  return Response(gen(VideoCamera()),
                  mimetype='multipart/x-mixed-replace; boundary=frame')
 
if __name__ == '__main__':
  app.secret_key = 'A0Zr98j/3yX R~XHHER!jmN]LWX/,?RT'
  app.run(host="0.0.0.0", port=5000, debug=True)
