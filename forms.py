from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed, FileRequired # what kind of files are allowed to be uploaded
from flask_login import current_user # now we can use this for the account update
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import *  #you forgot this and it took forever to notice the mistake!!!

#python classes will be forms
#then converted into forms in our html

class Attend(FlaskForm):
    attend = RadioField('Attendance', choices = [('On time', 'On time'), ('Late', 'Late')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired(), Length(9)])                  
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count')                                                  
    submit = SubmitField('Join')

class Chat(FlaskForm):
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])                  
    chat = StringField ('chat')
    response = StringField ('response')                         
    submit = SubmitField('Post Chat')


class RegistrationForm(FlaskForm):

    username = StringField ('Name in English', 
                                validators=[DataRequired(), Length(min=2, max=20)])    
    studentID = StringField ('Student ID (9 numbers)', 
                                validators=[DataRequired(), Length(9)])
    email = StringField('Email', 
                                validators=[DataRequired(), Email()] )  
    device = RadioField('Main Device', 
                                choices = [('Apple', 'Apple iphone'), ('Android', 'Android Phone'), ('Win', 'Windows Phone')])                                
    password = PasswordField('Password', 
                                validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password',  
                                        validators=[DataRequired(), EqualTo('password')] )
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
        user = User.query.filter_by(studentID=studentID.data).first()  
        if user:           
            raise ValidationError('That student ID already has an account, did you forget your password?')  

class LoginForm(FlaskForm):
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(9)])     
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

class AFU01(FlaskForm):

    Ans1 = StringField ('Q1', validators=[DataRequired(), Length(min=2, max=200)])    
    Ans2 = StringField ('Q2', validators=[DataRequired(), Length(min=2, max=200)])    
    Ans3 = StringField ('Q3', validators=[DataRequired(), Length(min=2, max=200)])     
    submit = SubmitField('Check Answers')
    update = SubmitField('Update Answers')

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


class UnitFS(FlaskForm):    
    Record1 = FileField ('Record 1', validators=[InputRequired(message='please upload record 1'), FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])    
    Answers1 = TextAreaField ('Answers 1', validators=[DataRequired(message='Please write your answers')])    
    Record2 = FileField ('Record 2', validators=[InputRequired(message='please upload record 2'), FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")]) 
    Answers2 = TextAreaField ('Answers 2', validators=[DataRequired(message='Please write your answers')])
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

