import os
from .. import app
from .backend import userCol, homePage, rateCol
from flask import request,session,redirect,jsonify,url_for
from werkzeug.utils import secure_filename
import datetime
from ._socket import notifation
from threading import Thread
from bson.objectid import ObjectId

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/setInfo',methods = ['GET','POST'])
def setInfo():
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    if user:
        info = request.values.to_dict()
        print(info)
        print(type(info))
        userCol.update({'_id':user['_id']},{'$set': {'_name' : info['_name'], '_gender' : info['_gender'],'_phone' : info['_phone'], '_mail' : info['_mail']}})
        thr = Thread(target=notifation, args=[app, user['_id'], user['_id'], 'user', '個人資料修改成功']) #呼叫通知函示
        thr.start()
        print(request.files)
        if '_user_photo' in request.files:
            file = request.files['_user_photo']
            if file and allowed_file(file.filename):
                if not os.path.isdir(app.config['UPLOAD_FOLDER']+'/'+user['Account_name']):
                    os.mkdir(app.config['UPLOAD_FOLDER']+'/'+user['Account_name'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/'+user['Account_name'], user['Account_name']+"_user_photo.jpg"))
                userCol.update_one({'_id':user['_id']},{'$set':{'_user_photo' : user['Account_name']+"_user_photo.jpg"}})
        if '_license_photo' in request.files:
            file = request.files['_license_photo']
            if file and allowed_file(file.filename):
                if not os.path.isdir(app.config['UPLOAD_FOLDER']+'/'+user['Account_name']):
                    os.mkdir(app.config['UPLOAD_FOLDER']+'/'+user['Account_name'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/'+user['Account_name'], user['Account_name']+"_license_photo.jpg"))
                userCol.update_one({'_id':user['_id']},{'$set':{'_license_photo' : user['Account_name']+"_license_photo.jpg"}})
    return redirect(url_for('homePage'))

#個人頁面拿資料
@app.route('/getUserData',methods=['GET','POST'])
def getUserData():
    #tmp = request.get_json(silent=True)
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    rate = []

    for rateId in user['_rateHistory']:#將每個評價的星數裝進陣列
        rateObj = rateCol.find_one({'_id' : ObjectId(rateId) })
        rateNum = rateObj['rate_range']
        rate.append(rateNum)

    userData = {
        '_name':user['_name'],
        '_mail': user['_mail'],
        '_gender':user['_gender'],
        '_motoplate':user['_motoplate'],
        '_rateHistory':rate,
        '_phone':user['_phone'],
        '_user_photo':user['_user_photo'],
        '_license_photo':user['_license_photo'],
        'Account_name':session['NTOUmotoGoUser']
        }
    
    return jsonify(userData)

#拿別人個人頁面資料
@app.route('/getAnotherUserData',methods=['GET','POST'])
def getAnotherUata():
    info = request.get_json(silent=True)
    rate = []
    user = userCol.find_one({'_id':ObjectId(info['_id'])})
    for rateId in user['_rateHistory']:#將每個評價的星數裝進陣列
        rateObj = rateCol.find_one({'_id' : ObjectId(rateId) })
        rateNum = rateObj['rate_range']
        rate.append(rateNum)

    userData = {
        '_name':user['_name'],
        '_mail': user['_mail'],
        '_gender':user['_gender'],
        '_motoplate':user['_motoplate'],
        '_phone':user['_phone'],
        '_user_photo':user['_user_photo'],
        '_license_photo':user['_license_photo'],
        '_rate':rate,
        }
    
    return jsonify(userData)


#設置email和通知的開關
@app.route('/getNotiMail',methods=['GET','POST'])
def getNotiMail():
    tmp = request.get_json(silent=True)
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    result = {}
    result.update({'_new_notifications':user['_new_notifications']})
    result.update({'_want_mail':user['_want_mail']})
    
    return jsonify(result)

    
#設置email和通知的開關
@app.route('/setNotiMail',methods=['GET','POST'])
def setNotiMail():
    tmp = request.get_json(silent=True)
    userCol.update_one({'Account_name' : session['NTOUmotoGoUser']},{'$set':{'_new_notifications' : tmp['_new_notifications']}})
    userCol.update_one({'Account_name' : session['NTOUmotoGoUser']},{'$set':{'_want_mail' : tmp['_want_mail']}})
    


