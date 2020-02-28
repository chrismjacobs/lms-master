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


class RegistrationForm(FlaskForm):

    username = StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])    
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired(), Length(9)])
    email = StringField('Email', validators=[DataRequired(), Email()] )  
    bookcode = StringField('bookcode')
    device = RadioField('Main Device', choices = [('Apple', 'Apple iphone'), ('Android', 'Android Phone'), ('Win', 'Windows Phone')])                                
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
            raise ValidationError('9 numbers; no S') 
        user = User.query.filter_by(studentID=studentID.data).first()  
        if user:           
            raise ValidationError('That student ID already has an account, did you forget your password?') 
        
        if SCHEMA < 3: 
            def validate_bookcode(self, bookcode):             
                bc1 = studentID.data[0] 
                bc2 = int(studentID.data[7])*2
                bc3 = int(studentID.data[8])*3
                bcFinal = bc1 + str(bc2) + str(bc3)
                print(bcFinal) 
                if bookcode.data != '12345': 
                    pass      
                elif bookcode.data != bcFinal:
                    raise ValidationError('Incorrect BookCode - please see your instructor')  

class LoginForm(FlaskForm):
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(min=2, max=9)])     
    password = PasswordField('Password', validators=[DataRequired()]) 
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

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

