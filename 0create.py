
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from pprint import pprint
from models import *

def main(): 
    host = User(username='Chris', studentID='100000000', email='cjx02121981@gmail.com', image_file='profiles/Chris.jpg', password='tc0212', device='Heroku')
    db.session.add(host)
    db.session.commit()

    test = User(username='Test', studentID='100000001', email='cjx@gmail.com', image_file='profiles/default.PNG', password='test0212', device='None')
    db.session.add(test)
    db.session.commit()

    att = Attendance(username='Chris', studentID='100000000', teamnumber=97, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()


action = main()