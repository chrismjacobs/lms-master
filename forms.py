from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import User
from meta import BaseConfig
SCHEMA = BaseConfig.SCHEMA


class Attend(FlaskForm):
    attend = RadioField('Attendance', choices = [('On time', 'On time'), ('Late', 'Late')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired(), Length(9)])
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count')
    submit = SubmitField('Join Class')

class AttendLate(FlaskForm):
    attend = RadioField('Attendance', choices = [('Late', 'Late'), ('2nd Class', '2nd Class')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired(), Length(9)])
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count')
    submit = SubmitField('Join')

class AttendInst(FlaskForm):
    attend = StringField ('Notice')
    username =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(9)])
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

bookcodeList = {
    "120000000":"6788",
    "120433033":"6789",
    "120554057":"6790",
    "120554127":"6791",
    "120654045":"6792",
    "120654052":"6793",
    "120654055":"6794",
    "120654065":"6795",
    "120654068":"6796",
    "120754060":"6797",
    "120754067":"6798",
    "120754070":"6799",
    "120754071":"6800",
    "120850904":"6801",
    "120850905":"6802",
    "120850909":"6803",
    "120850910":"6804",
    "120850915":"6805",
    "120850921":"6806",
    "120850922":"6807",
    "120850923":"6808",
    "120850933":"6809",
    "120850938":"6810",
    "120854014":"6811",
    "120954001":"6812",
    "120954002":"6813",
    "120954003":"6814",
    "120954004":"6815",
    "120954005":"6816",
    "120954006":"6817",
    "120954007":"6818",
    "120954008":"6819",
    "120954010":"6820",
    "120954011":"6821",
    "120954012":"6822",
    "120954014":"6823",
    "120954015":"6824",
    "120954016":"6825",
    "120954018":"6826",
    "120954020":"6827",
    "120954021":"6828",
    "120954022":"6829",
    "120954023":"6830",
    "120954026":"6831",
    "120954027":"6832",
    "120954028":"6833",
    "120954029":"6834",
    "120954030":"6835",
    "320952401":"6836",
    "320952402":"6837",
    "320952403":"6838",
    "320952404":"6839",
    "320952405":"6840",
    "320952406":"6841",
    "320952407":"6842",
    "320952408":"6843",
    "320952409":"6844",
    "320952410":"6845",
    "320952411":"6846",
    "320952412":"6847",
    "320952414":"6848",
    "120433033":"4634",
    "120454131":"4635",
    "120554060":"4636",
    "120554127":"4637",
    "120654033":"4638",
    "120654064":"4639",
    "120754067":"4640",
    "120754071":"4641",
    "120854002":"4642",
    "120854003":"4643",
    "120854005":"4644",
    "120854007":"4645",
    "120854008":"4646",
    "120854009":"4647",
    "120854010":"4648",
    "120854011":"4649",
    "120854012":"7139",
    "120854013":"7140",
    "120854015":"7141",
    "120854016":"7142",
    "120854017":"7143",
    "120854018":"7144",
    "120854019":"7145",
    "120854021":"7146",
    "120854022":"7147",
    "120854023":"7148",
    "120854025":"7149",
    "120854026":"7150",
    "120854028":"7151",
    "120854030":"7152",
    "120854031":"7153",
    "120854032":"7154",
    "120854034":"7155",
    "120854037":"7156",
    "120854040":"7157",
    "120854045":"1654",
    "120854047":"1655",
    "120854048":"1656",
    "120854049":"1657",
    "120854050":"1658",
    "120854052":"1659",
    "120854054":"1660",
    "120854055":"1661",
    "120854056":"1662",
    "120854058":"1663",
    "120854059":"1664",
    "320852201":"1665",
    "320852202":"1666",
    "320852203":"1667",
    "320852204":"1668",
    "320852205":"1669",
    "320852208":"1670",
    "320852209":"1671",
    "320852210":"1672",
    "320852215":"1673",
    "320852216":"1674",
    "320852219":"1675",
    "320852220":"1676",
    "320852221":"1677",
    "320852221":"1678"
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

