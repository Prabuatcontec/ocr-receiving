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


@api_blueprint.route('/modellist')
def modellist():
    responseBody = { "results": Connection().getModelList() }
    return jsonify(responseBody), 200

@api_blueprint.route('/insertmodeldata', methods=["POST","GET"])
def insertmodeldata():

    req1 = request.json.get('m_name')
    req2 = request.json.get('m_data')

    responseBody = {"results": Connection().insertmodeldata1(req1, req2)}
    return jsonify(responseBody), 200

@api_blueprint.route('/insertcustmodel', methods=["POST","GET"])
def insertcustmodel():

    req3 = request.json.get('m_cust2')
    req4 = request.json.get('m_model2')

    responseBody = {"results": Connection().insertcustmodel1(req3, req4)}
    return jsonify(responseBody), 200

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

@api_blueprint.route('/validatemodel/<model_id1>')
def validatemodel(model_id1):
    return jsonify(Connection().validateModel(model_id1)), 200



    