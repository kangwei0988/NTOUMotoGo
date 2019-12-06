from app import socketio, app

socketio.run(app,host ='0.0.0.0',port=443,keyfile='key.pem', certfile='cert.pem')