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
from flask_socketio import SocketIO, emit, join_room, leave_room

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
app.config["MONGODB_HOST"] = "mongodb+srv://kang:kkkk0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority"
app.config["MONGODB_DB"] = True
app.config['SECRET_KEY'] = 'ntouMOTOgo' #os.environ.get('SECRET_KEY')
app.config['BCRYPT_LOG_ROUNDS'] = 10
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.permanent_session_lifetime = datetime.timedelta(hours=1) #登入時效

#實作socketio
socketio = SocketIO(app)

#連接mongodb cluster
client = MongoClient('mongodb+srv://kang:kang0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority')
#連接cluster 裡的database
db = client['motoGo']
#連接user-collection
userCol = db['user']
#連接post-collection
postCol = db['postInfo']
#連接request-collection
requestCol = db['requestInfo']
#連接rate-collection
rateCol = db['rateInfo']

#每個請求前執行
@app.before_request
def before_request():
    #除了註冊，登入功能api及其頁面的請求外，才去判斷登入狀態
    if request.endpoint not in ['newAccount','register','loginPage','login']:
        if 'NTOUmotoGoUser' in session: #如果已登入
            userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_logged' : True, '_lastLogin' : datetime.datetime.now()}}) #更新登入時間，登入狀態
        if 'NTOUmotoGoUser' not in session: #未登入直接將頁面導引至登入頁面
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
#跳轉頁面到2-register.html
@app.route('/signup')
def register():
    return render_template('2-register.html',fault={})
#跳轉頁面到3-index.html
@app.route('/home')
def homePage():
    return render_template('3-index.html')
#跳轉頁面到4-setting.html
@app.route('/setting')
def settingPage():
    return render_template('4-setting.html')
#跳轉頁面到5-setting.html
@app.route('/passengerIndex')
def passengerIndex():
    return render_template('5-passengerIndex')    
#跳轉頁面到6-driverIndex
@app.route('/driverIndex')
def driverIndex():
    return render_template('6-driverIndex') 
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
#跳轉頁面到11.12-allPost.html
@app.route('/allPost')
def allPost():
    return render_template('11.12-allPost.html')
#跳轉頁面到13-passengerRespond.html
@app.route('/passengerRespond')
def passengerRespond():
    return render_template('13-passengerRespond.html')
#跳轉頁面到15-checkRequestt.html
@app.route('/checkRequestt')
def checkRequestt():
    return render_template('15-_checkRequestt.html')
#跳轉頁面到16-history.html
@app.route('/history')
def history():
    return render_template('16-history.html')
#跳轉頁面到19-userInfo.html
@app.route('/userInfo')
def userInfo():
    return render_template('19-userInfo.html')
#跳轉頁面到20-Map.html
@app.route('/Map')
def MapPage():
    return render_template('20-Map.html')
#跳轉頁面到21-notice.html
@app.route('/notice')
def notice():
    return render_template('21-notice.html')
#跳轉頁面到test.html
@app.route('/test')
def test():
    return render_template('test.html')

##############################
############功能api###########
##############################

#黑阿，就是websocket，每次io.connect會呼叫
@socketio.on('connect')
def connect():
    room = session['NTOUmotoGoUser']
    join_room(room)
#客戶端無回應呼叫
@socketio.on('disconnect')
def disconnect():
    room = session['NTOUmotoGoUser']
    leave_room(room)

#通知新推播(對象id，新內容)
def notifation(userid, indexid):
    user = userCol.find_one({'_id' : userid})
    notif = user['_notifications']
    newNotif = user['_new_notifications']
    notif.insert(0,indexid)
    newNotif.insert(0,indexid)
    userCol.update({'_id' : userid}, {"$set": {'_notifications' : notif, '_new_notifications' : newNotif}})
    socketio.emit('news', {'num' : len(newNotif)}, room = userCol.find_one({'_id' : userid})['Account_name']) #向room推播


#取得座標位置
@app.route('/getLocation',methods=['GET','POST'])
def getLocation():
    pos = request.get_json(silent=True)
    userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLocation' : pos}})
    return('success')

#回傳google Map 要顯示的對方座標位置
@app.route('/returnLocation',methods=['GET','POST'])
def returnLocation():
    other_id = request.get_json(silent=True)
    other_user = userCol.find_one({'_id' : ObjectId(other_id['other_id'])})
    other_pos = {'other_lat': other_user['_lastLocation']['lat'], 'other_lng': other_user['_lastLocation']['lng']}
    return jsonify(other_pos)

#創建新使用者
@app.route('/newAccount',methods=['GET','POST'])
def newAccount():
    newUser = request.values.to_dict()
    if userCol.find_one({"Account_name":newUser['Account_name']}):
        newUser["faultAccount_name"] = "帳號已被註冊"
    if userCol.find_one({"_phone":newUser['_phone']}):
        newUser["fault_phone"] = '電話已被註冊'
    if userCol.find_one({"_mail":newUser['_mail']}):
        newUser["fault_mail"] = 'email已被註冊'
    if len(newUser) > 5 :
        return render_template('2-register.html',fault=newUser)
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
        newUser['_notifications'] = []
        newUser['_new_notifications'] = []
        userCol.insert_one(newUser)
        # if(_mail.sendMail("海大機車共乘系統註冊通知","感謝您的使用，請注意交通安全，平安回家，學業順遂，寫程式不會遇到bug\n姓名:"+newUser["_name"]+"\n帳號:"+newUser["Account_name"]+
        #                     "\n電話:"+newUser["_phone"],newUser['_mail'])):
        #     print("create susecess")
        #     return render_template('1-login.html')
        return ('成功')

#使用者登入
@app.route('/loginAPI',methods=['GET','POST'])
def login():
    user = request.values.to_dict()
    login_user = userCol.find_one({'Account_name' : user['Account_name']})
    logoutTime = login_user['_lastLogin'] + datetime.timedelta(hours=1) #登入時效
    if login_user:
        if bcrypt.hashpw(user['_password'].encode('utf-8'), login_user['_password'].encode('utf-8')) == login_user['_password'].encode('utf-8'):#密碼解碼 核對密碼 找時間嘗試
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
#駕駛乘客發出請求
@app.route('/sendRequest',methods=['GET','POST'])
def sendRequest():
    tmp = request.get_json(silent=True)
    print(tmp)
    post = postCol.find_one({'_id':ObjectId(tmp['post_id'])})#postCol.find_one({'_id':tmp['post_id']})
    if post['post_matched']:
        return ('此刊登已消失')
    postType = post['post_type']
    info = {'post_id' : post['_id'], 'pas_id' : '', 'dri_id' : '', 'pas_ok' : False, 'dri_ok' : False, 'pas_rate' : False, 'dri_rate' : False}
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    if postType == 'pas':
        info['dri_id'] = user['_id']
        info['dri_ok'] = True
        info['pas_id'] = post['owner_id']
        info['pas_ok'] = False
    else:                   #如果請求人是乘客
        info['dri_id'] = post['owner_id']
        info['dri_ok'] = False
        info['pas_id'] = user['_id']
        info['pas_ok'] = True
    request_id =requestCol.insert_one(info).inserted_id #請求對象的id
    notifation(post['owner_id'], request_id)        #呼叫通知函示
    postOwnerRequHis = userCol.find_one({'_id' : post['owner_id']})['_requestHistory']  #抓下刊登者的請求歷史紀錄
    postOwnerRequHis.insert(0,str(request_id))
    userCol.update_one({'_id' : post['owner_id']},{'$set' : {'_requestHistory' : postOwnerRequHis}})
    #notifation(ObjectId('5dd2604146b1ebd47626add1'), ObjectId('5dd29fd93a6dc24cc32eddd9'))
    return ('成功')

#回傳使用者發出的要求
@app.route('/getMySendRequests',methods=['GET','POST'])
def getMySendRequests():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    result = []
    requests = user['_requestHistory']
    print(type(requests))
    print(requests)
    for requ in requests:
        event = requestCol.find_one({'_id':ObjectId(requ)})
        post = postCol.find_one({'_id': event['post_id']})
        if post['owner_id'] == user['_id']:
            post['_id'] = str(post['_id'])
            post['owner_id'] = str(post['owner_id'])
            post['dri_id'] = str(event['dri_id'])
            post['pas_id'] = str(event['pas_id'])
            post['dri_ok'] = event['dri_ok']
            post['pas_ok'] = event['pas_ok']
            result.append(post)
    return jsonify(result)
    
#回傳歷史紀錄(包含已完成共乘)
@app.route('/getHistory', methods=['POST'])
def getHistory():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    histories = user['_history']
    for his in histories:
        history = requestCol.find_one({'_id':ObjectId(his)})
        print(history)
        result={'_id':str(history['_id'])}##
        tmp = postCol.find_one({'_id':history['post_id']})
        tmp['_id'] = str(tmp['_id'])
        tmp['owner_id'] = str(tmp['owner_id'])
        result['_post'] = tmp##
        tmp= userCol.find_one({'_id' : history['pas_id']})
        result['passenger'] = {'_name' : tmp['_name'], '_id' : str(tmp['_id'])}##
        tmp= userCol.find_one({'_id' : history['dri_id']})
        result['driver'] = {'_name' : tmp['_name'], '_id' : str(tmp['_id'])}##
        result['pas_ok'] = history['pas_ok']
        result['dri_ok'] = history['dri_ok']
        result['pas_rate'] = str(history['pas_rate'])
        result['dri_rate'] = str(history['dri_rate'])
        result['user_id'] = str(user['_id'])
        print(result)
        results.append(result)
    return jsonify(results)
    
#回傳通知
@app.route('/getNotifation',methods=['POST','GET'])
def getNotifation():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    news = user['_notifications']
    results = []
    for noti in news:
        if type(noti) is str:#系統訊息
            tmp = {'type' : 'system', '_id' : str(result['_id']), 'msgTime':datetime.datetime.now(), 'text' : noti}
            results.append(tmp)
            continue
        result = postCol.find_one({'_id' : ObjectId(noti)})
        if result:#刊登相關通知
            tmp = {'type' : 'post', '_id' : str(result['_id']), 'msgTime':datetime.datetime.now()}
            results.append(tmp)
            continue
        result = requestCol.find_one({'_id' : ObjectId(noti)})
        if result:#請求相關通知
            tmp = {'type' : 'requ', '_id' : str(result['_id']), 'msgTime':datetime.datetime.now()}
            results.append(tmp)
            continue
        result = rateCol.find_one({'_id' : ObjectId(noti)})
        if result:#評價相關通知
            tmp = {'type' : 'rate', '_id': str(result['_id']), 'msgTime':datetime.datetime.now()}
            results.append(tmp)
            continue
    return jsonify(results)
socketio.run(app,host ='0.0.0.0',port =int('5000'))