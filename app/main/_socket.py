from .. import socketio
from flask_socketio import emit, join_room, leave_room
from .backend import userCol,requestCol
import urllib.parse
from bson.objectid import ObjectId
from flask import session,request
import datetime
from threading import Thread
from ._mail import sendMail

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

# 通知新推播(對象id，新內容)
# 用以下方式呼叫
# thr = Thread(target=notifation, args=[app, notiid, targetId, Type, msg) #呼叫通知函示
# thr.start()
def notifation(app, notiid, targetId, Type, msg):#(app:context上下文， notiid:對象id,string or objectid型態都行， targetId:相關事件的id， Type:'post,requ,rate,system'， msg:要顯示訊息)
    with app.app_context():
        target = userCol.find_one({'_id' : ObjectId(notiid)})
        notifications = target['_notifications']
        notifications.insert(0,{'_target':str(targetId),'_type':Type,'_msg':msg,'_msgTime':datetime.datetime.now()})
        userCol.update({'_id' : target['_id']}, {"$set": {'_notifications' : notifications}})
        if target['_want_mail'] and Type != 'system':
            title = '你在海大機車共乘系統中有一則新信息'
            sendMail(app,title,msg,target['_mail'])
        socketio.emit('news', {'num' : len(notifications)}, room = target['Account_name']) #向room推播
###########################################################################

#############################聊天室功能#####################################
#加入聊天室
@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = message['room']
    join_room(room)
    requ = requestCol.find_one({'_id' : ObjectId(room)})
    tarName = ''
    if requ['pas_id'] == userCol.find_one({'Account_name' : session['NTOUmotoGoUser']}):
        tarName = userCol.find_one({'_id':ObjectId(requ['dri_id'])})['_name']
    else:
        tarName = userCol.find_one({'_id' : ObjectId(requ['pas_id'])})['_name']
    emit('status', {'msg':  requ['chat_record'], 'tarName' : tarName}, room=room)
#傳送訊息
@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = message['room']
    msg = requestCol.find_one({'_id' : ObjectId(room)})['chat_record']
    name = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})['_name']
    uncodeMsg = urllib.parse.unquote(message['msg'])
    print(uncodeMsg)
    newMsg = name + ':' + uncodeMsg +'\n'+ str(datetime.datetime.now())
    msg += newMsg + '\n'
    requestCol.update_one({'_id' : ObjectId(room)}, {'$set' :{'chat_record' : msg}})
    emit('message', {'msg': newMsg}, room=room)
#離開
@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = message['room']
    leave_room(room)
########################################################################