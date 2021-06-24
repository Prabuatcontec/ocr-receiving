from flask import Blueprint, render_template, request, Response, session, Flask, jsonify
from mysql import Connection

api_blueprint = Blueprint('api', __name__,)


@api_blueprint.route('/customers')
def customers():
    responseBody = { "results": Connection().getCustomer() }
    return jsonify(responseBody), 200

@api_blueprint.route('/modellist')
def modellist():
    responseBody = { "results": Connection().getModelList() }
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


