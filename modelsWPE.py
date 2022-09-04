from datetime import datetime
from app import db


# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import BaseConfig

modDictUnits_WPE = {}
zeroDictUnits_WPE = {}

modDictAss_WPE = {}
zeroDictAss_WPE = {}


''' top of page

modDictUnits_WPE = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_WPE = {}  dictionary of all assignment models  01 : Model

'''



class ChatBox_WPE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    chat = db.Column(db.String)
    response = db.Column(db.String)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # lower case becasue looking for table in database

    def __repr__(self):
        return f"ChatBox('{self.username}','{self.chat}','{self.response}')"
     # the foreignkey shows a db.relationship to User ID ('User' is the class whereas 'user' is the table name which would be lower case)

class Attendance_WPE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))

class AttendLog_WPE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)


class Units_WPE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    u1 = db.Column(db.Integer)
    u2 = db.Column(db.Integer)
    u3 = db.Column(db.Integer)
    u4 = db.Column(db.Integer)
    uA = db.Column(db.Integer)

class Exams_WPE(db.Model):
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

class Errors_WPE(db.Model):
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

class U001U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


class U002U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U003U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U004U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


# remove after intro class

# print('Unit Filter', Units.query.filter_by(unit='00').first())



zeroDictUnits_WPE['00']=[None]
zeroDictUnits_WPE['00'].append(U001U_WPE)
zeroDictUnits_WPE['00'].append(U002U_WPE)
zeroDictUnits_WPE['00'].append(U003U_WPE)
zeroDictUnits_WPE['00'].append(U004U_WPE)

########################################

class U011U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['01']=[None]
modDictUnits_WPE['01'].append(U011U_WPE)

class U012U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['01'].append(U012U_WPE)

class U013U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['01'].append(U013U_WPE)

class U014U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['01'].append(U014U_WPE)



##########################################

class U021U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['02']=[None]
modDictUnits_WPE['02'].append(U021U_WPE)

class U022U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['02'].append(U022U_WPE)

class U023U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['02'].append(U023U_WPE)

class U024U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['02'].append(U024U_WPE)


##########################################

class U031U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['03']=[None]
modDictUnits_WPE['03'].append(U031U_WPE)

class U032U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['03'].append(U032U_WPE)

class U033U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['03'].append(U033U_WPE)

class U034U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['03'].append(U034U_WPE)

##########################################

class U041U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['04']=[None]
modDictUnits_WPE['04'].append(U041U_WPE)

class U042U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['04'].append(U042U_WPE)

class U043U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['04'].append(U043U_WPE)

class U044U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['04'].append(U044U_WPE)


##########################################

class U051U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['05']=[None]
modDictUnits_WPE['05'].append(U051U_WPE)

class U052U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['05'].append(U052U_WPE)

class U053U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['05'].append(U053U_WPE)

class U054U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['05'].append(U054U_WPE)



##########################################

class U061U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['06']=[None]
modDictUnits_WPE['06'].append(U061U_WPE)

class U062U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['06'].append(U062U_WPE)

class U063U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['06'].append(U063U_WPE)

class U064U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['06'].append(U064U_WPE)


##########################################

class U071U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['07']=[None]
modDictUnits_WPE['07'].append(U071U_WPE)

class U072U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['07'].append(U072U_WPE)

class U073U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['07'].append(U073U_WPE)

class U074U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['07'].append(U074U_WPE)


##########################################

class U081U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['08']=[None]
modDictUnits_WPE['08'].append(U081U_WPE)

class U082U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['08'].append(U082U_WPE)

class U083U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['08'].append(U083U_WPE)

class U084U_WPE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WPE['08'].append(U084U_WPE)


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

class A00A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)


### remove after intro class
## intro edit

### recode UNIT 00
zeroDictAss_WPE['00'] = A00A_WPE
# print('MOD ASS WPE 00')

class A01A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['01'] = A01A_WPE

class A02A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['02'] = A02A_WPE

class A03A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['03'] = A03A_WPE

class A04A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['04'] = A04A_WPE

class A05A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['05'] = A05A_WPE

class A06A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['06'] = A06A_WPE

class A07A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['07'] = A07A_WPE

class A08A_WPE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WPE['08'] = A08A_WPE


##############################################



