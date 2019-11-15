from flask-mail import Mail
from flask_mail import Message
from threading import Thread

app = Flask(__name__)
#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config.update(
    #gmail的設置
    MAIL_SERVER='smtp.gmail.com',
    MAIL_USE_SSL=True,
    MAIL_PROT=465,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = 'kangchiwei0988@gmail.com'
)
mail = Mail(app)

def sendMail(addr, msg_title, msg_sender, msg_body):
    #  主旨
    #msg_title = 'Hello It is Flask-Mail'
    #  寄件者，若參數有設置就不需再另外設置
    #msg_sender = 'Sender Mail@mail_domain.com'
    #  收件者，格式為list，否則報錯
    #msg_recipients = [addr]
    #  郵件內容
    #msg_body = 'Hey, I am mail body!'
    msg = Message(subject=msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients,
                  body=msg_body)
    #  mail.send:寄出郵件
      #  使用多線程
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    mail.send(msg)

def send_async_email(app, msg):
    #  下面有說明
    with app.app_context():
        mail.send(msg)


sendMail("lin1999213@gmail.com","flask_mail_test","生日快樂")