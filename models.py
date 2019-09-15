from datetime import datetime, timedelta
from app import app, db, login_manager
from flask_login import UserMixin, current_user # this imports current user, authentication, get id (all the login attributes)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

modDictUnits = {}
modDictAss = {}
modListSL = [0]


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
    unit = db.Column(db.String(2))    
 
class AttendLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)     
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9),nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)
   
class User(db.Model, UserMixin): #import the model
    id = db.Column(db.Integer, primary_key=True) #kind of value and the key unique to the user
    username =  db.Column(db.String(20), unique=True, nullable=False) #must be a unique name and cannot be null
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(), nullable=False, default='profiles/default.PNG') #images will be hashed to 20 and images could be the same
    password = db.Column(db.String(60), nullable=False)    
    device = db.Column (db.String(), nullable=False)
    #hometown = db.Column (db.String()) 
    #fName = db.Column (db.String())


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

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(), unique=True, nullable=False) 
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    assignments = db.Column(db.Integer)
    units = db.Column(db.Integer)  
    attend = db.Column(db.Integer)
    bonus = db.Column(db.Integer)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)

class Sources(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    unit = db.Column(db.String) 
    part = db.Column(db.String)
    form = db.Column(db.String)
    qnum = db.Column(db.String)
    classdate = db.Column(db.DateTime)
    duedate = db.Column(db.DateTime)  
    title = db.Column(db.String)
    notes = db.Column(db.String)
    questions = db.Column(db.String)     
    assSource = db.Column(db.String)
    assForm = db.Column(db.Integer)
    assDate = db.Column(db.DateTime)
    openSet = db.Column(db.Integer)
    openReset = db.Column(db.Integer)
    extra1 = db.Column(db.String)
    extra2 = db.Column(db.String)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    week = db.Column(db.Integer)
    unit = db.Column(db.String) 
    date = db.Column(db.DateTime)    
    topic = db.Column(db.String)
    goalOne = db.Column(db.String)
    goalTwo = db.Column(db.String)
    activity = db.Column(db.String)
    linkOne = db.Column(db.String)
    linkTwo = db.Column(db.String)    
    embed = db.Column(db.String)
    openSet = db.Column(db.Integer)    
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)   

    
############### UNIT MODELS ###################################

class U555(db.Model):
    id = db.Column(db.Integer, primary_key=True)     
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    unit = db.Column(db.String)
    record1 = db.Column(db.String)
    answers1 = db.Column(db.String)
    record2 = db.Column(db.String)
    answers2 = db.Column(db.String)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)

class BaseUnits(db.Model):
    __abstract__ = True
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username =  db.Column(db.String)
    teamnumber = db.Column(db.Integer)
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
modDictUnits['00']=[None]
modDictUnits['00'].append(U001U)

#class U004U(BaseUnits):
    #id = db.Column(db.Integer, primary_key=True)
#modDictUnits['00'].append(U004U)
####  SL  #####
#modListSL.append(U004U)

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
####  SL  #####
modListSL.append(U014U)

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
####  SL  #####
modListSL.append(U024U)

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
####  SL  #####
modListSL.append(U034U)
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
####  SL  #####
modListSL.append(U044U)

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
####  SL  #####
modListSL.append(U054U)

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
####  SL  #####
modListSL.append(U064U)

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
####  SL  #####
modListSL.append(U074U)

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
####  SL  #####
modListSL.append(U084U)

##########################################

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
####  SL  #####
modListSL.append(U094U)

##########################################

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
####  SL  #####
modListSL.append(U104U)

##########################################

class U111U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True) 
modDictUnits['11']=[None]
modDictUnits['11'].append(U111U) 

class U112U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)  
modDictUnits['11'].append(U112U) 

class U113U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True) 
modDictUnits['11'].append(U113U)

class U114U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['11'].append(U114U)
####  SL  #####
modListSL.append(U114U)

##########################################

class U121U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True) 
modDictUnits['12']=[None]
modDictUnits['12'].append(U121U) 

class U122U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)  
modDictUnits['12'].append(U122U) 

class U123U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True) 
modDictUnits['12'].append(U123U)

class U124U(BaseUnits):
    id = db.Column(db.Integer, primary_key=True)
modDictUnits['12'].append(U124U)
####  SL  #####
modListSL.append(U124U)



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
    TextThr = db.Column(db.String) 
    TextFor= db.Column(db.String)
    DateStart= db.Column(db.DateTime)
    Grade = db.Column(db.Integer)
    Comment = db.Column(db.String)  


class Ass00 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['00'] = Ass00

class Ass01 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['01'] = Ass01

class Ass02 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['02'] = Ass02

class Ass03 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['03'] = Ass03

class Ass04 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['04'] = Ass04

class Ass05 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['05'] = Ass05

class Ass06 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['06'] = Ass06

class Ass07 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['07'] = Ass07

class Ass08 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['08'] = Ass08

class Ass09 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['09'] = Ass09

class Ass10 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['10'] = Ass10

class Ass11 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['11'] = Ass11

class Ass12 (BaseAss):
    id = db.Column(db.Integer, primary_key=True)
modDictAss['12'] = Ass12

##############################################


listAss = modDictAss.values()

listUnits = []
for values in modDictUnits.values():
    for items in values:
        if items != None:
            listUnits.append(items)

modDictAssList = {}
for item in modDictAss:    
    modDictAssList[item] = ([modDictAss[item]])

class Info ():
    modDictAss = modDictAss
    modDictUnits = modDictUnits 
    modListUnits = listUnits
    modListAss = listUnits
    modListSL = modListSL    
    ansDict = modDictAssList
    unitList = modDictAss.keys()  ###['00', '01', .....]
    

class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.id == 1:
                return True
            else:
                return False
        else:
            return False

    #https://danidee10.github.io/2016/11/14/flask-by-example-7.html

    
#$2b$12$79FM1YLMP/rLWfznq2iHFelcQ9I6svAZtLFN9.2i1RDQXxq1oPvUS


admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Sources, db.session))
admin.add_view(MyModelView(Course, db.session))
admin.add_view(MyModelView(ChatBox, db.session))
admin.add_view(MyModelView(Attendance, db.session))
admin.add_view(MyModelView(AttendLog, db.session))
admin.add_view(MyModelView(Grades, db.session))
admin.add_view(MyModelView(U555, db.session))

for unit in listUnits:
    admin.add_view(MyModelView(unit, db.session))

for ass in listAss:
    admin.add_view(MyModelView(ass, db.session))
