from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import User, Users
from app import bcrypt
import json




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


def getCourseRadios():

    radioList = [
        ('1', 'Freshman Reading'),
        # ('2', 'Workplace English'),
        # ('3', 'Intercultural Communication'),
        # ('4', 'Presentation English'),
        ('5', 'Language and Culture'),
        # ('6', 'Vietnam Class'),
        ('0', 'My Course is not on the list'),
        ]

    return radioList

    # master = User.query.filter_by(id=1).first()

    # print('master', master, master.extra)

    # if master.extra == 0:
    #     return [('0', 'No Course')]
    # elif master.extra == 10:
    #     return radioList
    # else:
    #     return [radioList[0], radioList[master.extra]]


class RegistrationForm(FlaskForm):
    username = StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(min=2, max=20)])
    course = RadioField ('Course', validators=[DataRequired()], choices = getCourseRadios() )
    email = StringField('Email', validators=[DataRequired(), Email()] )
    device = RadioField('Main Device', choices = [('Apple', 'Apple iphone'), ('Android', 'Android Phone')])
    password = PasswordField('Password', validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')] )
    submit = SubmitField('Join')

    def validate_username(self, username):  # the field is username
        user = User.query.filter_by(username=username.data).first()  #User was imported at the top # first means just find first instance?
        if user:  # meaning if True
            raise ValidationError('Another student is using that username, please change or add family name')  # ValidationError needs to be imported from wtforms

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email has an account already, did you forget your password?')

        vocab_app = Users.query.filter_by(email=email.data).first()
        if vocab_app:
            raise ValidationError('There is a small problem, please see/contact your instructor')

    def validate_course(self, course):
        if int(course.data) == 0:
            raise ValidationError('If your course is not in the list right now then please contact your teacher or wait for the class to start')


    def validate_studentID(self, studentID):
        try:
            int(studentID.data)
        except:
            raise ValidationError('Numbers only (no S)')
        user = User.query.filter_by(studentID=studentID.data).first()
        if user:
            raise ValidationError('That student ID already has an account, if you are trying to join more than one course please contact your teacher for help')


class LoginForm(FlaskForm):
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(min=2, max=9)])
    course = RadioField ('Course', validators=[DataRequired()], choices = [('5', 'Language and Culture'), ('1', 'Freshman Reading'), ('2', 'Workplace English'), ('3', 'Intercultural Communication'), ('6', 'Vietnam Class')])
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
            if '000000' in studentID.data:
                pass
            else:
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

