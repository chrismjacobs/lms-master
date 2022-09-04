from datetime import datetime, timedelta
from app import app, db, login_manager
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import BaseConfig

modDictUnits_ICC = {}
zeroDictUnits_ICC = {}

modDictAss_ICC = {}
zeroDictAss_ICC = {}


''' top of page

modDictUnits_ICC = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_ICC = {}  dictionary of all assignment models  01 : Model

'''


class ChatBox_ICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    chat = db.Column(db.String)
    response = db.Column(db.String)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # lower case becasue looking for table in database

    def __repr__(self):
        return f"ChatBox('{self.username}','{self.chat}','{self.response}')"
     # the foreignkey shows a db.relationship to User ID ('User' is the class whereas 'user' is the table name which would be lower case)

class Attendance_ICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))

class AttendLog_ICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)


class Units_ICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    u1 = db.Column(db.Integer)
    u2 = db.Column(db.Integer)
    u3 = db.Column(db.Integer)
    u4 = db.Column(db.Integer)
    uA = db.Column(db.Integer)

class Exams_ICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    j1 = db.Column(db.String)
    j2 = db.Column(db.String)
    j3 = db.Column(db.String)
    j4 = db.Column(db.String)
    j5 = db.Column(db.String)
    j6 = db.Column(db.String)
    j7 = db.Column(db.String)
    j8 = db.Column(db.String)

class Errors_ICC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #date_added = db.Column(db.DateTime, default=datetime.now)
    username = db.Column(db.String)
    err = db.Column(db.String)
    device = db.Column(db.String)
    mode = db.Column(db.String)
    unit = db.Column(db.String)




############### UNIT MODELS ###################################

class BaseUnits(db.Model):
    __abstract__ = True
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String)
    teamnumber = db.Column(db.Integer, unique=True)
    Ans01 = db.Column(db.String)
    Ans02 = db.Column(db.String)
    Ans03 = db.Column(db.String)
    Ans04 = db.Column(db.String)
    Ans05 = db.Column(db.String)
    Ans06 = db.Column(db.String)
    Ans07 = db.Column(db.String)
    Ans08 = db.Column(db.String)
    Grade = db.Column(db.Integer)
    Comment = db.Column(db.String)

class U001U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


class U002U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U003U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U004U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


# remove after intro class

# print('Unit Filter', Units.query.filter_by(unit='00').first())



modDictUnits_ICC['00']=[None]
modDictUnits_ICC['00'].append(U001U_ICC)
modDictUnits_ICC['00'].append(U002U_ICC)
modDictUnits_ICC['00'].append(U003U_ICC)
modDictUnits_ICC['00'].append(U004U_ICC)

########################################

class U011U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['01']=[None]
modDictUnits_ICC['01'].append(U011U_ICC)

class U012U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['01'].append(U012U_ICC)

class U013U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['01'].append(U013U_ICC)

class U014U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['01'].append(U014U_ICC)



##########################################

class U021U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['02']=[None]
modDictUnits_ICC['02'].append(U021U_ICC)

class U022U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['02'].append(U022U_ICC)

class U023U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['02'].append(U023U_ICC)

class U024U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['02'].append(U024U_ICC)


##########################################

class U031U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['03']=[None]
modDictUnits_ICC['03'].append(U031U_ICC)

class U032U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['03'].append(U032U_ICC)

class U033U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['03'].append(U033U_ICC)

class U034U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['03'].append(U034U_ICC)

##########################################

class U041U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['04']=[None]
modDictUnits_ICC['04'].append(U041U_ICC)

class U042U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['04'].append(U042U_ICC)

class U043U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['04'].append(U043U_ICC)

class U044U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['04'].append(U044U_ICC)


##########################################

class U051U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['05']=[None]
modDictUnits_ICC['05'].append(U051U_ICC)

class U052U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['05'].append(U052U_ICC)

class U053U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['05'].append(U053U_ICC)

class U054U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['05'].append(U054U_ICC)



##########################################

class U061U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['06']=[None]
modDictUnits_ICC['06'].append(U061U_ICC)

class U062U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['06'].append(U062U_ICC)

class U063U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['06'].append(U063U_ICC)

class U064U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['06'].append(U064U_ICC)


##########################################

class U071U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['07']=[None]
modDictUnits_ICC['07'].append(U071U_ICC)

class U072U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['07'].append(U072U_ICC)

class U073U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['07'].append(U073U_ICC)

class U074U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['07'].append(U074U_ICC)


##########################################

class U081U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['08']=[None]
modDictUnits_ICC['08'].append(U081U_ICC)

class U082U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['08'].append(U082U_ICC)

class U083U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['08'].append(U083U_ICC)

class U084U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['08'].append(U084U_ICC)

##############################

class U091U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['09']=[None]
modDictUnits_ICC['09'].append(U091U_ICC)

class U092U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['09'].append(U092U_ICC)

class U093U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['09'].append(U093U_ICC)

class U094U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['09'].append(U094U_ICC)

class U101U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['10']=[None]
modDictUnits_ICC['10'].append(U101U_ICC)

class U102U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['10'].append(U102U_ICC)

class U103U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['10'].append(U103U_ICC)

class U104U_ICC(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_ICC['10'].append(U104U_ICC)




############### ASSIGNMENT MODELS ###################################

class BaseAss(db.Model):
    __abstract__ = True
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String(300))
    AudioDataOne = db.Column(db.String)
    LengthOne = db.Column(db.Integer)
    AudioDataTwo = db.Column(db.String)
    LengthTwo = db.Column(db.Integer)
    Notes = db.Column(db.String)
    TextOne = db.Column(db.String)
    TextTwo = db.Column(db.String)
    DateStart= db.Column(db.DateTime)
    Grade = db.Column(db.Integer)
    Comment = db.Column(db.String)

class A00A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)


### remove after intro class
## intro edit

### recode UNIT 00
modDictAss_ICC['00'] = A00A_ICC

class A01A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['01'] = A01A_ICC

class A02A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['02'] = A02A_ICC

class A03A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['03'] = A03A_ICC

class A04A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['04'] = A04A_ICC

class A05A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['05'] = A05A_ICC

class A06A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['06'] = A06A_ICC

class A07A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['07'] = A07A_ICC

class A08A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['08'] = A08A_ICC

class A09A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['09'] = A09A_ICC

class A10A_ICC (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_ICC['10'] = A10A_ICC

# class A11A_ICC (BaseAss):
#     id = db.Column(db.Integer, primary_key=True)
# modDictAss_ICC['11'] = A11A_ICC

# class A12A_ICC (BaseAss):
#     id = db.Column(db.Integer, primary_key=True)
# modDictAss_ICC['12'] = A12A_ICC

##############################################


''' top of page

modDictUnits_ICC = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_ICC = {}  dictionary of all assignment models  01 : Model

'''

