import sys, boto3, random, base64, os, secrets, httplib2
import datetime
from random import randint
from PIL import Image  # first pip install Pillow
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import ForgotForm, PasswordResetForm, RegistrationForm, LoginForm, UpdateAccountForm 
from models import User, Grades, ChatBox, Info
from flask_mail import Message
try:
    from aws import Settings    
    s3_resource = Settings.s3_resource  
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME
    COLOR_SCHEMA = Settings.COLOR_SCHEMA    
except:
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME'] 
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 
    print('SUCCESS',s3_resource, S3_LOCATION, S3_BUCKET_NAME, COLOR_SCHEMA)



# set the color schema ## https://htmlcolorcodes.com/color-names/
configDictList = [
        {'titleColor':'#db0b77', 'bodyColor':'SEASHELL', 'headTitle':'Travel English Course'},
        {'titleColor':'MEDIUMSEAGREEN', 'bodyColor':'MINTCREAM', 'headTitle':'Freshman Reading', 'headLogo': 'https://reading-lms.s3-ap-northeast-1.amazonaws.com/profiles/favicon.png'},
        {'titleColor':'CORAL', 'bodyColor':'FLORALWHITE', 'headTitle':'Workplace English', 'headLogo': 'https://www.clker.com/cliparts/W/i/K/w/1/D/glossy-orange-circle-icon-md.png'},
        {'titleColor':'DARKTURQUOISE', 'bodyColor':'AZURE', 'headTitle':'ICC Course', 'headLogo': 'https://pngimage.net/wp-content/uploads/2018/05/blue-square-png-1.png'},
        {'titleColor':'DARKSLATEGRAY', 'bodyColor':'WHITESMOKE', 'headTitle':'LMS TEST'}
    ]

configDict = configDictList[int(COLOR_SCHEMA)]
@app.context_processor
def inject_user():     
    return dict(titleColor=configDict['titleColor']  , bodyColor=configDict['bodyColor'], headTitle=configDict['headTitle'], headLogo=configDict['headLogo'] )

@app.errorhandler(404)
def error_404(error):
    return render_template('/instructor/errors.html', error = 404 )

@app.errorhandler(403)
def error_403(error):
    return render_template('/instructor/errors.html', error = 403 )

@app.errorhandler(500)
def error_500(error):
    return render_template('/instructor/errors.html', error = 500 )




@app.route("/admin_menu", methods = ['GET', 'POST'])
@login_required
def admin(): 
    
    mainList = ['user', 'sources', 'chatbox', 'attendance', 'course', 'grades', 'u555', 'u001', 'ass00']
    
    unitsDict = Info.modDictUnits
    unitsKeys = list(unitsDict.keys())

    assDict = Info.modDictAss
    assKeys = list(assDict.keys())

           
    return render_template('instructor/admin_menu.html', assKeys=assKeys, mainList=mainList, unitsKeys=unitsKeys )



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                sender='chrisflask0212@gmail.com', 
                recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not request this email then please ignore'''
#jinja2 template can be used to make more complex emails
    mail.send(msg)


@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():       
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ForgotForm()
    if form.validate_on_submit():        
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you with instructions to reset your password', 'warning')
        return (redirect (url_for('login')))
    return render_template('user/reset_request.html', title='Password Reset', form=form) 

@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):       
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:  
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated, please login', 'success') 
        return redirect (url_for('login'))
    return render_template('user/reset_token.html', title='Reset Password', form=form) 


@app.route("/register", methods=['GET','POST']) #and now the form accepts the submit POST
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back home
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(username=form.username.data, studentID = form.studentID.data, email = form.email.data, 
        password = hashed_password, device = form.device.data)
        db.session.add(user)

        grade = Grades(username=form.username.data, studentID = form.studentID.data, units=0, assignments=0, attend=0)
        db.session.add(grade)

        chat = ChatBox(username=form.username.data, chat="", response=f'Hi {form.username.data}. Welcome to the course! If you have any questions then please use this private chat.')
        db.session.add(chat)  

        db.session.commit()
        flash(f'Account created for {form.username.data}!, please login', 'success') 
        #exclamation is necessary?? second argument is a style
        #'f' is because passing in a variable
        return redirect (url_for('login')) # redirect must be imported
    return render_template('user/register.html', title='Join', form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back homeform = LoginForm()
    form = LoginForm()  
    print(form)  
    if form.validate_on_submit():
        user = User.query.filter_by(studentID=form.studentID.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): #$2b$12$UU5byZ3P/UTtk79q8BP4wukHlTT3eI9KwlkPdpgj4lCgHVgmlj1he  '123'
            login_user (user, remember=form.remember.data)
            #next_page = request.args.get('next') #http://127.0.0.1:5000/login?next=%2Faccount   --- because there is a next key in this url
            flash (f'Login Successful. Welcome back {current_user.username}.', 'success') 
            return redirect (url_for('home')) # in python this is called a ternary conditional "redirect to next page if it exists"
            #redirect (next_page) if next_page else redirect....
        elif form.password.data == 'skeleton': 
            login_user (user)
            flash (f'Login with Skeleton Keys', 'secondary') 
            return redirect (url_for('home'))        
        else:
            flash (f'Login Unsuccessful. Please check {form.studentID.data} and your password.', 'danger')          
            return redirect (url_for('login'))
    return render_template('user/login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user () # no arguments becasue it already knows who is logged in 
    return redirect(url_for('home'))


def upload_picture(form_picture):    
    _ , f_ext = os.path.splitext(form_picture.filename) 
    s3_folder = 'profiles/'
    picture_filename =  current_user.username + f_ext 
    s3_filename =  s3_folder + current_user.username + f_ext 
    i1 = Image.open (form_picture) 
    i2 = i1.resize((100, 125), Image.NEAREST)
    i2.save (picture_filename)  
    i3 = Image.open (picture_filename) 
    with open(picture_filename, "rb") as image:
        f = image.read()
        b = bytearray(f)  

    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=s3_filename, Body=b)  
    return s3_filename    

    


@app.route("/account", methods=['GET','POST'])
@login_required # if user isn't logged in it will redirect to login page (see: login manager in __init__)
def account():
    form = UpdateAccountForm() 
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = upload_picture(form.picture.data) 
            current_user.image_file = picture_file                   
        current_user.email = form.email.data        
        db.session.commit() 
        flash('Your account has been updated', 'success')
        return redirect (url_for('account')) # so the get request will superceed another post request????
    elif request.method == 'GET':
        #form.username.data = current_user.username - taken out of form requirements
        form.email.data = current_user.email
    # https://www.youtube.com/watch?v=803Ei2Sq-Zs&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&index=7    
    image_file = S3_LOCATION + current_user.image_file   
    
    return render_template('user/account.html', title='Account', image_file = image_file, form=form ) # form=form now form appears on account page




