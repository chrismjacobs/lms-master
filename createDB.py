
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from pprint import pprint
from models import ChatBox, AttendLog, Attendance, User
from models import Units, Exams, Errors
from aws import dbpassword


## neccessary for reading intro class only
#from models import U001U, U002U, U003U, U003U, A00A

from models import U011U, U012U, U013U, U014U
from models import U021U, U022U, U023U, U024U
from models import U031U, U032U, U033U, U034U
from models import U041U, U042U, U043U, U044U
from models import U051U, U052U, U053U, U054U
from models import U061U, U062U, U063U, U064U
from models import U071U, U072U, U073U, U074U
from models import U081U, U082U, U083U, U084U

#from models import U091U, U092U, U093U, U094U
#from models import U101U, U102U, U103U, U104U
#from models import U111U, U112U, U113U, U114U
#from models import U121U, U122U, U123U, U124U


from models import A01A, A02A, A03A, A04A, A05A, A06A, A07A, A08A
#from models import A09A, A10A, A11A, A12A

db.create_all()

def main():
    host = User(username='Chris', studentID='100000000', email='cjx02121981@gmail.com', image_file='profiles/Chris.jpg', password=dbpassword, device='Heroku')
    db.session.add(host)
    db.session.commit()

    test = User(username='Test', studentID='100000001', email='cjx@gmail.com', image_file='profiles/default.PNG', password='test0212', device='None')
    db.session.add(test)
    db.session.commit()

    att = Attendance(username='Chris', studentID='100000000', teamnumber=97, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()

    att = AttendLog(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


action = main()