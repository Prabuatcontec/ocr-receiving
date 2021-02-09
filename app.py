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
from config import Config
from filehandling import HoldStatus
__author__ = 'Prabu <mprabu@gocontec.com>'
__source__ = ''

app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix='/api')
import jyserver.Flask as jsf
@jsf.use(app)
class App:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count += 1
        HoldStatus().readFile(self.count)
        self.js.document.getElementById("count").innerHTML = self.count

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/video", methods = ['POST'])
def about():
  if request.method == 'POST':
    return App.render(render_template("ocr.html" , model= request.form['model']))

def gen(camera, model):
    response = requests.get(
            Config.API_URL + 'model/'+model,
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
  if request.method == 'POST':
    response = requests.post(
            Config.API_USER_URL + 'users/login', data=json.dumps({"username": request.form['username'],"password": request.form['password'],"Site":"Matamoros"}),
            headers={'Content-Type': 'application/json'}
        ) 
    a = response.json()
    session['user'] = a['user']['userName']
    response = requests.get(
            Config.API_URL + 'customers',
            headers={'Content-Type': 'application/json'}
        )
    a = response.json()
    return  render_template("receiving.html", customers=a['results'], user=session['user'])

@app.route("/login", methods=['GET',"POST"])
def login():
  if request.method == 'POST':
    response = requests.post(
            Config.API_USER_URL + 'users/login', data=json.dumps({"username": request.form['username'],"password": request.form['password'],"Site":"Matamoros"}),
            headers={'Content-Type': 'application/json'}
        ) 
    a = response.json()
    session['user'] = a['user']['userName']
    response = requests.get(
            Config.API_URL + 'customers',
            headers={'Content-Type': 'application/json'}
        )
    a = response.json()
    return  render_template("receiving.html", user=session['user'], customers=a['results'])
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
