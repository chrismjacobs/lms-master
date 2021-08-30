from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import User
from meta import BaseConfig
from app import bcrypt
SCHEMA = BaseConfig.SCHEMA


class Attend(FlaskForm):
    attend = RadioField('Attendance', choices = [('On time', 'On time'), ('Late', 'Late')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired()])
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count')
    submit = SubmitField('Join Class')

class AttendLate(FlaskForm):
    attend = RadioField('Attendance', choices = [('Late', 'Late'), ('2nd Class', '2nd Class')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired()])
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count')
    submit = SubmitField('Join')

class AttendInst(FlaskForm):
    attend = StringField ('Notice')
    username =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID', validators=[DataRequired()])
    teamnumber = IntegerField ('Status (50-review; 97-disabled; 98-open; 99-late; 100-clear)')
    #RadioField('Status', choices = [(97, 'disabled'), (98, 'open'), (99, 'late'), (100, 'clear')])
    teamcount = IntegerField ('Team Count')
    teamsize = IntegerField ('Team Size (0 for no teams)')
    #RadioField('Size', choices = [(0, '0'), (2, '2'), (3, '3'), (4, '4')])
    unit = StringField ('unit(2) eg 01 or MT', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Start Class')


class Chat(FlaskForm):
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    chat = StringField ('chat')
    response = StringField ('response')
    submit = SubmitField('Post Chat')



bookcodeID = None
loginID = None

bookcodeList = {
                "120454000":"2400",
                "120454132":"2500",
                "120512128":"2501",
                "120554038":"2502",
                "120554127":"2503",
                "120615233":"2504",
                "120654029":"2505",
                "120654033":"2506",
                "120654045":"2507",
                "120654051":"2508",
                "120654052":"2509",
                "120654065":"2510",
                "120754057":"2511",
                "120754060":"2512",
                "120754062":"2513",
                "120754067":"2514",
                "120754070":"2515",
                "120754071":"2516",
                "120754502":"2517",
                "120815126":"2518",
                "120815130":"2519",
                "120815154":"2520",
                "120815158":"2521",
                "120850905":"2522",
                "120850910":"2523",
                "120850915":"2524",
                "120850921":"2525",
                "120850923":"2526",
                "120850938":"2527",
                "120854014":"2528",
                "120854030":"2529",
                "120854059":"2530",
                "120954001":"2531",
                "120954002":"2532",
                "120954003":"2533",
                "120954004":"2534",
                "120954005":"2535",
                "120954006":"2536",
                "120954007":"2537",
                "120954008":"2538",
                "120954010":"2539",
                "120954011":"2540",
                "120954012":"2541",
                "120954014":"2542",
                "120954015":"2543",
                "120954016":"2544",
                "120954018":"2545",
                "120954021":"2546",
                "120954022":"2547",
                "120954023":"2548",
                "120954026":"2549",
                "120954027":"2550",
                "120954028":"2551",
                "120954029":"2552",
                "120954030":"2553",
                "320816131":"2554",
                "320952401":"2555",
                "320952403":"2556",
                "320952404":"2557",
                "320952405":"2558",
                "320952406":"2559",
                "320952407":"2560",
                "320952408":"2561",
                "320952409":"2562",
                "320952410":"2563",
                "320952411":"2564",
                "320952412":"2565",
                "320952414":"2566",
                "320952415":"2567",
                "120254173":"8963",
                "120433033":"8964",
                "120454132":"8965",
                "120554127":"8966",
                "120634205":"8967",
                "120635130":"8968",
                "120654006":"8969",
                "120674003":"8970",
                "120736507":"8971",
                "120754060":"8972",
                "120754071":"8973",
                "120854002":"8974",
                "120854003":"8975",
                "120854005":"8976",
                "120854007":"8977",
                "120854009":"8978",
                "120854010":"8979",
                "120854011":"8980",
                "120854012":"8981",
                "120854013":"8982",
                "120854015":"8983",
                "120854016":"8984",
                "120854017":"8985",
                "120854018":"8986",
                "120854019":"8987",
                "120854021":"8988",
                "120854022":"8989",
                "120854023":"8990",
                "120854025":"8991",
                "120854026":"8992",
                "120854028":"8993",
                "120854029":"8994",
                "120854030":"8995",
                "120854031":"8996",
                "120854032":"8997",
                "120854034":"8998",
                "120854037":"8999",
                "120854040":"9000",
                "120854045":"9001",
                "120854047":"9002",
                "120854048":"9003",
                "120854049":"9004",
                "120854050":"9005",
                "120854052":"9006",
                "120854055":"9007",
                "120854056":"9008",
                "120854058":"9009",
                "120854059":"9010",
                "120854061":"9011",
                "320852201":"9012",
                "320852203":"9013",
                "320852204":"9014",
                "320852205":"9015",
                "320852208":"9016",
                "320852209":"9017",
                "320852210":"9018",
                "320852215":"9019",
                "320852216":"9020",
                "320852219":"9021",
                "320852220":"9022",
                "320852221":"9023"
            }


class RegistrationForm(FlaskForm):


    username = StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()] )
    bookcode = StringField('bookcode')
    device = RadioField('Main Device', choices = [('Apple', 'Apple iphone'), ('Android', 'Android Phone')])
    password = PasswordField('Password', validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')] )
    submit = SubmitField('Join')

    def validate_username(self, username):  # the field is username
        user = User.query.filter_by(username=username.data).first()  #User was imported at the top # first means just find first instance?
        if user:  # meaning if True
            raise ValidationError('Another student has that username, please add family name')  # ValidationError needs to be imported from wtforms

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email has an account already, did you forget your password?')


    def validate_studentID(self, studentID):
        try:
            int(studentID.data)
        except:
            raise ValidationError('Numbers only')
        user = User.query.filter_by(studentID=studentID.data).first()
        if user:
            raise ValidationError('That student ID already has an account, did you forget your password?')

        if SCHEMA < 3:
            print('BOOKCODE TEST')
            global bookcodeID
            bookcodeID = studentID.data

    def validate_bookcode(self, bookcode):
        if SCHEMA < 3:
            print(bookcodeID)
            print(bookcode)
            if bookcode.data == '9009':
                pass
            elif bookcodeList[bookcodeID] != bookcode.data:
                raise ValidationError('Incorrect BookCode - please see your instructor')
        else:
            pass

class LoginForm(FlaskForm):
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(min=2, max=9)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_studentID(self, studentID):
        try:
            print(studentID.data)
            int(studentID.data)
            pass
        except:
            raise ValidationError('This should be your ID with no `s`')
        try:
            int(User.query.filter_by(studentID=studentID.data).first().studentID)
            pass
        except:
            raise ValidationError('This ID has not been registered yet')

        global loginID
        loginID = studentID.data

    # def validate_password(self, password):
    #     try:
    #         user = User.query.filter_by(studentID=loginID).first()
    #         print('USER', user)
    #         print('Password', password.data)
    #         print('Password', user.password)
    #         print(bcrypt.check_password_hash(user.password, password.data))
    #         pass
    #     except:
    #         raise ValidationError('There is a problem with this password')




class ForgotForm(FlaskForm):
    email = StringField ('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email, contact your instructor')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')] )
    submit = SubmitField('Set New Password')

class UpdateAccountForm(FlaskForm):
    #username = StringField ('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()] )
    picture = FileField ('Change Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):  # the field is username
        if username.data != current_user.username: # if the updated one is the same then no need to validate
            user = User.query.filter_by(username=username.data).first()  #User was imported at the top # first means just find first instance?
            if user:  # meaning if True
                raise ValidationError('That user name has been used already, please add another letter')  # ValidationError needs to be imported from wtforms

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email has an account already, did you forget your password?')

    def validate_studentID(self, studentID):
        if studentID.data != current_user.student.ID:
            user = User.query.filter_by(studentID=studentID.data).first()
            if user:
                raise ValidationError('That student ID already has an account, did you forget your password?')


class UnitF1(FlaskForm):
    Ans01 = TextAreaField ('Q1')
    Ans02 = TextAreaField ('Q2')
    Ans03 = TextAreaField ('Q3')
    Ans04 = TextAreaField ('Q4')
    Ans05 = TextAreaField ('Q5')
    Ans06 = TextAreaField ('Q6')
    Ans07 = TextAreaField ('Q7')
    Ans08 = TextAreaField ('Q8')
    submit = SubmitField('Submit Answers')


class AssBasic(FlaskForm):
    AudioDataOne = StringField('audioDataOne')
    AudioDataTwo = StringField('audioDataTwo')
    LengthOne = IntegerField('lengthOne')
    LengthTwo = IntegerField('lengthTwo')
    Notes = TextAreaField('Notes')
    TextOne = TextAreaField('One')
    TextTwo = TextAreaField('Two')
    TextThr = TextAreaField('Three')
    Submit = SubmitField('Submit')

