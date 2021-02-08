from flask import Flask, flash, render_template, request, Response, session
from werkzeug import secure_filename
import os
import sys
import pytesseract
import threading
import argparse
import cv2
import re
from PIL import Image,ImageTk
from camera import VideoCamera
import requests
import json
import login
from api import api_blueprint
from mysql import Connection
from selenium import webdriver 
__author__ = 'Prabu <mprabu@gocontec.com>'
__source__ = ''

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
API_URL = 'http://localhost:5000/api/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['API_URL'] = API_URL 
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/video", methods = ['POST'])
def about():
  if request.method == 'POST':
    return render_template("ocr.html" , model= request.form['model'])

def gen(camera, model):
    response = requests.get(
            API_URL + 'model/'+model,
            headers={'Content-Type': 'application/json'}
        )
    validation = response.json()
    while True:
        frame = camera.get_frame(model, validation)
        
        yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame[0] + b'\r\n\r\n')

def onoff(camera, model):
    while True:
        frame = camera.on_off(session["onoff"])
        yield (b'--frame\r\n'
              b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n\r\n')

def ocr(camera):
    while True:
        frame1 = camera.get_ocr()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n\r\n')

@app.route('/ocr', methods = ['GET', 'POST'])
def video_ocr():
  return Response(ocr(VideoCamera()),
                  mimetype='multipart/x-mixed-replace; boundary=frame')
                  
@app.route("/receiving", methods=['GET',"POST"])
def receiving():
    response = requests.get(
            API_URL + 'customers',
            headers={'Content-Type': 'application/json'}
        )
    a = response.json()
    return  render_template("receiving.html", customers=a['results'])

@app.route("/login", methods=['GET',"POST"])
def login():
  if request.method == 'POST':
    response = requests.post(
            API_URL + 'users/login', data=json.dumps({"username":"2223","password":"qewqeqw","Site":"Matamoros"}),
            headers={'Content-Type': 'application/json'}
        )
    # a = response.json()
    # session['token'] = a['user']['jwtToken']
    return  render_template("receiving.html")
  if request.method == 'GET':
    return render_template("index.html")


@app.route('/video_feed/<string:model>')
def video_feed(model):
  return Response(gen(VideoCamera(), model),
                  mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/on_off')
def on_off(model):
  return Response(onoff(VideoCamera(), model),
                  mimetype='multipart/x-mixed-replace; boundary=frame')
 
if __name__ == '__main__':
  app.secret_key = 'A0Zr98j/3yX R~XHHER!jmN]LWX/,?RT'
  # t1 = threading.Thread(target=onoff, name='t1') 
  # t1.start()  
  app.run(host="0.0.0.0", port=5000, debug=True)
