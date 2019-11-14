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
db = client['motoGo']
#連接user-collection
userCol = db['user']


@app.route('/')
def login():
    return render_template('2-register.html')
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
@app.route('/checkRequestt')
def checkRequestt():
    return render_template('15-_checkRequestt.html')
#跳轉頁面到20-Map.html
@app.route('/Map')
def MapPage():
    return render_template('20-Map.html')
##############################
############功能api###########
##############################

#回傳google Map 要顯示的座標位置
@app.route('/checkLocation',methods=['GET','POST'])
def getTargetLocation():
    addr = {'lat': 25.1504516, 'lng': 121.780}
    return jsonify(addr)
#創建新使用者
@app.route('/newAccount',methods=['GET','POST'])
def insertNewUser():
    fault = {}
    newUser = request.values.to_dict()
    if userCol.find_one({"Account_name":newUser["_name"]}):
        fault["_name"] = False
    if userCol.find_one({"_phone":newUser["_phone"]}):
        fault["_phone"] = False
    if len(fault) != 0 :
        #return jsonify(fault)
        print("create false")
        return render_template('2-register.html')
    else:
        newUser['_gender'] = False
        newUser['_motoplate'] = ''
        newUser['_history'] = []
        newUser['_postHistory'] = []
        newUser['_requestHistory'] = []
        userCol.insert_one(newUser)
        print("create susecess")
        return render_template('3-index.html')


app.run(host ='0.0.0.0',port = '5000')