from datetime import datetime, timedelta
from app import app, db, login_manager
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import BaseConfig

modDictUnits_VTM = {}
zeroDictUnits_VTM = {}

modDictAss_VTM = {}
zeroDictAss_VTM = {}


''' top of page

modDictUnits_VTM = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_VTM = {}  dictionary of all assignment models  01 : Model

'''


class ChatBox_VTM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    chat = db.Column(db.String)
    response = db.Column(db.String)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # lower case becasue looking for table in database

    def __repr__(self):
        return f"ChatBox('{self.username}','{self.chat}','{self.response}')"
     # the foreignkey shows a db.relationship to User ID ('User' is the class whereas 'user' is the table name which would be lower case)

class Attendance_VTM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))

class AttendLog_VTM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)


class Units_VTM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    u1 = db.Column(db.Integer)
    u2 = db.Column(db.Integer)
    u3 = db.Column(db.Integer)
    u4 = db.Column(db.Integer)
    uA = db.Column(db.Integer)

class Exams_VTM(db.Model):
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

class Errors_VTM(db.Model):
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

class U001U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


class U002U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U003U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U004U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


# remove after intro class

# print('Unit Filter', Units.query.filter_by(unit='00').first())



zeroDictUnits_VTM['00']=[None]
zeroDictUnits_VTM['00'].append(U001U_VTM)
zeroDictUnits_VTM['00'].append(U002U_VTM)
zeroDictUnits_VTM['00'].append(U003U_VTM)
zeroDictUnits_VTM['00'].append(U004U_VTM)

########################################

class U011U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['01']=[None]
modDictUnits_VTM['01'].append(U011U_VTM)

class U012U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['01'].append(U012U_VTM)

class U013U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['01'].append(U013U_VTM)

class U014U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['01'].append(U014U_VTM)



##########################################

class U021U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['02']=[None]
modDictUnits_VTM['02'].append(U021U_VTM)

class U022U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['02'].append(U022U_VTM)

class U023U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['02'].append(U023U_VTM)

class U024U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['02'].append(U024U_VTM)


##########################################

class U031U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['03']=[None]
modDictUnits_VTM['03'].append(U031U_VTM)

class U032U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['03'].append(U032U_VTM)

class U033U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['03'].append(U033U_VTM)

class U034U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['03'].append(U034U_VTM)

##########################################

class U041U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['04']=[None]
modDictUnits_VTM['04'].append(U041U_VTM)

class U042U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['04'].append(U042U_VTM)

class U043U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['04'].append(U043U_VTM)

class U044U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['04'].append(U044U_VTM)


##########################################

class U051U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['05']=[None]
modDictUnits_VTM['05'].append(U051U_VTM)

class U052U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['05'].append(U052U_VTM)

class U053U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['05'].append(U053U_VTM)

class U054U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['05'].append(U054U_VTM)



##########################################

class U061U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['06']=[None]
modDictUnits_VTM['06'].append(U061U_VTM)

class U062U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['06'].append(U062U_VTM)

class U063U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['06'].append(U063U_VTM)

class U064U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['06'].append(U064U_VTM)


##########################################

class U071U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['07']=[None]
modDictUnits_VTM['07'].append(U071U_VTM)

class U072U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['07'].append(U072U_VTM)

class U073U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['07'].append(U073U_VTM)

class U074U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['07'].append(U074U_VTM)


##########################################

class U081U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['08']=[None]
modDictUnits_VTM['08'].append(U081U_VTM)

class U082U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['08'].append(U082U_VTM)

class U083U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['08'].append(U083U_VTM)

class U084U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['08'].append(U084U_VTM)

##############################

class U091U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['09']=[None]
modDictUnits_VTM['09'].append(U091U_VTM)

class U092U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['09'].append(U092U_VTM)

class U093U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['09'].append(U093U_VTM)

class U094U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['09'].append(U094U_VTM)

class U101U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['10']=[None]
modDictUnits_VTM['10'].append(U101U_VTM)

class U102U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['10'].append(U102U_VTM)

class U103U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['10'].append(U103U_VTM)

class U104U_VTM(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_VTM['10'].append(U104U_VTM)




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

class A00A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)


### remove after intro class
## intro edit

### recode UNIT 00
zeroDictAss_VTM['00'] = A00A_VTM

class A01A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['01'] = A01A_VTM

class A02A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['02'] = A02A_VTM

class A03A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['03'] = A03A_VTM

class A04A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['04'] = A04A_VTM

class A05A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['05'] = A05A_VTM

class A06A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['06'] = A06A_VTM

class A07A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['07'] = A07A_VTM

class A08A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['08'] = A08A_VTM

class A09A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['09'] = A09A_VTM

class A10A_VTM (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_VTM['10'] = A10A_VTM

# class A11A_VTM (BaseAss):
#     id = db.Column(db.Integer, primary_key=True)
# modDictAss_VTM['11'] = A11A_VTM

# class A12A_VTM (BaseAss):
#     id = db.Column(db.Integer, primary_key=True)
# modDictAss_VTM['12'] = A12A_VTM

##############################################


''' top of page

modDictUnits_VTM = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_VTM = {}  dictionary of all assignment models  01 : Model

'''

