import os
import flask
from .. import app,socketio
from flask import render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient, DESCENDING
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from threading import Thread
import urllib.parse
import datetime



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

from ._socket import notifation
#每個請求前執行
@app.before_request
def before_request():
    #除了註冊，登入功能api及其頁面的請求外，才去判斷登入狀態
    if request.endpoint not in ['newAccount','register','loginPage','login']:
        if 'NTOUmotoGoUser' in session and 'NTOUmotoGoToken' in session:#如果已登入and 'NTOUmotoGoToken' in session
            # print(session['NTOUmotoGoUser'])
            # print(session['NTOUmotoGoToken'])
            # print(userCol.find_one({'Account_name':session['NTOUmotoGoUser']})['_token'])
            user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
            if session['NTOUmotoGoToken'] == user['_token']:#為什麼不能用ｉｓ要用＝＝阿
                userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLogin' : datetime.datetime.now()}}) #更新登入時間，登入狀態
                if user['_new_notifications']:
                    socketio.emit('news', {'num' : 1}, room = user['Account_name'])
            else:
                session.clear()
                return redirect(url_for('loginPage'))
        else: #未登入直接將頁面導引至登入頁面
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
#跳轉頁面到17-18-rating.html
@app.route('/rate')
def rating():
    return render_template('17-18-rating.html')
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
    userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_new_notifications' : False}})
    return render_template('21-notice.html')
@app.route('/chatRoom')
def chatRoom():
    return render_template('22-chat.html')
#跳轉頁面到test.html
@app.route('/test')
def test():
    return render_template('test.html')

##############################
############功能api###########
##############################


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


###########################post#########################################
#乘客刊登
@app.route('/pasPost',methods=['GET','POST'])
def pasPost():
    info = request.get_json(silent=True) #將data拿出
    login_user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    print(info['post_getOnTime'])
    info['post_getOnTime'] = datetime.datetime.fromisoformat(info['post_getOnTime'])
    info['post_type'] = 'pas'
    info['owner_id'] = login_user['_id']
    info['_uptime'] = datetime.datetime.now()
    info['post_matched'] = False
    post_id = postCol.insert_one(info).inserted_id #資料庫內建立一筆刊登資訊
    if post_id:
        login_user['_postHistory'].insert(0,str(post_id))
        userCol.update_one({'_id' : login_user['_id']}, {"$set": {'_postHistory' : login_user['_postHistory']}})
        thr = Thread(target=notifation, args=[app, login_user['_id'], post_id, 'post', '刊登成功']) #呼叫通知函示
        thr.start()
    else:
        thr = Thread(target=notifation, args=[app, login_user['_id'], False, 'post', '刊登失敗']) #呼叫通知函示
        thr.start()
    return redirect(url_for('allPost'))
#駕駛刊登
@app.route('/driPost',methods=['GET','POST'])
def driPost():
    info = request.get_json(silent=True) #將data拿出
    login_user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    info['post_getOnTime'] = datetime.datetime.fromisoformat(info['post_getOnTime'])
    info['post_type'] = 'dri'
    info['owner_id'] = login_user['_id']
    info['_uptime'] = datetime.datetime.now()
    info['post_matched'] = False
    post_id = postCol.insert_one(info).inserted_id #資料庫內建立一筆刊登資訊
    if post_id:
        login_user['_postHistory'].insert(0,str(post_id))
        userCol.update_one({'_id' : login_user['_id']}, {"$set": {'_postHistory' : login_user['_postHistory']}})
        thr = Thread(target=notifation, args=[app, login_user['_id'], post_id, 'post', '刊登成功']) #呼叫通知函示
        thr.start()
    else:
        thr = Thread(target=notifation, args=[app, login_user['_id'], False, 'post', '刊登失敗']) #呼叫通知函示
        thr.start()
    return redirect(url_for('allPost'))
#駕駛乘客刊登資訊頁面
@app.route('/postBoard',methods=['GET','POST'])
def postBoard():
    post_type = request.get_json()['post_type']
    print(post_type)
    posts = postCol.find({'post_type':post_type,'post_matched':False,'post_getOnTime' : {'$gt' : datetime.datetime.now()}}).sort('post_getOnTime')#,'post_getOnTime' : {'$lt' : datetime.datetime.now()}
    results = []
    for post in posts:
        print(post)
        result = post
        result['_id'] = str(result['_id'])
        result['owner_id'] = str(result['owner_id'])
        result['post_name'] = userCol.find_one({'_id' : ObjectId(post['owner_id'])})['_name']
        results.append(result)
    return jsonify(results)


#######################################################################

###########################request#####################################
#刪除請求紀錄
@app.route('/deleteRequest',methods=['GET','POST'])
def deleteRequest():
    deleteID = request.get_json(silent=True)
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    temp = user['_requestHistory']
    for eachRequest in temp:
        if eachRequest == deleteID['requ_id']:
            temp.remove(deleteID['requ_id'])
            userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_requestHistory' : temp}})       
            requestCol.delete_one({'_id':ObjectId(deleteID['requ_id'])})
            thr = Thread(target=notifation, args=[app, user['_id'], eachRequest, 'requ', '刪除請求紀錄成功']) #呼叫通知函式，回報刪除成功
            thr.start()
            return redirect(request.url)
    thr = Thread(target=notifation, args=[app, user['_id'], eachRequest, 'requ', '刪除失敗，該請求紀錄可能已被刪除，或請重新嘗試']) #呼叫通知函式，回報刪除失敗
    thr.start()        
    return redirect(request.url)

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
        info = {'post_id' : post['_id'],
                'sender_id': user['_id'],
                'pas_id' : '',
                'dri_id' : '',
                'pas_ok' : False,
                'dri_ok' : False,
                'pas_rate' : False,
                'dri_rate' : False,
                '_state' : 'waiting',
                '_uptime': datetime.datetime.now(),
                'chat_record' : ''
                } #請求資料初始
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
            postOwnerRequHis = userCol.find_one({'_id' : post['owner_id']})['_requestHistory']   #更改被請求者請求歷史紀錄
            postOwnerRequHis.insert(0,str(request_id))
            userCol.update_one({'_id' : post['owner_id']},{'$set' : {'_requestHistory' : postOwnerRequHis}})
            userRequHis = userCol.find_one({'_id' : user['_id']})['_requestHistory']             #更改被請求者請求歷史紀錄
            userRequHis.insert(0,str(request_id))
            userCol.update_one({'_id' : user['_id']},{'$set' : {'_requestHistory' : userRequHis}})
            thr = Thread(target=notifation, args=[app, post['owner_id'], request_id, 'requ', '新的請求']) #呼叫通知函示，通知被請求者
            thr.start()
            thr2 = Thread(target=notifation, args=[app, user['_id'], request_id, 'requ', '成功發出請求']) #呼叫通知函示，回報請求者發出成功
            thr2.start()
        else:
            thr = Thread(target=notifation, args=[app, user['_id'], request_id, 'requ', '發出請求失敗，請重新嘗試一次']) #呼叫通知函示，回報請求者發出失敗
            thr.start()
    return redirect(url_for('allPost'))

#回傳使用者發出的要求
@app.route('/getMySendRequests',methods=['GET','POST'])
def getRequests():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    requests = user['_requestHistory']
    for requid in requests[::-1]:#注意　倒敘問題
        requ = requestCol.find_one({'_id':ObjectId(requid)})
        if requ:
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
                    'notice'    :   Post['post_id'],
                    'state'     :   requ['_state']
                }
                results.insert(0,result)
        else:
            requests.remove(requid)
    userCol.update_one({'_id':user['_id']},{'$set':{'_requestHistory' : requests}})
    return jsonify(results)

#回傳使用者接收的要求
@app.route('/getMyRequests',methods=['GET','POST'])
def getMyRequests():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    requests = user['_requestHistory']
    for requid in requests[::-1]:#注意　倒敘問題
        requ = requestCol.find_one({'_id':ObjectId(requid)})
        if requ:
            if requ['sender_id'] != user['_id']:
                Post = postCol.find_one({'_id' : ObjectId(requ['post_id'])})
                result={
                    'driverName' :  userCol.find_one({'_id':ObjectId(requ['dri_id'])})['_name'],
                    'passengerName' : userCol.find_one({'_id':ObjectId(requ['pas_id'])})['_name'],
                    'Location' : Post['post_goto'],
                    'Goto' : Post['post_goto'],
                    'getonTime' : Post['post_getOnTime'],
                    'driver_id' : str(requ['dri_id']),
                    'passenger_id' : str(requ['pas_id']),
                    'user_id'   :   str(user['_id']),
                    'notice'    :   Post['post_notice'],
                    'state'     :   requ['_state']
                }
                results.insert(0,result)
        else:
            requests.remove(requid)
    userCol.update_one({'_id':user['_id']},{'$set':{'_requestHistory' : requests}})
    return jsonify(results)

#回覆要求
@app.route('/replyRequest',methods=['GET','POST'])
def replyRequest():
    reply = request.get_json(silent=True)
    requ = requestCol.find_one({'_id' : ObjectId(reply['requ_id'])})
    post = postCol.find_one({'_id' : requ['post_id']})
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    sender = userCol.find_one({'_id' : post['owner_id']})
    if requ and post['post_getOnTime'] > datetime.datetime.now() and post['post_matched'] != True:
        requ.update({'_id':requ['_id']},{'$set' : {requ['type']+'_ok' : reply['accept_ok'], 'answer_msg' : reply['answer_msg']}})
        if reply['accept_ok']:
            requestCol.update_one({'_id':requ['_id']},{'$set' : {'_state' : 'macthed'}})
            postCol.update_one({'_id':post['_id']},{'$set' : {'post_matched' : True}})
            thr = Thread(target=notifation, args=[app, user['_id'], requ['_id'], 'requ', '答應'+sender['_name']+'的請求成功'])    #呼叫通知函示，回報被請求者
            thr.start()
            thr2 = Thread(target=notifation, args=[app, sender['_id'], requ['_id'], 'requ', user['_name']+'已答應你的請求'])        #呼叫通知函示，回報請求者
            thr2.start()
        else:
            requestCol.update_one({'_id':requ['_id']},{'$set' : {'_state' : 'refuse'}})
            thr = Thread(target=notifation, args=[app, user['_id'], requ['_id'], 'requ', '已拒絕'+sender['_name']+'的請求'])     #呼叫通知函示，回報被請求者
            thr.start()
            thr2 = Thread(target=notifation, args=[app, sender['_id'], requ['_id'], 'requ', '對'+ user['_name']+'的請求被拒絕'])  #呼叫通知函示，回報請求者
            thr2.start()
    else:
        thr = Thread(target=notifation, args=[app, user['_id'], False, 'requ', '回復請求失敗，該請求已消失']) #呼叫通知函示，回報請求者發出失敗
        thr.start()
    return redirect(request.url)
######################################################################


#回傳歷史紀錄(包含已完成共乘)
@app.route('/getHistory', methods=['POST'])
def getHistory():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    histories = user['_matchHistory']
    for his in histories:
        history = requestCol.find_one({'_id':ObjectId(his)})
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
        results.append(result)
    return jsonify(results)
    
#回傳通知
@app.route('/getNotifation',methods=['POST','GET'])
def getNotifation():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    news = user['_notifications']
    results = []
    for noti in news:
        results.append(noti)
    return jsonify(results)

#評價資訊存入資料庫
@app.route('/sendRate',methods=['GET','POST'])
def sendRate():
    tmp = request.get_json(silent=True)
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    receiver = userCol.find_one({'_id' : tmp['receiver_id']})
    info = {'request_id':tmp['request_id'],'rater_id': user['_id'],'receiver_id':tmp['receiver_id'],'rate_range':tmp['rate_range'],'rate_note':tmp['rate_note']}
    rate_id = rateCol.insert_one(info).inserted_id
    userRateTmp = user['_rateHistory'].append(rate_id)
    receiverRateTmp = receiver['_rateHistory'].append(rate_id)
    userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_rateHistory' : userRateTmp}})
    userCol.update_one({'_id' : tmp['receiver_id']}, {"$set": {'_rateHistory' : receiverRateTmp}})

    return '成功'
