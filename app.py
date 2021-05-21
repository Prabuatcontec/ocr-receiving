import jyserver.Flask as jsf
from flask import Flask, flash, render_template, request, Response, session
from werkzeug import secure_filename
from requests.auth import HTTPBasicAuth
import os
import sys
import pytesseract
import argparse
import cv2
import re
import time
import calendar
from PIL import Image, ImageTk
from camera import VideoCamera
from image import ImageProcess
import requests
import json
from api import api_blueprint
from routes import routes_blueprint
from mysql import Connection
from selenium import webdriver
from config import Config
from filehandling import HoldStatus
import threading
import face_recognition
import pickle
__author__ = 'Prabu <mprabu@gocontec.com>'
__source__ = ''
encodeListKnown = "global"
app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(routes_blueprint, url_prefix='/')

# global camera
# camera = VideoCamera()
@jsf.use(app)
class App:
    def __init__(self):
        self.count = 5

    def increment(self):
        r = HoldStatus("").readFile("_scan")
        if r == "1":
            self.js.document.getElementById("on_status").style.display = "block"
            self.js.document.getElementById("on_status").style.color = "green"
            self.js.document.getElementById("on_status").innerHTML = "Valid"
        elif r =="2":
            self.js.document.getElementById("on_status").style.color = "green"
            self.js.document.getElementById("on_status").innerHTML = "Running"
        else:
            self.js.document.getElementById("on_status").style.display = "block"
            self.js.document.getElementById("on_status").style.color = "red"
            self.js.document.getElementById("on_status").innerHTML = "In-valid"

        r = HoldStatus("").readFile("_goodData")
        self.js.document.getElementById("dc_").innerHTML = r

        r = HoldStatus("").readFile("_processing")
        if r== "1":
            self.js.document.getElementById("on_bgp").innerHTML = "Processing"
        else:
            self.js.document.getElementById("on_bgp").innerHTML = "Waiting"

#background process happening without any refreshing
@app.route('/background_process_enable/<string:val>')
def background_process_enable(val):
    HoldStatus("0").writeFile(val,"_update")
    return ('{"nothing":1}')


@app.route('/video_feed/<string:user>')
def video_feed(user):
    return Response(gen( VideoCamera(), user),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen(camera, user):
    while True:
        frame = camera.get_Singleframe(user)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame[0] + b'\r\n\r\n')

@app.route('/getFileName')
def getFileName():
    return 'static/audio/UnitNotFound.mp3'

@app.route("/video", methods=['POST','GET'])
def ocr():
    if request.method == 'POST':
        HoldStatus("").writeFile("", "_serial")
        HoldStatus("").writeFile("", "_lastScan")
        HoldStatus("").writeFile("0", "_lastScanCount")
        HoldStatus("").writeFile("2", "_scan")
        HoldStatus("").writeFile("0", "_serialrowcount")
        HoldStatus("").writeFile("0", "_serialpostCount")
        HoldStatus("").writeFile("", "_goodData")
        HoldStatus("").writeFile("0", "_processing")
        dict = {}
        
        for value in Connection().getModels(request.form['customer'], request.form['model']):
           mdict1 = {value[1]:value[2]}
           dict.update(mdict1)
        HoldStatus("").writeFile(json.dumps(dict),"_validation")
        return App.render(render_template("ocr.html", user=session['user'] ))

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return App.render(render_template("index.html", error=""))

def maintenance():
    """ Background thread doing various maintenance tasks """
    readText = ImageProcess()
    while True:
        # do things...
        readText.readData()
        time.sleep(MAINTENANCE_INTERVAL)

def postingData():
    """ Background thread doing various maintenance tasks """
    readText = ImageProcess()
    while True:
        # do things...
        readText.postToDeepblu()
        time.sleep(MAINTENANCE_INTERVAL)

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHHER!jmN]LWX/,?RT'
    # t1 = threading.Thread(target=onoff, name='t1')
    # t1.start()

    MAINTENANCE_INTERVAL = .1

    threading.Thread(target=maintenance, daemon=True).start()
    threading.Thread(target=postingData, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
