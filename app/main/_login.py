from .. import app,socketio
import random
from .backend import userCol,requestCol
from flask import render_template, request, jsonify, redirect, url_for, session
import datetime
import bcrypt
from threading import Thread
from ._socket import notifation
from ._mail import sendMail
from bson.objectid import ObjectId
import os
from ._userInfo import allowed_file



###########################login########################################
#創建新使用者
@app.route('/newAccount',methods=['GET','POST'])
def newAccount():
    newUser = request.values.to_dict()
    if userCol.find_one({"Account_name":newUser['Account_name']}):
        newUser["faultAccount_name"] = "帳號已被註冊"
    if userCol.find_one({"_phone":newUser['_phone']}):
        newUser["fault_phone"] = '電話已被註冊'
    # if userCol.find_one({"_mail":newUser['_mail']}):
    #     newUser["fault_mail"] = 'email已被註冊'
    if len(newUser) > 6 :
        return render_template('2-register.html',fault=newUser)
    else:
        token = random.random()
        pshash = bcrypt.hashpw(str(token).encode('utf-8'), bcrypt.gensalt())#密碼加密 編碼:UTF-8
        newUser['_password'] = str(pshash, encoding = "utf-8")
        newUser['_gender'] = newUser['_gender']
        newUser['_motoplate'] = ''
        newUser['_matchHistory'] = []
        newUser['_postHistory'] = []
        newUser['_requestHistory'] = []
        newUser['_rateHistory'] = []
        newUser['_lastLocation'] = {'lat': 25.1504516, 'lng': 121.780}
        newUser['_lastLogin'] = datetime.datetime.now()
        newUser['_token'] = False
        newUser['_notifications'] = []
        newUser['_new_notifications'] = True
        newUser['_want_mail'] = True
        newUser['_user_photo'] = '#'
        newUser['_license_photo'] = '#'
        if '_studentCard' in request.files:
            file = request.files['_studentCard']
            if file and allowed_file(file.filename):
                if not os.path.isdir(app.config['UPLOAD_FOLDER']+'/'+newUser['Account_name']):
                    os.mkdir(app.config['UPLOAD_FOLDER']+'/'+newUser['Account_name'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/'+newUser['Account_name'], newUser['Account_name']+"_studentCard.jpg"))
                newUser['_studentCard'] = newUser['Account_name']+"_studentCard.jpg"
        userid = userCol.insert_one(newUser).inserted_id
        if userid:
            title = "海大機車共乘系統註冊驗證"
            msg = "前往頁面填寫密碼以激活帳號 \n https://ntoumotogo.kangs.idv.tw/verify?id="+str(userid)+"&token="+str(pshash,encoding="utf-8") #激活網址
            thr = Thread(target=sendMail, args=[app, title,msg,newUser['_mail']]) #寄送驗證信
            thr.start()
        return redirect(url_for('checkAccountStatus'))
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


@app.route('/verify') #帳號激活頁面
def verify():
    user_id = request.args['id']
    token = request.args['token']
    if token and user_id:
        user = userCol.find_one({'_id':ObjectId(user_id)})
        if user:
            if user['_password'] == token:
                newtoken = random.random()
                session['NTOUmotoGoUser'] = user['Account_name'] #建立session
                session['NTOUmotoGoToken'] = newtoken
                session.permanent = True #設定session時效
                return render_template('26-setPassword.html')
    return redirect(url_for('homePage'))



@app.route('/setPsw',methods=['GET','POST'])
def setPsw():
    info = request.values.to_dict()
    psw = info['_password']
    pshash = bcrypt.hashpw(str(psw).encode('utf-8'), bcrypt.gensalt())#密碼加密 編碼:UTF-8
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    if user:
        userCol.update_one({'_id':user['_id']},{'$set':{'_password':str(pshash,encoding="utf-8")}})
        title = "海大機車共乘系統註冊通知"
        msg = "感謝您的註冊，請注意交通安全，平安回家，學業順遂，寫程式不會遇到bug\n姓名:"+user["_name"]+"\n帳號:"+user["Account_name"]+"\n電話:"+user["_phone"]
        thr = Thread(target=sendMail, args=[app, title,msg,user['_mail']]) #寄送郵件
        thr.start()
        thr2 = Thread(target=notifation, args=[app, user['_id'], user['_id'], 'system', '帳號創建成功~']) #呼叫通知
        thr2.start()
        token = 0
        while token == user['_token']:
            token = random.random()
        userCol.update({'_id' : user['_id']}, {"$set": {'_token' : token, '_lastLogin' : datetime.datetime.now()}}) #修改登入時間，登入狀態
        session['NTOUmotoGoUser'] = user['Account_name'] #建立session
        session['NTOUmotoGoToken'] = token
        session.permanent = True #設定session時效
        return redirect(url_for('homePage'))
    return '錯誤'
            

@app.route('/checkAccountStatus')
def checkAccountStatus():
    return render_template('25-checkAccountCreat.html')



    

