from flask import Blueprint, render_template, request, Response, session, Flask, jsonify
from mysql import Connection
from filehandling import HoldStatus
from camera import VideoCamera

routes_blueprint = Blueprint('routes', __name__,)


@routes_blueprint.route("")
def index():
    return render_template("index.html")


@routes_blueprint.route("/login", methods=['GET', "POST"])
def login():
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
        return render_template("receiving.html", user=session['user'], customers=a['results'])
    if request.method == 'GET':
        return render_template("index.html")
