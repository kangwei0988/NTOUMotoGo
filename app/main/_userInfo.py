import os
from .. import app
from .backend import userCol, homePage
from flask import request,session,redirect,jsonify,url_for
from werkzeug.utils import secure_filename
import datetime

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/setInfo',methods = ['GET','POST'])
def setInfo():
    print('set')
    user = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})
    if user:
        info = request.values.to_dict()
        print(info)
        print(type(info))
        userCol.update({'_id':user['_id']},{'$set': {'_name' : info['_name'], '_gender' : info['_gender'],'_phone' : info['_phone'], '_mail' : info['_mail']}})
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

