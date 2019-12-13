import os
from .. import app
from flask_mail import Mail
from flask_mail import Message
from threading import Thread

#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config.update(
    #gmail的設置
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PROT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = ('海大機車共乘系統',os.environ.get('MAIL_PASSWORD'))
)
mail = Mail(app)

def sendMail(app,msg_title,msg_body,addr):
    #  主旨addr, msg_title, msg_body
    #msg_title = 'Hello It is Flask-Mail'
    #  寄件者，若參數有設置就不需再另外設置
    #msg_sender = 'Sender Mail@mail_domain.com'
    #  收件者，格式為list，否則報錯
    #msg_recipients = [addr]
    #  郵件內容
    #msg_body = 'Hey, I am mail body!'
    with app.app_context():
        msg = Message(subject=msg_title,
                    recipients=[addr],
                    )
        msg.body = msg_body
        mail.send(msg)
    
        
