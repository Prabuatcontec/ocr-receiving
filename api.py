from time import sleep
from flask import Blueprint, render_template, request, Response, session, Flask, jsonify
from mysql import Connection
from filehandling import HoldStatus
import os
import glob
from camera import VideoCamera
from image import ImageProcess
import pickle

api_blueprint = Blueprint('api', __name__,)


@api_blueprint.route('/customers')
def customers():
    responseBody = { "results": Connection().getCustomer() }
    return jsonify(responseBody), 200

@api_blueprint.route('/model/<m_id>')
def model(m_id):
    return jsonify(Connection().getModel(m_id)), 200

@api_blueprint.route('/serial/<m_id>/<s>')
def serial(m_id,s):
    return jsonify(Connection().insertModel(m_id, s)), 200

@api_blueprint.route('/customer/models/<customer_id>')
def models(customer_id):
    responseBody = { "results": Connection().getModels(customer_id) }
    return jsonify(responseBody), 200

@api_blueprint.route('/capture')
def capture():
    HoldStatus("").writeFile("1", "_calibrate")
    sleep(1)
    responseBody = { "results": glob.glob("static/calibration/*.jpg")}
    return jsonify(responseBody), 200


@api_blueprint.route('/capture/delete/<id>')
def captureDelete(id):
    os.remove('static/calibration/'+id+'.jpg')
    responseBody = { "results": glob.glob("static/calibration/*.jpg")}
    return jsonify(responseBody), 200


@api_blueprint.route('/calibrate')
def calibrate():
    print(444448)
    ImageProcess().calibrateIt()
    
    responseBody = { "results": 1}
    return jsonify(responseBody), 200


    