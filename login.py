from flask import render_template, session
import requests
import json

def login():
    response = requests.post(
            app.config['API_URL'] + 'users/login', data=json.dumps({"username":"rsenthil","password":"Demo@123","Site":"Matamoros"}),
            headers={'Content-Type': 'application/json'}
        )
    a = response.json()
    session['token'] = a['user']['jwtToken']
    return  render_template("ocr.html", value=session['token'])
 
