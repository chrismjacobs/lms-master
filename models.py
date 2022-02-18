from datetime import datetime, timedelta
from app import app, db, login_manager
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# verify token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meta import BaseConfig
SCHEMA = BaseConfig.SCHEMA

modDictUnits = {}
modDictAss = {}



#login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class ChatBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    chat = db.Column(db.String)
    response = db.Column(db.String)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # lower case becasue looking for table in database

    def __repr__(self):
        return f"ChatBox('{self.username}','{self.chat}','{self.response}')"
     # the foreignkey shows a db.relationship to User ID ('User' is the class whereas 'user' is the table name which would be lower case)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))

class AttendLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(20), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(), nullable=False, default='profiles/default.PNG')
    password = db.Column(db.String(60), nullable=False)
    device = db.Column (db.String(), nullable=False)
    extra = db.Column(db.Integer)



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


class Units(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    u1 = db.Column(db.Integer)
    u2 = db.Column(db.Integer)
    u3 = db.Column(db.Integer)
    u4 = db.Column(db.Integer)
    uA = db.Column(db.Integer)

class Exams(db.Model):
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

class Errors(db.Model):
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

class U001U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


class U002U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U003U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)

class U004U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)


# remove after intro class
if Units.query.filter_by(unit='00').first():
    if SCHEMA == 1 or SCHEMA == 2 or SCHEMA == 10:
        modDictUnits['00']=[None]
        modDictUnits['00'].append(U001U)
        modDictUnits['00'].append(U002U)
        modDictUnits['00'].append(U003U)
        modDictUnits['00'].append(U004U)

########################################

class U011U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['01']=[None]
modDictUnits['01'].append(U011U)

class U012U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['01'].append(U012U)

class U013U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['01'].append(U013U)

class U014U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['01'].append(U014U)



##########################################

class U021U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['02']=[None]
modDictUnits['02'].append(U021U)

class U022U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['02'].append(U022U)

class U023U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['02'].append(U023U)

class U024U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['02'].append(U024U)


##########################################

class U031U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['03']=[None]
modDictUnits['03'].append(U031U)

class U032U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['03'].append(U032U)

class U033U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['03'].append(U033U)

class U034U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['03'].append(U034U)

##########################################

class U041U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['04']=[None]
modDictUnits['04'].append(U041U)

class U042U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['04'].append(U042U)

class U043U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['04'].append(U043U)

class U044U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['04'].append(U044U)


##########################################

class U051U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['05']=[None]
modDictUnits['05'].append(U051U)

class U052U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['05'].append(U052U)

class U053U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['05'].append(U053U)

class U054U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['05'].append(U054U)



##########################################

class U061U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['06']=[None]
modDictUnits['06'].append(U061U)

class U062U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['06'].append(U062U)

class U063U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['06'].append(U063U)

class U064U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['06'].append(U064U)


##########################################

class U071U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['07']=[None]
modDictUnits['07'].append(U071U)

class U072U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['07'].append(U072U)

class U073U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['07'].append(U073U)

class U074U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['07'].append(U074U)


##########################################

class U081U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['08']=[None]
modDictUnits['08'].append(U081U)

class U082U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['08'].append(U082U)

class U083U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['08'].append(U083U)

class U084U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['08'].append(U084U)


if BaseConfig.SCHEMA == 9:
    class U091U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['09']=[None]
    modDictUnits['09'].append(U091U)

    class U092U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['09'].append(U092U)

    class U093U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['09'].append(U093U)

    class U094U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['09'].append(U094U)

    class U101U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['10']=[None]
    modDictUnits['10'].append(U101U)

    class U102U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['10'].append(U102U)

    class U103U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['10'].append(U103U)

    class U104U(BaseUnits):
        id = db.Column(db.Integer, primary_key=True)
    modDictUnits['10'].append(U104U)




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

class A00A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)


### remove after intro class
## intro edit
if Units.query.filter_by(unit='00').first():
    if SCHEMA == 1 or SCHEMA == 2 or SCHEMA == 10:
        modDictAss['00'] = A00A
        print('MOD DICTS INC 00')

class A01A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['01'] = A01A

class A02A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['02'] = A02A

class A03A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['03'] = A03A

class A04A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['04'] = A04A

class A05A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['05'] = A05A

class A06A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['06'] = A06A

class A07A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['07'] = A07A

class A08A (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['08'] = A08A

if BaseConfig.SCHEMA == 9:

    class A09A (BaseAss):
        id = db.Column(db.Integer, primary_key=True)
    modDictAss['09'] = A09A

    class A10A (BaseAss):
        id = db.Column(db.Integer, primary_key=True)
    modDictAss['10'] = A10A

    class A11A (BaseAss):
        id = db.Column(db.Integer, primary_key=True)
    modDictAss['11'] = A11A

    class A12A (BaseAss):
        id = db.Column(db.Integer, primary_key=True)
    modDictAss['12'] = A12A

##############################################


''' top of page

modDictUnits = {}  dictionary of all unit models   01 : [None, Mod1, Mod2, Mod3, Mod4]
modDictAss = {}  dictionary of all assignment models  01 : Model

'''


# used for admin rendering
listAss = []
for elements in modDictAss.values():
    listAss.append(elements)

listUnits = []
for elements in modDictUnits.values():
    for item in elements:
        if item != None:
            listUnits.append(item)



class Info ():
    ### for reading and workplace
    ass_mods_dict = modDictAss   #{'01': <class 'models.A01A'>, '02': <class 'models.A02A'>, '03': <class 'models.A03A'>,
    unit_mods_dict = modDictUnits
    unit_mods_list = listUnits
    ass_mods_list = listAss
    unit_name_list = modDictAss.keys()

    ### for ABC




class MyModelView(ModelView):
    def is_accessible(self):
        if BaseConfig.DEBUG == True:
            return True
        elif current_user.is_authenticated:
            if current_user.id == 1:
                return True
            else:
                return False
        else:
            return False

#https://danidee10.github.io/2016/11/14/flask-by-example-7.html



admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(ChatBox, db.session))
admin.add_view(MyModelView(Attendance, db.session))
admin.add_view(MyModelView(AttendLog, db.session))
admin.add_view(MyModelView(Units, db.session))

sList = [1,2,10,6,9]
if BaseConfig.SCHEMA in sList:
    admin.add_view(MyModelView(Exams, db.session))
    admin.add_view(MyModelView(Errors, db.session))
    for unit in listUnits:
        admin.add_view(MyModelView(unit, db.session))

    for ass in listAss:
        admin.add_view(MyModelView(ass, db.session))



elif BaseConfig.SCHEMA == 7: # movies
    admin.add_view(MyModelView(Exams, db.session))


    admin.add_view(MyModelView(U013U, db.session))
    admin.add_view(MyModelView(U014U, db.session))

    admin.add_view(MyModelView(U023U, db.session))
    admin.add_view(MyModelView(U024U, db.session))

    admin.add_view(MyModelView(U033U, db.session))
    admin.add_view(MyModelView(U034U, db.session))

    admin.add_view(MyModelView(U043U, db.session))
    admin.add_view(MyModelView(U044U, db.session))

    admin.add_view(MyModelView(U053U, db.session))
    admin.add_view(MyModelView(U054U, db.session))

    admin.add_view(MyModelView(U063U, db.session))
    admin.add_view(MyModelView(U064U, db.session))

    # projects - 1
    admin.add_view(MyModelView(U011U, db.session))
    admin.add_view(MyModelView(U021U, db.session))
    admin.add_view(MyModelView(U031U, db.session))

    # projects - 2
    admin.add_view(MyModelView(U012U, db.session))
    admin.add_view(MyModelView(U022U, db.session))
    admin.add_view(MyModelView(U032U, db.session))

    # effort regard
    admin.add_view(MyModelView(U001U, db.session))

    # listening - 1
    admin.add_view(MyModelView(U041U, db.session))

    # summary - 1
    admin.add_view(MyModelView(U051U, db.session))

    # reading test - 1
    admin.add_view(MyModelView(U061U, db.session))




elif BaseConfig.SCHEMA == 3:
    admin.add_view(MyModelView(Exams, db.session))
    admin.add_view(MyModelView(U001U, db.session))
    admin.add_view(MyModelView(U013U, db.session))
    admin.add_view(MyModelView(U023U, db.session))
    admin.add_view(MyModelView(U033U, db.session))
    admin.add_view(MyModelView(U043U, db.session))
    admin.add_view(MyModelView(U011U, db.session))
    admin.add_view(MyModelView(U012U, db.session))
    admin.add_view(MyModelView(U021U, db.session))
    admin.add_view(MyModelView(U031U, db.session))
    admin.add_view(MyModelView(U041U, db.session))
    admin.add_view(MyModelView(U051U, db.session))
    admin.add_view(MyModelView(U061U, db.session))
    admin.add_view(MyModelView(U071U, db.session))


elif BaseConfig.SCHEMA == 8:
    admin.add_view(MyModelView(Exams, db.session))
    admin.add_view(MyModelView(U071U, db.session))
    admin.add_view(MyModelView(U072U, db.session))
    admin.add_view(MyModelView(U073U, db.session))
    admin.add_view(MyModelView(U081U, db.session))
    admin.add_view(MyModelView(U082U, db.session))
    admin.add_view(MyModelView(U083U, db.session))


elif BaseConfig.SCHEMA == 5:
    admin.add_view(MyModelView(U011U, db.session))
    admin.add_view(MyModelView(U021U, db.session))

elif BaseConfig.SCHEMA == 4:
    admin.add_view(MyModelView(U011U, db.session))
    admin.add_view(MyModelView(U021U, db.session))




