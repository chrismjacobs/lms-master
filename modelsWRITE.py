from datetime import datetime, timedelta
from app import app, db, login_manager
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import BaseConfig

modDictUnits_WRITE = {}
modDictAss_WRITE = {}



''' top of page

modDictUnits_WRITE = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss_WRITE = {}  dictionary of all assignment models  01 : Model

'''



class ChatBox_WRITE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    chat = db.Column(db.String)
    response = db.Column(db.String)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # lower case becasue looking for table in database

    def __repr__(self):
        return f"ChatBox('{self.username}','{self.chat}','{self.response}')"
     # the foreignkey shows a db.relationship to User ID ('User' is the class whereas 'user' is the table name which would be lower case)

class Attendance_WRITE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))

class AttendLog_WRITE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)


class Units_WRITE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    u1 = db.Column(db.Integer)
    u2 = db.Column(db.Integer)
    u3 = db.Column(db.Integer)
    u4 = db.Column(db.Integer)
    uA = db.Column(db.Integer)

class Exams_WRITE(db.Model):
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

class Errors_WRITE(db.Model):
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

class U001U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U002U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U003U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U004U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


# remove after intro class

# print('Unit Filter', Units.query.filter_by(unit='00').first())


modDictUnits_WRITE['00']=[None]
modDictUnits_WRITE['00'].append(U001U_WRITE)
modDictUnits_WRITE['00'].append(U002U_WRITE)
modDictUnits_WRITE['00'].append(U003U_WRITE)
modDictUnits_WRITE['00'].append(U004U_WRITE)

########################################

class U011U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['01']=[None]
modDictUnits_WRITE['01'].append(U011U_WRITE)

class U012U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['01'].append(U012U_WRITE)

class U013U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['01'].append(U013U_WRITE)

class U014U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['01'].append(U014U_WRITE)



##########################################

class U021U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['02']=[None]
modDictUnits_WRITE['02'].append(U021U_WRITE)

class U022U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['02'].append(U022U_WRITE)

class U023U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['02'].append(U023U_WRITE)

class U024U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['02'].append(U024U_WRITE)


##########################################

class U031U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['03']=[None]
modDictUnits_WRITE['03'].append(U031U_WRITE)

class U032U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['03'].append(U032U_WRITE)

class U033U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['03'].append(U033U_WRITE)

class U034U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['03'].append(U034U_WRITE)

##########################################

class U041U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['04']=[None]
modDictUnits_WRITE['04'].append(U041U_WRITE)

class U042U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['04'].append(U042U_WRITE)

class U043U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['04'].append(U043U_WRITE)

class U044U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['04'].append(U044U_WRITE)


##########################################

class U051U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['05']=[None]
modDictUnits_WRITE['05'].append(U051U_WRITE)

class U052U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['05'].append(U052U_WRITE)

class U053U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['05'].append(U053U_WRITE)

class U054U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['05'].append(U054U_WRITE)



##########################################

class U061U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['06']=[None]
modDictUnits_WRITE['06'].append(U061U_WRITE)

class U062U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['06'].append(U062U_WRITE)

class U063U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['06'].append(U063U_WRITE)

class U064U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['06'].append(U064U_WRITE)


##########################################

class U071U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['07']=[None]
modDictUnits_WRITE['07'].append(U071U_WRITE)

class U072U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['07'].append(U072U_WRITE)

class U073U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['07'].append(U073U_WRITE)

class U074U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['07'].append(U074U_WRITE)


##########################################

class U081U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['08']=[None]
modDictUnits_WRITE['08'].append(U081U_WRITE)

class U082U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['08'].append(U082U_WRITE)

class U083U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['08'].append(U083U_WRITE)

class U084U_WRITE(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits_WRITE['08'].append(U084U_WRITE)


############### ASSIGNMENT MODELS ###################################

class BaseAss(db.Model):
    __abstract__ = True
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String)
    partner =  db.Column(db.String)
    number = db.Column(db.Integer, unique=True)
    info = db.Column(db.String)
    plan = db.Column(db.String)
    draft = db.Column(db.String)
    revise = db.Column(db.String)
    publish = db.Column(db.String)
    grade = db.Column(db.Integer)
    comment = db.Column(db.String)
    extra = db.Column(db.String)



# class A00A_WRITE (BaseAss):
#     id = db.Column(db.Integer, primary_key=True)


# ### remove after intro class
# ## intro edit

# ### recode UNIT 00
# modDictAss_WRITE['00'] = A00A_WRITE
# # print('MOD ASS FRD 00')

class A01A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['01'] = A01A_WRITE

class A02A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['02'] = A02A_WRITE

class A03A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['03'] = A03A_WRITE

class A04A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['04'] = A04A_WRITE

class A05A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['05'] = A05A_WRITE

class A06A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['06'] = A06A_WRITE

class A07A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['07'] = A07A_WRITE

class A08A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['08'] = A08A_WRITE

class A09A_WRITE (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss_WRITE['09'] = A09A_WRITE


##############################################



