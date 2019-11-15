import os
from flask import Flask
from flask_mail import Mail
from flask_mail import Message
from threading import Thread

app = Flask(__name__)
#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config.update(
    #gmail的設置
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PROT=587,
    MAIL_USE_TLS=True,

    MAIL_USERNAME='kangchiwei0988@gmail.com',
    MAIL_PASSWORD='kang0988089437',
    MAIL_DEFAULT_SENDER = ('admin','kangchiwei0988@gmail.com')
)
mail = Mail(app)
@app.route('/')
def sendMail():
    #  主旨addr, msg_title, msg_body
    #msg_title = 'Hello It is Flask-Mail'
    #  寄件者，若參數有設置就不需再另外設置
    #msg_sender = 'Sender Mail@mail_domain.com'
    #  收件者，格式為list，否則報錯
    #msg_recipients = [addr]
    addrList = ['lin1999213@gmail.com']
    #  郵件內容
    #msg_body = 'Hey, I am mail body!'
    msg = Message(subject="flask_mail_test",
                  recipients=addrList,
                  )
    msg.body = "happy birthday"
    #msg.body = msg_body
    #  mail.send:寄出郵件
      #  使用多線程
    #thr = Thread(target=send_async_email, args=[app, msg])
    #thr.start()
    mail.send(msg)
    return 'You Send Mail by Flask-Mail Success!!'

def send_async_email(app, msg):
    #  下面有說明
    with app.app_context():
        mail.send(msg)

app.run(host ='127.0.0.1',port = '5000')