import os
import flask
from _init_ import app
from flask import render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from flask_mongoengine import MongoEngine
import _mail
import bcrypt
from flask_bcrypt import Bcrypt
import datetime
import time

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
app.config["MONGODB_HOST"] = "mongodb+srv://kang:kkkk0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority"
app.config["MONGODB_DB"] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['BCRYPT_LOG_ROUNDS'] = 10
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.permanent_session_lifetime = datetime.timedelta(seconds=30)

#連接mongodb cluster
client = MongoClient('mongodb+srv://kang:kang0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority')
#連接cluster 裡的database
db = client['motoGo']
#連接user-collection
userCol = db['user']

#進入每個頁面前
@app.before_request
def before_request():
    #除了註冊，登入功能api及其頁面的請求外，才去判斷登入狀態
    if request.endpoint not in ['newAccount','register','loginPage','login']:
        if 'NTOUmotoGoUser' in session: #判斷登入狀態
            #修改登入時間，登入狀態
            userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_logged' : True, '_lastLogin' : datetime.datetime.now()}})
        if 'NTOUmotoGoUser' not in session:
            return redirect(url_for('loginPage'))


#首頁
@app.route('/')
def index():
    return redirect(url_for('homePage'))
#跳轉頁面到0-logout.html
@app.route('/loginp')
def loginPage():
    return render_template('1-login.html')
#跳轉頁面到1-login.html
@app.route('/logout')
def logoutPage():
    return render_template('0-logout.html')
@app.route('/home')
def homePage():
    return render_template('3-index.html')
@app.route('/signup')
def register():
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
def newAccount():
    fault = {}
    newUser = request.values.to_dict()
    print(newUser)
    if userCol.find_one({"Account_name":newUser['Account_name']}):
        fault["_name"] = False
    if userCol.find_one({"_phone":newUser['_phone']}):
        fault["_phone"] = False
    if len(fault) != 0 :
        #return jsonify(fault)
        print("create false")
        return render_template('2-register.html')
    else:
        pshash = bcrypt.hashpw(newUser['_password'].encode('utf-8'), bcrypt.gensalt())
        newUser['_password'] = str(pshash, encoding = "utf-8")
        newUser['_gender'] = False
        newUser['_motoplate'] = ''
        newUser['_history'] = []
        newUser['_postHistory'] = []
        newUser['_requestHistory'] = []
        newUser['_lastLogin'] = datetime.datetime.now()
        newUser['_logged'] = False

        userCol.insert_one(newUser)
        # if(_mail.sendMail("海大機車共乘系統註冊通知","感謝您的使用，請注意交通安全，平安回家，學業順遂，寫程式不會遇到bug\n姓名:"+newUser["_name"]+"\n帳號:"+newUser["Account_name"]+
        #                     "\n電話:"+newUser["_phone"],newUser['_mail'])):
        #     print("create susecess")
        #     return render_template('1-login.html')
        return '失敗'

#使用者登入
@app.route('/login',methods=['GET','POST'])
def login():
    user = request.values.to_dict()
    login_user = userCol.find_one({'Account_name' : user['Account_name']})
    logoutTime = login_user['_lastLogin'] + datetime.timedelta(seconds= 30)
    if login_user:
        if bcrypt.hashpw(user['_password'].encode('utf-8'), login_user['_password'].encode('utf-8')) == login_user['_password'].encode('utf-8'):
            if login_user['_logged'] is False or logoutTime < datetime.datetime.now() :
                userCol.update({'Account_name' : user['Account_name']}, {"$set": {'_logged' : True, '_lastLogin' : datetime.datetime.now()}})
                session['NTOUmotoGoUser'] = login_user['Account_name']
                session.permanent = True
                return ('登入成功')
            return ('this account already signin!!')
        return ('password wrong')
    return ('account not exist')

@app.route('/logOut',methods=['GET','POST'])
def logout():
    userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_logged' : False, '_lastLogin' : datetime.datetime.now()}})
    session.clear()
    return ('登出成功')


app.run(host ='0.0.0.0',port = '5000')