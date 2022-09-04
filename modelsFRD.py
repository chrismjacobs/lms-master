from datetime import datetime, timedelta
from app import app, db, login_manager
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import BaseConfig

modDictUnits_FRD = {}
zeroDictUnits_FRD = {}

modDictAss_FRD = {}
zeroDictAss_FRD = {}


''' top of page

modDictUnits_FRD = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_FRD = {}  dictionary of all assignment models  01 : Model

'''



class ChatBox_FRD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    chat = db.Column(db.String)
    response = db.Column(db.String)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # lower case becasue looking for table in database

    def __repr__(self):
        return f"ChatBox('{self.username}','{self.chat}','{self.response}')"
     # the foreignkey shows a db.relationship to User ID ('User' is the class whereas 'user' is the table name which would be lower case)

class Attendance_FRD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))

class AttendLog_FRD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)


class Units_FRD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    u1 = db.Column(db.Integer)
    u2 = db.Column(db.Integer)
    u3 = db.Column(db.Integer)
    u4 = db.Column(db.Integer)
    uA = db.Column(db.Integer)

class Exams_FRD(db.Model):
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

class Errors_FRD(db.Model):
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

class U001U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


class U002U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U003U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U004U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


# remove after intro class

# print('Unit Filter', Units.query.filter_by(unit='00').first())



zeroDictUnits_FRD['00']=[None]
zeroDictUnits_FRD['00'].append(U001U_FRD)
zeroDictUnits_FRD['00'].append(U002U_FRD)
zeroDictUnits_FRD['00'].append(U003U_FRD)
zeroDictUnits_FRD['00'].append(U004U_FRD)

########################################

class U011U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['01']=[None]
modDictUnits_FRD['01'].append(U011U_FRD)

class U012U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['01'].append(U012U_FRD)

class U013U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['01'].append(U013U_FRD)

class U014U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['01'].append(U014U_FRD)



##########################################

class U021U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['02']=[None]
modDictUnits_FRD['02'].append(U021U_FRD)

class U022U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['02'].append(U022U_FRD)

class U023U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['02'].append(U023U_FRD)

class U024U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['02'].append(U024U_FRD)


##########################################

class U031U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['03']=[None]
modDictUnits_FRD['03'].append(U031U_FRD)

class U032U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['03'].append(U032U_FRD)

class U033U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['03'].append(U033U_FRD)

class U034U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['03'].append(U034U_FRD)

##########################################

class U041U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['04']=[None]
modDictUnits_FRD['04'].append(U041U_FRD)

class U042U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['04'].append(U042U_FRD)

class U043U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['04'].append(U043U_FRD)

class U044U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['04'].append(U044U_FRD)


##########################################

class U051U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['05']=[None]
modDictUnits_FRD['05'].append(U051U_FRD)

class U052U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['05'].append(U052U_FRD)

class U053U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['05'].append(U053U_FRD)

class U054U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['05'].append(U054U_FRD)



##########################################

class U061U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['06']=[None]
modDictUnits_FRD['06'].append(U061U_FRD)

class U062U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['06'].append(U062U_FRD)

class U063U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['06'].append(U063U_FRD)

class U064U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['06'].append(U064U_FRD)


##########################################

class U071U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['07']=[None]
modDictUnits_FRD['07'].append(U071U_FRD)

class U072U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['07'].append(U072U_FRD)

class U073U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['07'].append(U073U_FRD)

class U074U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['07'].append(U074U_FRD)


##########################################

class U081U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['08']=[None]
modDictUnits_FRD['08'].append(U081U_FRD)

class U082U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['08'].append(U082U_FRD)

class U083U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['08'].append(U083U_FRD)

class U084U_FRD(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_FRD['08'].append(U084U_FRD)


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

class A00A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)


### remove after intro class
## intro edit

### recode UNIT 00
zeroDictAss_FRD['00'] = A00A_FRD
print('MOD ASS 00')

class A01A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['01'] = A01A_FRD

class A02A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['02'] = A02A_FRD

class A03A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['03'] = A03A_FRD

class A04A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['04'] = A04A_FRD

class A05A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['05'] = A05A_FRD

class A06A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['06'] = A06A_FRD

class A07A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['07'] = A07A_FRD

class A08A_FRD (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_FRD['08'] = A08A_FRD


##############################################



