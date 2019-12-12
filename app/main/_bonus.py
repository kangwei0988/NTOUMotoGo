from .. import app
from .backend import userCol, postCol, requestCol
from flask import request,session,jsonify
import datetime
from bson.objectid import ObjectId
import pytz

@app.route('/checkBusy', methods=['POST'])
def checkbusy():
    data = request.get_json()
    user = userCol.find_one({'Account_name':session['NTOUmotoGoUser']})
    time = ''
    if data['type'] == 'post':
        time = datetime.datetime.fromisoformat(data['target'])
    elif data['type'] == 'requ':
        _requ = requestCol.find_one({'_id':ObjectId(data['target'])})
        if _requ:
            _post = postCol.find_one({'_id':_requ['post_id']})
            if _post:
                time = _post['post_getOnTime']
            else:
                return jsonify({'result':False})
        else:
            return jsonify({'result':False})
    dt = datetime.timedelta(minutes=30)
    upTime = time + dt
    downTime = time - dt
    #upTime.replace(tzinfo=None) #this funtion 'replace' is no longer available
    for requid in user['_matchHistory'] :
        requ = requestCol.find_one({'_id':ObjectId(requid)})
        if requ:
            post = postCol.find_one({'_id' : ObjectId(requ['post_id'])})
            if post:
                postTime = datetime.datetime.fromisoformat(str(post['post_getOnTime'])+'+00:00')
                if downTime < postTime and postTime < upTime:
                    return jsonify({'result':True})
    return jsonify({'result':False})
    
    #posts = postCol.find({'post_type':post_type,'post_matched':False,'post_getOnTime' : {'$gt' : datetime.datetime.now()+datetime.timedelta(minutes=30)}}).sort('post_getOnTime')