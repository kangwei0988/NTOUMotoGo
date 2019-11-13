import os
import flask
from flask import render_template, request, jsonify, redirect, url_for
from flask_security import Security, MongoEngineUserDatastore ,login_user, logout_user, UserMixin, RoleMixin, login_required, current_user, roles_accepted
from pymongo import MongoClient
from flask_mongoengine import MongoEngine

app = flask.Flask(__name__)

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
app.config["MONGODB_HOST"] = "mongodb+srv://kang:kkkk0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority"
app.config["MONGODB_DB"] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'bcrypt'
app.config['SECURITY_LOGIN_USER_TEMPLATE']='login.html'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

#連接mongodb cluster
client = MongoClient('mongodb+srv://kang:kkkk0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority')
#連接cluster 裡的database
db = client['test']
#連接collection
col = db['test']

col.stats


activity_data=col.find_one({"user":"康致瑋"})
print(activity_data)

@app.route('/')
def login():
    return render_template('3-index.html')
#跳轉頁面到7-passengerSearch.html
@app.route('/passengerSearch')
def passengerSearch():
    return render_template('7-passengerSearch.html')
#跳轉頁面到8-driverSearch.html
@app.route('/driverSearch')
def driverSearch():
    return render_template('8-driverSearch.html')
#跳轉頁面到9-passengerPost.html
@app.route('/passengerPost')
def passengerPost():
    return render_template('9-passengerPost.html')
#跳轉頁面到10-driverPost.html
@app.route('/driverPost')
def driverPost():
    return render_template('10-driverPost.html')
#跳轉頁面到13-passengerRespond.html
@app.route('/passengerRespond')
def passengerRespond():
    return render_template('13-passengerRespond.html')
#跳轉頁面到15-checkRequestt.html
@app.route('checkRequestt')
def checkRequestt():
    return render_template('13-15-checkRequestt.html')


app.run(host ='0.0.0.0',port = '5000')