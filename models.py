from datetime import datetime, timedelta
# from http.client import UNSUPPORTED_MEDIA_TYPE
# from msilib import AMD64
from app import app, db, login_manager
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import *
from modelsFRD import *
from modelsICC import *
from modelsLNC import *
from modelsWPE import *
from modelsVTM import *

def getSchema():
    SCHEMA = 0
    try:
        SCHEMA = int(current_user.schema)
    except:
        SCHEMA = 0

    return SCHEMA


def getModels():
    SCHEMA = getSchema()
    # print('getModels', SCHEMA)

    chatbox = [None, ChatBox_FRD, ChatBox_WPE, ChatBox_ICC, 'ChatBox_PENG', ChatBox_LNC, ChatBox_VTM, 'ChatBox_NME']
    attend = [None, Attendance_FRD, Attendance_WPE, Attendance_ICC, 'Attendance_PENG', Attendance_LNC, Attendance_VTM, 'Attendance_NME']
    attl = [None, AttendLog_FRD, AttendLog_WPE, AttendLog_ICC, 'AttendLog_PENG', AttendLog_LNC, AttendLog_VTM, 'AttendLog_NME']
    units = [None, Units_FRD, Units_WPE, Units_ICC, 'Units_PENG', Units_LNC, Units_VTM, 'Units_NME']
    exams = [None, Exams_FRD, Exams_WPE, Exams_ICC, 'Exams_PENG', Exams_LNC, Exams_VTM, 'Exams_NME']
    errors = [None, Errors_FRD, Errors_WPE, Errors_ICC, 'Errors_PENG', Errors_LNC, Errors_VTM, 'Errors_NME']

    return {
        'ChatBox_' : chatbox[SCHEMA],
        'Attendance_' : attend[SCHEMA],
        'AttendLog_' : attl[SCHEMA],
        'Units_' : units[SCHEMA],
        'Exams_' : exams[SCHEMA],
        'Errors_' : errors[SCHEMA]
    }


def getInfo():
    SCHEMA = getSchema()

    infoDict = {
        'mda' : [{}, modDictAss_FRD, modDictAss_WPE, modDictAss_ICC, 'modDictAss_PENG', modDictAss_LNC, modDictAss_VTM, 'modDictAss_NME'],
        'mdu' : [{}, modDictUnits_FRD, modDictUnits_WPE, modDictUnits_ICC, 'modDictUnits_PENG', modDictUnits_LNC, modDictUnits_VTM, 'modDictUnits_NME'],
    }


    modDictAss  = infoDict['mda'][SCHEMA]
    modDictUnits = infoDict['mdu'][SCHEMA]

    print('mod dict ass', modDictAss)

    if getModels()['Units_'] and not getModels()['Units_'].query.filter_by(unit='00').first():
        try:
            print('try delete 00')
            del modDictUnits['00']
            del modDictAss['00']
        except:
            print('delete 00 fail')



    # print('infoDict', SCHEMA, modDictUnits) #modDictAss, zeroDictAss, zeroDictUnits

    # used for admin rendering
    listAss = []
    for elements in modDictAss.values():
        listAss.append(elements)

    listUnits = []
    for elements in modDictUnits.values():
        # print('elements', elements, modDictUnits.values())
        for item in elements:
            if item != None:
                listUnits.append(item)

    # zeroAss = []
    # for elements in zeroDictAss.values():
    #     zeroAss.append(elements)

    # zeroUnits = []
    # for elements in zeroDictUnits.values():
    #     for item in elements:
    #         if item != None:
    #             zeroUnits.append(item)

    return {
        'aModsDict' : modDictAss,
        'uModsDict' : modDictUnits,
        'unit_mods_list' : listUnits,
        'ass_mods_list' : listAss,
    }





#login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(20), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(), nullable=False, default='profiles/default.PNG')
    password = db.Column(db.String(60), nullable=False)
    device = db.Column (db.String(), nullable=False)
    frd = db.Column(db.Integer, default=0)
    wpe = db.Column(db.Integer, default=0)
    icc = db.Column(db.Integer, default=0)
    lnc = db.Column(db.Integer, default=0)
    vtm = db.Column(db.Integer, default=0)
    png = db.Column(db.Integer, default=0)
    semester = db.Column(db.Integer)
    schema = db.Column(db.Integer)
    extra = db.Column(db.Integer)
    condition = db.Column(db.Integer, default=0)
    info = db.Column(db.String(), default='')


    def get_reset_token(self, expires_sec=1800):
        expires_sec = 1800
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod #tell python not to expect that self parameter as an argument, just accepting the token
    def verify_reset_token(token):
        expires_sec = 1800
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):  # double underscore method or dunder method, marks the data, this is how it is printed
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Users(db.Model): #import the model
    id = db.Column(db.Integer, primary_key=True) #kind of value and the key unique to the user
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String(20), nullable=False) #must be a unique name and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)
    studentID = db.Column(db.String(20))
    vocab = db.Column(db.String(), nullable=False, default='generalW')
    password = db.Column(db.String(60), nullable=False)
    school = db.Column(db.String(30))
    classroom = db.Column(db.String(20))
    extraStr = db.Column(db.String())
    extraInfo = db.Column(db.String())
    extraInt = db.Column(db.Integer())


class MyModelView(ModelView):
    def is_accessible(self):
        if BaseConfig.DEBUG == True:
            return True
        elif current_user.is_authenticated:
            if current_user.id == 1 or current_user.id == 2:
                return True
            else:
                return False
        else:
            return False

#https://danidee10.github.io/2016/11/14/flask-by-example-7.html



admin = Admin(app, 'Example: Layout-BS3', base_template='admin.html', template_mode='bootstrap3')



admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Users, db.session))

mList1 = [
            Attendance_FRD, Attendance_WPE, Attendance_ICC, Attendance_LNC, Attendance_VTM,
            AttendLog_FRD, AttendLog_WPE, AttendLog_ICC, AttendLog_LNC, AttendLog_VTM,
            Units_FRD, Units_WPE, Units_ICC, Units_LNC, Units_VTM,
            Exams_FRD, Exams_WPE, Exams_ICC, Exams_LNC, Exams_VTM
         ]

for m in mList1:
    admin.add_view(MyModelView(m, db.session))


mList2 = [modDictAss_FRD, modDictAss_WPE, modDictAss_ICC, modDictAss_LNC, modDictAss_VTM]
mList3 = [modDictUnits_FRD, modDictUnits_WPE, modDictUnits_ICC, modDictUnits_LNC, modDictUnits_VTM]

for s in mList3:
    for d in s:
        for m in s[d]:
            if m:
                admin.add_view(MyModelView(m, db.session))

for d in mList2:
    for x in d:
        admin.add_view(MyModelView(d[x], db.session))


mList4 = [
            ChatBox_FRD, ChatBox_WPE, ChatBox_ICC, ChatBox_LNC, ChatBox_VTM,
            Errors_FRD, Errors_WPE, Errors_ICC, Errors_LNC, Errors_VTM
         ]

for m in mList4:
    admin.add_view(MyModelView(m, db.session))








