
from app import db

from models import *
from aws import dbpassword
import json


db.create_all()

def main():

    semester = str(1)
    ''' change jMaker global as well '''

    host = User(username='Chris',
                studentID='100000000',
                email='cjx02121981@gmail.com',
                image_file='profiles/Chris.jpg',
                password=dbpassword,
                device=json.dumps('{}'),
                semester=semester,
                icc=1,
                frd=1,
                wpe=1,
                lnc=1,
                vtm=1,
                png=1
                )
    db.session.add(host)
    db.session.commit()

    duo = User(username='Duo',
                studentID='100000001',
                email='duo@gmail.com',
                image_file='profiles/default.PNG',
                password='Duo0212',
                device='None',
                semester=semester,
                icc=1,
                frd=1,
                wpe=1,
                lnc=1,
                vtm=1,
                png=1
                )
    db.session.add(duo)
    db.session.commit()

    test = User(username='Test',
                studentID='100000002',
                email='test@gmail.com',
                image_file='profiles/default.PNG',
                password='Test0212',
                device='None'
                )
    db.session.add(test)
    db.session.commit()

    att = Attendance_FRD(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_FRD(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


    att = Attendance_WPE(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_WPE(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


    att = Attendance_ICC(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_ICC(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


    att = Attendance_LNC(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_LNC(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


    att = Attendance_VTM(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='01')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_VTM(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


action = main()