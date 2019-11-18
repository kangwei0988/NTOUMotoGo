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
from bson.objectid import ObjectId

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
app.config["MONGODB_HOST"] = "mongodb+srv://kang:kkkk0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority"
app.config["MONGODB_DB"] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['BCRYPT_LOG_ROUNDS'] = 10
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.permanent_session_lifetime = datetime.timedelta(hours=1) #登入時效

#連接mongodb cluster
client = MongoClient('mongodb+srv://kang:kang0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority')
#連接cluster 裡的database
db = client['motoGo']
#連接user-collection
userCol = db['user']
#連接user-collection
postCol = db['postInfo']
#連接user-collection
requestCol = db['requestInfo']

#每個請求前執行
@app.before_request
def before_request():
    #除了註冊，登入功能api及其頁面的請求外，才去判斷登入狀態
    if request.endpoint not in ['newAccount','register','loginPage','login']:
        if 'NTOUmotoGoUser' in session: #判斷登入狀態
            userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_logged' : True, '_lastLogin' : datetime.datetime.now()}}) #修改登入時間，登入狀態
        if 'NTOUmotoGoUser' not in session: #未登入直接將頁面導引至登入
            return redirect(url_for('loginPage'))


#首頁
@app.route('/')
def index():
    return redirect(url_for('homePage'))
#跳轉頁面到0-logout.html
@app.route('/login')
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

#通知新推播
def notifation(userid, postid):
    user = userCol.find_one({'_id' : userid})
    notif = user['_notifactions']
    newNotif = user['_new_notifactions']
    notif.insert(0,userid)
    newNotif.insert(0,userid)
    userCol.update({'_id' : userid}, {"$set": {'_logged' : True, '_lastLogin' : datetime.datetime.now()}})



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
    if userCol.find_one({"Account_name":newUser['Account_name']}):
        fault["_name"] = False
    if userCol.find_one({"_phone":newUser['_phone']}):
        fault["_phone"] = False
    if userCol.find_one({"_mail":newUser['_mail']}):
        fault["_mail"] = False
    if len(fault) != 0 :
        return render_template('2-register.html',fault=fault)
    else:
        pshash = bcrypt.hashpw(newUser['_password'].encode('utf-8'), bcrypt.gensalt())
        newUser['_password'] = str(pshash, encoding = "utf-8")
        newUser['_gender'] = False
        newUser['_motoplate'] = ''
        newUser['_history'] = []
        newUser['_postHistory'] = []
        newUser['_requestHistory'] = []
        newUser['_lastLocation'] = {'lat': 25.1504516, 'lng': 121.780}
        newUser['_lastLogin'] = datetime.datetime.now()
        newUser['_logged'] = False
        newUser['_notifactions'] = []
        newUser['_new_notifactions'] = []
        userCol.insert_one(newUser)
        # if(_mail.sendMail("海大機車共乘系統註冊通知","感謝您的使用，請注意交通安全，平安回家，學業順遂，寫程式不會遇到bug\n姓名:"+newUser["_name"]+"\n帳號:"+newUser["Account_name"]+
        #                     "\n電話:"+newUser["_phone"],newUser['_mail'])):
        #     print("create susecess")
        #     return render_template('1-login.html')
        return ('失敗')

#使用者登入
@app.route('/loginAPI',methods=['GET','POST'])
def login():
    user = request.values.to_dict()
    login_user = userCol.find_one({'Account_name' : user['Account_name']})
    logoutTime = login_user['_lastLogin'] + datetime.timedelta(hours=1) #登入時效
    if login_user:
        if bcrypt.hashpw(user['_password'].encode('utf-8'), login_user['_password'].encode('utf-8')) == login_user['_password'].encode('utf-8'):#密碼解碼 核對密碼
            if login_user['_logged'] is False or logoutTime < datetime.datetime.now() : #檢查帳號目前登入狀態
                userCol.update({'Account_name' : user['Account_name']}, {"$set": {'_logged' : True, '_lastLogin' : datetime.datetime.now()}}) #修改登入時間，登入狀態
                session['NTOUmotoGoUser'] = login_user['Account_name'] #建立session
                session.permanent = True #設定session時效
                return redirect(url_for('homePage'))
            return ('this account already signin!!')
        return ('password wrong')
    return ('account not exist')

#使用者登出
@app.route('/logoutAPI',methods=['GET','POST'])
def logout():
    userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_logged' : False, '_lastLogin' : datetime.datetime.now()}})
    session.clear()
    return ('登出成功')
#乘客刊登
@app.route('/pasPost',methods=['GET','POST'])
def pasPost():
    info = request.values.to_dict() #將data拿出
    login_user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    info['post_type'] = 'pas'
    info['owner_id'] = login_user['_id']
    info['post_time'] = datetime.datetime.now()
    info['post_matched'] = False
    post_id = postCol.insert_one(info).inserted_id #資料庫內建立一筆刊登資訊
    print(str(post_id))
    login_user['_postHistory'].append(str(post_id))
    print(login_user['_postHistory'])
    userCol.update_one({'_id' : login_user['_id']}, {"$set": {'_postHistory' : login_user['_postHistory']}})
    return ('刊登成功')
#駕駛刊登
@app.route('/driPost',methods=['GET','POST'])
def driPost():
    info = request.values.to_dict() #將data拿出
    login_user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    info['post_type'] = 'dri'
    info['owner_id'] = login_user['_id']
    info['post_time'] = datetime.datetime.now()
    info['post_matched'] = False
    post_id = postCol.insert_one(info).inserted_id #資料庫內建立一筆刊登資訊
    login_user['_postHistory'].append(str(post_id))
    userCol.update_one({'_id' : login_user['_id']}, {"$set": {'_postHistory' : login_user['_postHistory']}})
    return ('刊登成功')
#駕駛乘客刊登資訊頁面
@app.route('/postBoard',methods=['GET','POST'])
def postBoard():
    info = request.values.to_dict() #將data拿出
    target = postCol.find_one({'_id' : info['_id']})
    return jsonify(target)
#駕駛乘客刊登資訊頁面
@app.route('/sendRequest',methods=['GET','POST'])
def sendRequest():
    tmp = request.values.to_dict()
    post = postCol.find_one({'_id':tmp['_id']})
    if post['post_matched']:
        return ('此刊登已消失')
    postType = post['post_type']
    info = {'post_id' : post['_id'], 'pas_id' : '', 'dri_id' : '', 'pas_ok' : False, 'dri_ok' : False, 'pas_rate' : ObjectId(), 'dri_rate' : ObjectId()}
    if postType == 'pas':
        info['dri_id'] = postCol.find_one({'Account_name':session['NTOUnotoGoUser']})['_id']
        info['dri_ok'] = True
        info['pas_id'] = post['owner_id']
        info['pas_ok'] = False
    else:
        info['dri_id'] = post['owner_id']
        info['dri_ok'] = False
        info['pas_id'] = postCol.find_one({'Account_name':session['NTOUnotoGoUser']})['_id']
        info['pas_ok'] = True
    request_id =requestCol.insert_one(info).inserted_id
    notifation(post['owner_id'],str(request_id))##???


    

app.run(host ='0.0.0.0',port = '5000')