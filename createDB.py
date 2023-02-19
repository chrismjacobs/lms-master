
from app import db

from models import *
from aws import dbpassword
import json

def drop():
    db.drop_all()
    return False

drop()

db.create_all()

def main():
    #return False

    semester = str(2)
    ''' change jMaker global as well '''

    host = User(username='Chris',
                studentID='100000000',
                email='cjx02121981@gmail.com',
                image_file='profiles/Chris.jpg',
                password=dbpassword,
                device=json.dumps('{}'),
                semester=semester,
                #icc=1,
                frd=1,
                wpe=1,
                #lnc=1,
                vtm=1,
                png=1,
                app=1,
                extra=10
                )
    db.session.add(host)
    db.session.commit()

    test = User(username='Test',
                studentID='100000001',
                email='test@gmail.com',
                image_file='profiles/default.PNG',
                password='Test0212',
                device='None'
                )
    db.session.add(test)
    db.session.commit()

    att = Attendance_FRD(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_FRD(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()

    att = Attendance_WPE(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_WPE(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()

    att = Attendance_ICC(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_ICC(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


    att = Attendance_LNC(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_LNC(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()

    att = Attendance_VTM(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_VTM(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()

    att = Attendance_WRITE(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_WRITE(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()

    att = Attendance_NME(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_NME(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()

    att = Attendance_PENG(username='Chris', studentID='100000000', teamnumber=97, teamsize=4, teamcount=10, unit='RR')
    db.session.add(att)
    db.session.commit()

    att = AttendLog_PENG(username='Chris', studentID='100000000')
    db.session.add(att)
    db.session.commit()


action = main()