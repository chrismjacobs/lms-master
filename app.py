from flask import Flask, render_template   #app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy  #needed for app initialization (see below - db)
from flask_bcrypt import Bcrypt  #needed for password storage
from flask_login import LoginManager, current_user #needed for login
from flask_mail import Mail
from meta import BaseConfig

app = Flask(__name__)
app.config.from_object('meta.BaseConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = 'login' # if user isn't logged in it will redirect to login page
login_manager.login_message_category = 'info'

app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'chrisflask0212@gmail.com',
    MAIL_PASSWORD = BaseConfig.MAIL_PASSWORD,
    MAIL_SUPPRESS_SEND = False,
    MAIL_DEBUG = True,
    TESTING = False
))


mail = Mail(app)

# if SCHEMA == 2:
#     import redis
#     REDIS_PASSWORD = BaseConfig.REDIS_PASSWORD
#     redisData = redis.Redis(
#         host = 'redis-12011.c54.ap-northeast-1-2.ec2.cloud.redislabs.com',
#         port = 12011,
#         password = REDIS_PASSWORD,
#         decode_responses = True # get python freiendlt format
#     )


from routesInst import *
from routesAdmin import *


from routesUser import *
from routesPart import *
## from routesNME import *
# from routesFOOD import *
# from routesPENG import *



if __name__ == '__main__':
    app.run()

