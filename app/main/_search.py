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
from .backend import userCol,postCol,rateCol
from math import radians, cos, sin, asin, sqrt


#按照地點搜尋
@app.route('/search',methods=['GET','POST'])
def search():
    tmp = request.get_json(silent=True)
    
    results = [] 
    resultsId = set()    
    setGoto = set()
    setLoca = set()
    setGoto.add(tmp["post_goto"])
    setLoca.add(tmp["post_location"])

    setA = {"瑞芳車站"}
    setB = {"山海觀"}
    setC = {"海洋大學體育館","海洋大學濱海校門","海洋大學祥豐校門","中正路加油站"}
    setD = {"基隆市立圖書館","長榮桂冠","基隆市政府","海洋廣場","基隆火車站","廟口","基隆女子高級中學"}
    setE = {"微笑台北","深溪路愛買","海中天","巴賽隆納","海洋世界","新豐麥當勞"}
    setF = {"基隆海事","祥豐市場"}


    if setLoca == (setLoca & setA):
        setLoca = setA
    elif setLoca == (setLoca & setB):
        setLoca = setB
    elif setLoca == (setLoca & setC):
        setLoca = setC
    elif setLoca == (setLoca & setD):
        setLoca = setD
    elif setLoca == (setLoca & setE):
        setLoca = setE
    elif setLoca == (setLoca & setF):
        setLoca = setF

    if setGoto == (setGoto & setA):
        setGoto = setA
    elif setGoto == (setGoto & setB):
        setGoto = setB
    elif setGoto == (setGoto & setC):
        setGoto = setC
    elif setGoto == (setGoto & setD):
        setGoto = setD
    elif setGoto == (setGoto & setE):
        setGoto = setE
    elif setGoto == (setGoto & setF):
        setGoto = setF

   
    for Loca in setLoca:
        postloca = postCol.find({'post_location':Loca,'post_getOnTime' : {'$gt' : datetime.datetime.now()}}).sort('post_getOnTime')
        for x in postloca:
            resultsId.add(str(x['_id']))

    for goto in setGoto:
        postgo = postCol.find({'post_goto':goto,'post_getOnTime' : {'$gt' : datetime.datetime.now()}}).sort('post_getOnTime')
        for x in postgo:
            resultsId.add(str(x['_id']))
        

    myId = userCol.find_one({'Account_name' : session['NTOUmotoGoUser']})['_id']


    for id in resultsId:
        result = postCol.find_one({'_id' : ObjectId(id)})
        result['_id'] = str(result['_id'])
        result['owner_id'] = str(result['owner_id'])
        result['post_name'] = userCol.find_one({'_id' : ObjectId(result['owner_id'])})['_name']
        result['yourID'] = str(myId)
        results.append(result)

    return jsonify(results)


@app.route('/searchName',methods=['GET','POST'])
def searchName():
    info = request.get_json(silent=True)
    
    userArray = userCol.find({'_name':info['_name']})
    userDataArray = []


    for user in userArray:
        rate = []

        for rateId in user['_rateHistory']:#將每個評價的星數裝進陣列
            rateObj = rateCol.find_one({'_id' : ObjectId(rateId) })
            rateNum = rateObj['rate_range']
            rate.append(rateNum)

        userData = {
            '_id':str(user['_id']),
            '_name':user['_name'],
            '_mail': user['_mail'],
            '_gender':user['_gender'],
            '_motoplate':user['_motoplate'],
            '_phone':user['_phone'],
            '_user_photo':user['_user_photo'],
            '_license_photo':user['_license_photo'],
            '_rate':rate,
            }
        
        userDataArray.append(userData)
    
    return jsonify(userDataArray)
    
    
# location = {
#     "瑞芳車站":{"lat":25.108789,"lng":121.805969},
#     "山海觀":{"lat":25.137714,"lng":121.794330},
#     "海洋大學體育館":{"lat":25.150322,"lng":121.77931},
#     "海洋大學濱海校門":{"lat":25.150527,"lng":121.775998},
#     "海洋大學祥豐校門":{"lat":25.150886,"lng":121.772456},
#     "中正路加油站":{"lat":25.151556,"lng":121.767483},
#     "基隆市立圖書館":{"lat":25.140944,"lng":121.759003},
#     "長榮桂冠":{"lat":25.135144,"lng":121.746160},
#     "基隆市政府":{"lat":25.131649,"lng":121.744662},
#     "海洋廣場":{"lat":25.131043,"lng":121.741354},
#     "基隆火車站":{"lat":25.131691,"lng":121.738281},
#     "廟口":{"lat":25.128318,"lng":121.743584},
#     "基隆女子高級中學":{"lat":25.128624,"lng":121.759173},
#     "微笑台北":{"lat":25.128331,"lng":121.779216},
#     "深溪路愛買":{"lat":25.133204,"lng":121.782300},
#     "海中天":{"lat":25.135051,"lng":121.784516},
#     "巴賽隆納":{"lat":25.135727,"lng":121.786233},
#     "海洋世界":{"lat":25.135889,"lng":121.786977},
#     "新豐麥當勞":{"lat":25.136430,"lng":121.788084},
#     "和平島和平國小":{"lat":25.155660,"lng":121.766066},
#     "基隆海事":{"lat":25.147726,"lng":121.771737},
#     "祥豐市場":{"lat":25.142020,"lng":121.763944}
# }
    
# goto = {
#     "瑞芳車站":{"lat":25.108789,"lng":121.805969},
#     "山海觀":{"lat":25.137714,"lng":121.794330},
#     "海洋大學體育館":{"lat":25.150322,"lng":121.77931},
#     "海洋大學濱海校門":{"lat":25.150527,"lng":121.775998},
#     "海洋大學祥豐校門":{"lat":25.150886,"lng":121.772456},
#     "中正路加油站":{"lat":25.151556,"lng":121.767483},
#     "基隆市立圖書館":{"lat":25.140944,"lng":121.759003},
#     "長榮桂冠":{"lat":25.135144,"lng":121.746160},
#     "基隆市政府":{"lat":25.131649,"lng":121.744662},
#     "海洋廣場":{"lat":25.131043,"lng":121.741354},
#     "基隆火車站":{"lat":25.131691,"lng":121.738281},
#     "廟口":{"lat":25.128318,"lng":121.743584},
#     "基隆女子高級中學":{"lat":25.128624,"lng":121.759173},
#     "微笑台北":{"lat":25.128331,"lng":121.779216},
#     "深溪路愛買":{"lat":25.133204,"lng":121.782300},
#     "海中天":{"lat":25.135051,"lng":121.784516},
#     "巴賽隆納":{"lat":25.135727,"lng":121.786233},
#     "海洋世界":{"lat":25.135889,"lng":121.786977},
#     "新豐麥當勞":{"lat":25.136430,"lng":121.788084},
#     "和平島和平國小":{"lat":25.155660,"lng":121.766066},
#     "基隆海事":{"lat":25.147726,"lng":121.771737},
#     "祥豐市場":{"lat":25.142020,"lng":121.763944}
# }

# #計算兩經緯度距離,haversine
# def haversine(lat1, lng1, lat2, lng2):
#     lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2]) 
#     dlng = lng2 - lng1
#     dlat = lat2 - lat1 
#     a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
#     c = 2 * asin(sqrt(a)) 
#     r = 6378137 #地球半徑公尺
#     return c * r
            
    

    
        