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

