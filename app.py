import jyserver.Flask as jsf
from flask import Flask, flash, render_template, request, Response, session
from werkzeug import secure_filename
import os
import sys
import pytesseract
import threading
import argparse
import cv2
import re
from PIL import Image, ImageTk
from camera import VideoCamera
import requests
import json
from api import api_blueprint
from routes import routes_blueprint
from mysql import Connection
from selenium import webdriver
from config import Config
from filehandling import HoldStatus
__author__ = 'Prabu <mprabu@gocontec.com>'
__source__ = ''

app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(routes_blueprint, url_prefix='/')


@jsf.use(app)
class App:
    def __init__(self):
        self.count = 5

    def increment(self):
        r = HoldStatus(self.js.document.getElementById(
            "user").innerHTML).readFile("_scan")
        if r == "1":
            self.js.document.getElementById("on_status").style.display = "none"
            self.js.document.getElementById(
                "off_status").style.display = "block"
        else:
            self.js.document.getElementById(
                "on_status").style.display = "block"
            self.js.document.getElementById(
                "off_status").style.display = "none"

        r = HoldStatus(self.js.document.getElementById(
            "user").innerHTML).readFile("_serial")
        self.js.document.getElementById("dc_").innerHTML = r


@app.route('/video_feed/<string:model>/<string:user>')
def video_feed(model, user):
    return Response(gen(VideoCamera(), model, user),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen(camera, model, user):
    response = requests.get(
        Config.API_URL + 'model/'+model,
        headers={'Content-Type': 'application/json'}
    )
    validation = response.json()
    while True:
        frame = camera.get_frame(model, validation, user)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame[0] + b'\r\n\r\n')


@app.route("/video", methods=['POST'])
def about():
    if request.method == 'POST':
        HoldStatus(session['user']).writeFile("-", "_serial")
        HoldStatus(session['user']).writeFile("0", "_scan")
        return App.render(render_template("ocr.html", model=request.form['model'], user=session['user']))


@app.route("/receiving", methods=['GET', "POST"])
def receiving():
    if request.method == 'POST':
        response = requests.post(
            Config.API_USER_URL + 'users/login', data=json.dumps({"username": request.form['username'], "password": request.form['password'], "Site": "Matamoros"}),
            headers={'Content-Type': 'application/json'}
        )
        a = response.json()
        session['user'] = a['user']['userName']
        response = requests.get(
            Config.API_URL + 'customers',
            headers={'Content-Type': 'application/json'}
        )
        a = response.json()

        return render_template("receiving.html", customers=a['results'], user=session['user'])


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHHER!jmN]LWX/,?RT'
    # t1 = threading.Thread(target=onoff, name='t1')
    # t1.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
