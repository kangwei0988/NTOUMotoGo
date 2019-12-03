import os
from .. import app
from .backend import userCol
from flask import request,session
from werkzeug.utils import secure_filename
import datetime

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/setInfo',methods = ['GET','POST'])
def setInfo():
    user = userCol.find_one({'_id',session['NTOUmotoGoUser']})
    info = request.values.to_dict()
    userCol.update_one({'_id',user['_id']},{'$set',info})
    if 'user_photo' in request.files:
        file = request.files['user_photo']
        if file and allowed_file(file.filename):
            fileName = datetime.datetime.now()
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/'+userCol['Account_name'], str(datetime.datetime.now(fileName))+".jpg"))
            userCol.update_one({'_id',user['_id']},{'$set',{'_user_photo' : str(fileName)+".jpg"}})
    if 'user_photo' in request.files:
        file = request.files['user_photo']
        if file and allowed_file(file.filename):
            fileName = datetime.datetime.now()
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/'+userCol['Account_name'], str(datetime.datetime.now(fileName))+".jpg"))
            userCol.update_one({'_id',user['_id']},{'$set',{'_license_photo' : str(fileName)+".jpg"}})

