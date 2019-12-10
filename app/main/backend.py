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
    if request.endpoint not in ['newAccount','register','loginPage','login','verify','checkAccountStatus','setPsw','static']:
        if 'NTOUmotoGoUser' in session and 'NTOUmotoGoToken' in session:#如果已登入and 'NTOUmotoGoToken' in session
            # print(session['NTOUmotoGoUser'])
            # print(session['NTOUmotoGoToken'])
            # print(userCol.find_one({'Account_name':session['NTOUmotoGoUser']})['_token'])
            user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
            if user:
                if session['NTOUmotoGoToken'] == user['_token']:#為什麼不能用ｉｓ要用＝＝阿
                    userCol.update_one({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLogin' : datetime.datetime.now()}}) #更新登入時間，登入狀態
                    if user['_new_notifications']:
                        socketio.emit('news', {'num' : 1}, room = user['Account_name'])
                else:
                    session.clear()
                    return redirect(url_for('loginPage'))
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
#跳轉頁面到23-myPost.html
@app.route('/myPost')
def myPost():
    return render_template('23-myPost.html')
#跳轉頁面到24-matchedProcess.html
@app.route('/matchedPost')
def matchedPost():
    return render_template('24-matchedProcess.html')
@app.route('/chatRoom')
def chatRoom():
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    url = request.url.split('?')
    if len(url)>1: #判斷?後有無data
        if len(url[1]) == 24: #判斷data是否長度為24
            requ = requestCol.find_one({'_id':ObjectId(url[1])})
            if requ and user: #判斷是否有該requ
                if requ['pas_id'] == user['_id'] or requ['dri_id'] == user['_id']: #判斷用戶是否為該requ腳色
                    return render_template('22-chat.html')
    return redirect(url_for('homePage'))
    
#跳轉頁面到test.html
@app.route('/test')
def test():
    return render_template('test.html')


##############################
############功能api###########
##############################


#回傳google Map 要顯示的對方座標位置
@app.route('/getLocation',methods=['GET','POST'])
def getLocation():
    pos = request.get_json(silent=True)
    userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_lastLocation' : pos}})
    return('success')

#回傳google Map 要顯示的對方座標位置
@app.route('/returnLocation',methods=['GET','POST'])
def returnLocation():
    tmp = request.get_json(silent=True)
    other_id = tmp['other_id']
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    other_pos = {'other_lat': user['_lastLocation']['lat'], 'other_lng': user['_lastLocation']['lng']}
    if other_id and len(other_id) == 24:
        other_user = userCol.find_one({'_id' : ObjectId(other_id)})
        if other_user:
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
        # thr = Thread(target=notifation, args=[app, login_user['_id'], post_id, 'post', '刊登成功']) #呼叫通知函示
        # thr.start()
        socketio.start_background_task(notifation, app, login_user['_id'], post_id, 'post', '刊登成功')
    else:
        # thr = Thread(target=notifation, args=[app, login_user['_id'], False, 'post', '刊登失敗']) #呼叫通知函示
        # thr.start()
        socketio.start_background_task(notifation, app, login_user['_id'], False, 'post', '刊登失敗')
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
        socketio.start_background_task(notifation, app, login_user['_id'], post_id, 'post', '刊登成功')
    else:
        socketio.start_background_task(notifation, app, login_user['_id'], False, 'post', '刊登失敗')
    return redirect(url_for('allPost'))
#駕駛乘客刊登資訊頁面
@app.route('/postBoard',methods=['GET','POST'])
def postBoard():
    post_type = request.get_json()['post_type']

    requIds = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})['_requestHistory']
    not_postsId =[]
    postId = []

    for requId in requIds:
        p = str(requestCol.find_one({'_id' : ObjectId(requId)})['post_id'])
        not_postsId.append(p)

    posts = postCol.find({'post_type':post_type,'post_matched':False,'post_getOnTime' : {'$gt' : datetime.datetime.now()}}).sort('post_getOnTime')
    
    for i in posts:
        postId.append(str(i['_id']))

    not_postsId = set(not_postsId)
    postId = set(postId)
    postId = list(postId.difference(not_postsId))
    
    myId = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})['_id']
    results = []
    for id in postId:
        result = postCol.find_one({'_id' : ObjectId(id)})
        result['_id'] = str(result['_id'])
        result['owner_id'] = str(result['owner_id'])
        result['post_name'] = userCol.find_one({'_id' : ObjectId(result['owner_id'])})['_name']
        result['yourID'] = str(myId)
        results.append(result)
    return jsonify(results)


#######################################################################

###########################request#####################################
#刪除請求紀錄
@app.route('/deleteRequest',methods=['GET','POST'])
def deleteRequest():
    deleteID = request.get_json(silent=True)
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    temp = user['_requestHistory']
    for eachRequest in temp:
        if eachRequest == deleteID['delete_id']:#delete_id配合front end
            temp.remove(deleteID['delete_id'])
            userCol.update({'Account_name' : session['NTOUmotoGoUser']}, {"$set": {'_requestHistory' : temp}})       
            # thr = Thread(target=notifation, args=[app, user['_id'], deleteID['delete_id'], 'requ', '刪除請求紀錄成功']) #呼叫通知函式，回報刪除成功
            # thr.start()
            socketio.start_background_task(notifation, app, user['_id'], deleteID['delete_id'], 'requ', '刪除請求紀錄成功')
            return redirect(request.url)
    # thr = Thread(target=notifation, app, user['_id'], deleteID['delete_id'], 'requ', '刪除失敗，該請求紀錄可能已被刪除') #呼叫通知函式，回報刪除失敗
    # thr.start()        
    socketio.start_background_task(notifation, app, user['_id'], deleteID['delete_id'], 'requ', '刪除失敗，該請求紀錄可能已被刪除')
    return redirect(request.url)

#取消請求
@app.route('/cancelRequest',methods=['GET','POST'])
def cancelRequest():
    cancelID = request.get_json(silent=True)
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    requcancel = requestCol.find_one({'_id':ObjectId(cancelID['cancel_id'])})#cancel_id配合front end
    if requcancel is None:
            socketio.start_background_task(notifation, app, user['_id'], requcancel['_id'], 'requ', '找不到該請求')      
            return redirect(request.url)
    if user['_id'] == requcancel['sender_id']:
        if requcancel['_state'] == "cancelled":   
            socketio.start_background_task(notifation, app, user['_id'], requcancel['_id'], 'requ', '取消失敗，該請求已被取消')
            return redirect(request.url)
        elif requcancel['_state'] == "waiting":    
            requestCol.update({'_id':ObjectId(cancelID['cancel_id'])},{"$set": {'_state' : "cancelled"}})
            socketio.start_background_task(notifation, app, user['_id'], requcancel['_id'], 'requ', '取消請求成功')
            return redirect(request.url)
        else:
            socketio.start_background_task(notifation, app, user['_id'], requcancel['_id'], 'requ', '該請求無法取消')     
            return redirect(request.url)
    else:
        socketio.start_background_task(notifation, app, user['_id'], requcancel['_id'], 'requ', '發出請求者才有權限取消該請求')    
        return redirect(request.url)

#駕駛乘客發出請求
@app.route('/sendRequest',methods=['GET','POST'])
def sendRequest():
    tmp = request.get_json(silent=True)
    post = postCol.find_one({'_id':ObjectId(tmp['post_id'])})#postCol.find_one({'_id':tmp['post_id']})
    if post['post_matched']:
        socketio.start_background_task(notifation, app, post['owner_id'], False, 'requ', '發出請求失敗，該刊登已消失')
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
                'chat_record' : '',
                'answer_msg':''
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
            socketio.start_background_task(notifation, app, post['owner_id'], request_id, 'requ', '新的請求')
            socketio.start_background_task(notifation, app, user['_id'], request_id, 'requ', '成功發出請求')
        else:
            socketio.start_background_task(notifation, app, user['_id'], request_id, 'requ', '發出請求失敗，請重新嘗試一次')
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
                    'requ_id'   :   str(requ['_id']),
                    'driverName' :  userCol.find_one({'_id':ObjectId(requ['dri_id'])})['_name'],
                    'passengerName' : userCol.find_one({'_id':ObjectId(requ['pas_id'])})['_name'],
                    'Location' : Post['post_location'],
                    'Goto' : Post['post_goto'],
                    'getonTime' : Post['post_getOnTime'],
                    'driver_id' : str(requ['dri_id']),
                    'passenger_id' : str(requ['pas_id']),
                    'user_id'   :   str(user['_id']),
                    'notice'    :   Post['post_notice'],
                    'state'     :   requ['_state'],
                    'answer_msg':   requ['answer_msg']
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
                    'requ_id'   :   str(requ['_id']),
                    'driverName' :  userCol.find_one({'_id':ObjectId(requ['dri_id'])})['_name'],
                    'passengerName' : userCol.find_one({'_id':ObjectId(requ['pas_id'])})['_name'],
                    'Location' : Post['post_location'],
                    'Goto' : Post['post_goto'],
                    'getonTime' : Post['post_getOnTime'],
                    'driwver_id' : str(requ['dri_id']),
                    'passenger_id' : str(requ['pas_id']),
                    'user_id'   :   str(user['_id']),
                    'notice'    :   Post['post_notice'],
                    'state'     :   requ['_state'],
                    'answer_msg':   requ['answer_msg']
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
    print(reply)
    print(request.url)
    print(request.endpoint)
    requ = requestCol.find_one({'_id' : ObjectId(reply['requ_id'])})
    post = postCol.find_one({'_id' : requ['post_id']})
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    sender = userCol.find_one({'_id' : requ['sender_id']})

    umatchHistory = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})['_matchHistory']
    smatchHistory = userCol.find_one({'_id' : requ['sender_id']})['_matchHistory']

    if requ and post['post_getOnTime'] > datetime.datetime.now() and post['post_matched'] != True:
        requestCol.update_one({'_id':requ['_id']},{'$set' : {'answer_msg' : reply['answer_msg']}})
        requestCol.update_one({'_id':requ['_id']},{'$set' : {reply['type'] +'_ok': reply['accept_ok']}})
        if reply['accept_ok']:
            requestCol.update_one({'_id':requ['_id']},{'$set' : {'_state' : 'matched'}})
            postCol.update_one({'_id':post['_id']},{'$set' : {'post_matched' : True}})
            umatchHistory.insert(0,reply['requ_id'])
            smatchHistory.insert(0,reply['requ_id'])
            userCol.update_one({'Account_name':session['NTOUmotoGoUser']},{'$set' : {'_matchHistory' : umatchHistory}})
            userCol.update_one({'_id' : requ['sender_id']},{'$set' : {'_matchHistory' : smatchHistory}})
            socketio.start_background_task(notifation, app, user['_id'], requ['_id'], 'requ', '答應'+sender['_name']+'的請求成功')  #呼叫通知函示，回報被請求者
            socketio.start_background_task(notifation, app, sender['_id'], requ['_id'], 'requ', user['_name']+'已答應你的請求')     #呼叫通知函示，回報請求者
        else:
            requestCol.update_one({'_id':requ['_id']},{'$set' : {'_state' : 'refuse'}})
            socketio.start_background_task(notifation, app, user['_id'], requ['_id'], 'requ', '已拒絕'+sender['_name']+'的請求')#呼叫通知函示，回報被請求者
            socketio.start_background_task(notifation, app, sender['_id'], requ['_id'], 'requ', '對'+ user['_name']+'的請求被拒絕') #呼叫通知函示，回報請求者
    else:
        thr = Thread(target=notifation, args=[app, user['_id'], False, 'requ', '回復請求失敗，該請求已消失']) #呼叫通知函示，回報請求者發出失敗
        thr.start()
    return 'hehe'
######################################################################


#回傳歷史紀錄(包含已完成共乘及對方給予評價)
@app.route('/getHistory', methods=['POST'])
def getHistory():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    histories = user['_matchHistory']

    for his in histories:
        history = requestCol.find_one({'_id':ObjectId(his)})
        if history:
            result={'_id':str(history['_id'])}
            tmpPost = postCol.find_one({'_id':history['post_id']})
            tmpPost['_id'] = str(tmpPost['_id'])
            tmpPost['owner_id'] = str(tmpPost['owner_id'])
            result['_post'] = tmpPost
            pasUser= userCol.find_one({'_id' : history['pas_id']})
            result['passenger'] = {'_name' : pasUser['_name'], '_id' : str(pasUser['_id'])} #填入駕駛資料
            driUser= userCol.find_one({'_id' : history['dri_id']})
            result['driver']    = {'_name' : pasUser['_name'], '_id' : str(driUser['_id'])} #填入乘客資料
            result['pas_ok'] = history['pas_ok']
            result['dri_ok'] = history['dri_ok']
            if str(history['pas_rate']) in user['_rateHistory']: #如果乘客有寫評價且被評價者為自己
                pasRate = rateCol.find_one({'_id':ObjectId(history['pas_rate'])})
                if pasRate: #如果該評價存在
                    result['pas_rate'] = {'_name' : pasUser['_name'] , 'rate_range' : pasRate['rate_range'], 'rate_note' : pasRate['rate_note']} #加入乘客評價
            if str(history['dri_rate']) in user['_rateHistory']: #如果駕駛有寫評價且被評價者為自己
                pasRate = rateCol.find_one({'_id':ObjectId(history['dri_rate'])})
                if pasRate: #如果該評價存在
                    result['dri_rate'] = {'_name' : pasUser['_name'] , 'rate_range' : pasRate['rate_range'], 'rate_note' : pasRate['rate_note']} #加入駕駛評價
            result['user_id'] = str(user['_id']) #回傳自己id
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
    receiver = userCol.find_one({'_id' : ObjectId(tmp['receiver_id'])})
    requ = requestCol.find_one({'_id':ObjectId(tmp['request_id'])})
    info = {'request_id'  : ObjectId(tmp['request_id']),
            'rater_id'    : ObjectId(user['_id']),
            'receiver_id' : ObjectId(tmp['receiver_id']),
            'rate_range'  : tmp['rate_range'],
            'rate_note'   : tmp['rate_note']
            }
    rate_id = rateCol.insert_one(info).inserted_id
    if rate_id and receiver and requ:
        receiverRateTmp = receiver['_rateHistory']
        receiverRateTmp.append(str(rate_id))
        userCol.update_one({'_id' : ObjectId(tmp['receiver_id'])}, {"$set": {'_rateHistory' : receiverRateTmp}})#在接收者的_rateHistory新增被評價紀錄
        if requ['pas_id'] == user['_id']:   #如果評價者是乘客，填入乘客評價id
            requestCol.update_one({'_id':ObjectId(requ['_id'])},{'$set':{'pas_rate':rate_id}})
        else:                               #如果評價者是駕駛，填入駕駛評價id
            requestCol.update_one({'_id':ObjectId(requ['_id'])},{'$set':{'dri_rate':rate_id}})
    
    return '成功'


#個人刊登資訊
@app.route('/getSelfPost',methods=['GET','POST'])
def getSelfPost():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    results = []
    Posts = postCol.find({'owner_id':user['_id'],'post_getOnTime' : {'$gt' : datetime.datetime.now()}}).sort('post_getOnTime')#,'post_getOnTime' : {'$lt' : datetime.datetime.now()}
    
    for post in Posts:
        print(post)
        result = post
        result['_id'] = str(result['_id'])
        result['owner_id'] = str(result['owner_id'])
        result['post_name'] = userCol.find_one({'_id' : ObjectId(post['owner_id'])})['_name']
        results.append(result)
    return jsonify(results)



#配對成功測試
@app.route('/getMatchedPost',methods=['GET','POST'])
def getMatchedPost():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    matchHistory = user['_matchHistory']
    results = []

    for requestId in matchHistory:
        result = requestCol.find_one({'_id':ObjectId(requestId)})
        if result['_state'] == 'matched':
            if user['_id'] == result['pas_id']: #設定map要看的目標
                result.update({'target_id':str(result['dri_id'])})
            if user['_id'] == result['dri_id']: #設定map要看的目標
                result.update({'target_id':str(result['pas_id'])})

            result['_id'] = str(result['_id'])
            result['post_id'] = str(result['post_id'])
            result['sender_id'] = str(result['sender_id'])
            result['pas_id'] = str(result['pas_id'])
            result['dri_id'] = str(result['dri_id'])
            if type(result['pas_rate']) is not bool:
                result['pas_rate'] = str(result['pas_rate'])
            if type(result['dri_rate']) is not bool:
                result['dri_rate'] = str(result['dri_rate'])
            Post = postCol.find_one({'_id' : ObjectId(result['post_id'])})
            Post['_id'] = str(Post['_id'])
            Post['owner_id'] = str(Post['owner_id'])
            Post['post_name'] = userCol.find_one({'_id' : ObjectId(Post['owner_id'])})['_name']
            result.update({'post':Post})
            results.append(result)
    return jsonify(results)

#已完成配對
@app.route('/requComplete',methods=['GET','POST'])
def requComplete():
    tmp = request.get_json(silent=True)
    print(tmp)
    if tmp['ok']:
        requestCol.update_one({'_id':ObjectId(tmp['requ_id'])},{'$set' : {'_state' : "completed"}})
    else:
        requestCol.update_one({'_id':ObjectId(tmp['requ_id'])},{'$set' : {'_state' : "failed"}})
    return redirect(url_for('homePage'))
