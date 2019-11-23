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
from threading import Thread
import random

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
app.config["MONGODB_HOST"] = "mongodb+srv://kang:kkkk0000@cluster0-ew3ql.gcp.mongodb.net/test?retryWrites=true&w=majority"
app.config["MONGODB_DB"] = True
app.config['SECRET_KEY'] = 'ntouMOTOgo' #os.environ.get('SECRET_KEY')
app.config['BCRYPT_LOG_ROUNDS'] = 10
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.permanent_session_lifetime = datetime.timedelta(days=1) #登入時效

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
        if 'NTOUmotoGoUser' in session and 'NTOUmotoGoToken' in session:#如果已登入and 'NTOUmotoGoToken' in session
            # print(session['NTOUmotoGoUser'])
            # print(session['NTOUmotoGoToken'])
            # print(userCol.find_one({'Account_name':session['NTOUmotoGoUser']})['_token'])
            if session['NTOUmotoGoToken'] == userCol.find_one({'Account_name':session['NTOUmotoGoUser']})['_token']:#為什麼不能用ｉｓ要用＝＝阿
                userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLogin' : datetime.datetime.now()}}) #更新登入時間，登入狀態
                print(0)
            else:
                print(1)
                session.clear()
                return redirect(url_for('loginPage'))
        else: #未登入直接將頁面導引至登入頁面
            print(2)
            return redirect(url_for('loginPage'))


#首頁
@app.route('/')
def index():
    return redirect(url_for('homePage'))
#跳轉頁面到0-logout.html
@app.route('/login')
def loginPage():
    return render_template('1-login.html',fault={})
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
    return render_template('5-passengerIndex.html')    
#跳轉頁面到6-driverIndex
@app.route('/driverIndex')
def driverIndex():
    return render_template('6-driverIndex.html') 
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
    return render_template('15-checkRequest.html')
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


#########################socketio########################################
#黑阿，就是websocket，每次io.connect會呼叫
@socketio.on('connect')
def connect():
    room = session['NTOUmotoGoUser']
    print(room)
    print(request.sid)
    print('connect')
    join_room(room)
#客戶端無回應呼叫
@socketio.on('disconnect')
def disconnect():
    room = session['NTOUmotoGoUser']
    print(room)
    print(request.sid)
    print('disconnect')
    leave_room(room)

#通知新推播(對象id，新內容)
def notifation(app, notiid, targetId, Type, msg):
    with app.app_context():
        user = userCol.find_one({'_id' : notiid})
        notif = user['_notifications']
        notif.insert(0,{'_target':str(targetId),'_type':Type,'_msg':msg,'_msgTime':datetime.datetime.now()})
        userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLogin' : datetime.datetime.now()}})
        socketio.emit('news', {'num' : len(notif)}, room = userCol.find_one({'_id' : notiid})['Account_name']) #向room推播
########################################################################

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

###########################login########################################
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
        pshash = bcrypt.hashpw(newUser['_password'].encode('utf-8'), bcrypt.gensalt())#密碼加密 編碼:UTF-8
        newUser['_password'] = str(pshash, encoding = "utf-8")
        newUser['_gender'] = False
        newUser['_motoplate'] = ''
        newUser['_history'] = []
        newUser['_postHistory'] = []
        newUser['_requestHistory'] = []
        newUser['rateHistory'] = []
        newUser['_lastLocation'] = {'lat': 25.1504516, 'lng': 121.780}
        newUser['_lastLogin'] = datetime.datetime.now()
        newUser['_token'] = False
        newUser['_notifications'] = []
        newUser['_new_notifications'] = True
        userCol.insert_one(newUser)
        # if(_mail.sendMail("海大機車共乘系統註冊通知","感謝您的使用，請注意交通安全，平安回家，學業順遂，寫程式不會遇到bug\n姓名:"+newUser["_name"]+"\n帳號:"+newUser["Account_name"]+
        #                     "\n電話:"+newUser["_phone"],newUser['_mail'])):
        return redirect(url_for('loginPage'))
#使用者登入
@app.route('/loginAPI',methods=['GET','POST'])
def login():
    user = request.values.to_dict()
    login_user = userCol.find_one({'Account_name' : user['Account_name']})
    if login_user:
        if bcrypt.hashpw(user['_password'].encode('utf-8'), login_user['_password'].encode('utf-8')) == login_user['_password'].encode('utf-8'):#密碼解碼 核對密碼 找時間嘗試
            socketio.emit('socketlogout',room = login_user['Account_name']) #把以前的用戶登出
            token = login_user['_token']
            while token is login_user['_token']:
                token = random.random()
            userCol.update({'_id' : login_user['_id']}, {"$set": {'_token' : token, '_lastLogin' : datetime.datetime.now()}}) #修改登入時間，登入狀態
            session['NTOUmotoGoUser'] = login_user['Account_name'] #建立session
            session['NTOUmotoGoToken'] = token
            session.permanent = True #設定session時效
            return redirect(url_for('homePage'))
        user["fault_password"] = '錯誤的密碼'
        return render_template('1-login.html',fault=user)
    else:
        user["faultAccount_name"] = '帳號不存在喔~'
        return render_template('1-login.html',fault=user)

#使用者登出
@app.route('/logoutAPI',methods=['GET','POST'])
def logout():
    userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLogin' : datetime.datetime.now()}})
    session.clear()
    return redirect(url_for('homePage'))
########################################################################

###########################post#########################################
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
    if post_id:
        login_user['_postHistory'].insert(0,str(post_id))
        userCol.update_one({'_id' : login_user['_id']}, {"$set": {'_postHistory' : login_user['_postHistory']}})
        thr = Thread(target=notifation, args=[app, login_user['owner_id'], post_id, 'post', '刊登成功']) #呼叫通知函示
        thr.start()
    else:
        thr = Thread(target=notifation, args=[app, login_user['owner_id'], False, 'post', '刊登失敗']) #呼叫通知函示
        thr.start()
    return redirect(url_for('allPost'))
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
    if post_id:
        login_user['_postHistory'].insert(0,str(post_id))
        userCol.update_one({'_id' : login_user['_id']}, {"$set": {'_postHistory' : login_user['_postHistory']}})
        thr = Thread(target=notifation, args=[app, login_user['owner_id'], post_id, 'post', '刊登成功']) #呼叫通知函示
        thr.start()
    else:
        thr = Thread(target=notifation, args=[app, login_user['owner_id'], False, 'post', '刊登失敗']) #呼叫通知函示
        thr.start()
    return redirect(url_for('allPost'))
#駕駛乘客刊登資訊頁面
@app.route('/postBoard',methods=['GET','POST'])
def postBoard():
    return 0
    

#######################################################################

###########################request#####################################
#駕駛乘客發出請求
@app.route('/sendRequest',methods=['GET','POST'])
def sendRequest():
    tmp = request.get_json(silent=True)
    post = postCol.find_one({'_id':ObjectId(tmp['post_id'])})#postCol.find_one({'_id':tmp['post_id']})
    if post['post_matched']:
        thr = Thread(target=notifation, args=[app, post['owner_id'], False, 'requ', '發出請求失敗，該刊登已消失']) #呼叫通知函示
        thr.start()
    else:
        user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
        info = {'post_id' : post['_id'],'sender_id': user['id'], 'pas_id' : '', 'dri_id' : '','pas_ok' : False, 'dri_ok' : False, 'pas_rate' : False, 'dri_rate' : False} #請求資料初始
        if post['post_type'] == 'pas':  #如果請求人是駕駛
            info['dri_id'] = user['_id']
            info['dri_ok'] = True
            info['pas_id'] = post['owner_id']
            info['pas_ok'] = False
        else:                           #如果請求人是乘客
            info['dri_id'] = post['owner_id']
            info['dri_ok'] = False
            info['pas_id'] = user['_id']
            info['pas_ok'] = True
        request_id =requestCol.insert_one(info).inserted_id     #請求資料的id
        if request_id:
            postOwnerRequHis = userCol.find_one({'_id' : post['owner_id']})['_requestHistory']  #更改被請求者請求歷史紀錄
            postOwnerRequHis.insert(0,str(request_id))
            userCol.update_one({'_id' : post['owner_id']},{'$set' : {'_requestHistory' : postOwnerRequHis}})
            userRequHis = userCol.find_one({'_id' : user['id']})['_requestHistory']             #更改被請求者請求歷史紀錄
            userRequHis.insert(0,str(request_id))
            userCol.update_one({'_id' : user['owner_id']},{'$set' : {'_requestHistory' : userRequHis}})
            thr = Thread(target=notifation, args=[app, post['owner_id'], request_id, 'requ', '新的請求']) #呼叫通知函示，通知被請求者
            thr.start()
            thr2 = Thread(target=notifation, args=[app, user['_id'], request_id, 'requ', '成功發出請求']) #呼叫通知函示，回報請求者發出成功
            thr2.start()
        else:
            thr = Thread(target=notifation, args=[app, user['id'], request_id, 'requ', '發出請求失敗，請重新嘗試一次']) #呼叫通知函示，回報請求者發出失敗
            thr.start()
    return redirect(url_for('allPost'))

#回傳使用者發出的要求
@app.route('/getMySendRequests',methods=['GET','POST'])
def getMySendRequests():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    requests = user['_requestHistory']
    for requid in requests:
        requ = requestCol.find_one({'_id':ObjectId(requid)})
        if requ['sender_id'] == user['_id']:
            Post = postCol.find_one({'_id' : ObjectId(requ['post_id'])})
            result={
                'driverName' :  userCol.find_one({'_id':ObjectId(requ['dri_id'])})['_name'],
                'passengerName' : userCol.find_one({'_id':ObjectId(requ['pas_id'])})['_name'],
                'Location' : Post['post_goto'],
                'Goto' : Post['post_goto'],
                'getonTime' : requ['post_getOnTime'],
                'driver_id' : str(requ['dri_id']),
                'passenger_id' : str(requ['pas_id']),
                'user_id'   :   str(user['_id']),
                'notice'    :   Post['post_id']
            }
            results.append(result)
    return jsonify(results)

#回傳使用者接收的要求
@app.route('/getMyRequests',methods=['GET','POST'])
def getMyRequests():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    requests = user['_requestHistory']
    for requid in requests:
        requ = requestCol.find_one({'_id':ObjectId(requid)})
        if requ['sender_id'] is not user['_id']:
            Post = postCol.find_one({'_id' : ObjectId(requ['post_id'])})
            result={
                'driverName' :  userCol.find_one({'_id':ObjectId(requ['dri_id'])})['_name'],
                'passengerName' : userCol.find_one({'_id':ObjectId(requ['pas_id'])})['_name'],
                'Location' : Post['post_goto'],
                'Goto' : Post['post_goto'],
                'getonTime' : requ['post_getOnTime'],
                'driver_id' : str(requ['dri_id']),
                'passenger_id' : str(requ['pas_id']),
                'user_id'   :   str(user['_id']),
                'notice'    :   Post['post_id']
            }
            results.append(result)
    return jsonify(results)
######################################################################


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
socketio.run(app,host ='0.0.0.0',port = 5000)