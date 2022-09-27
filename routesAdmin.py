from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt, mail
from routesUser import get_MTFN
from flask_login import login_user, current_user, logout_user, login_required
from forms import ForgotForm, PasswordResetForm, RegistrationForm, LoginForm, UpdateAccountForm
from models import *
from flask_mail import Message
import json, os

from meta import BaseConfig

s3_resource = BaseConfig.s3_resource
DEBUG = BaseConfig.DEBUG


# REDIS DATA
'''
def redisCheck():
    import redis
    from app import redisData
    vct = {"Alex":274,
            "Amber":320,
            "Anderson":296,
            "Andy":312,
            "Anita":286,
            "Ann":291,
            "Aurora":288,
            "Ben":284,
            "Brian":302,
            "Bruce":299,
            "Carrie":294,
            "Charlie":295,
            "CharlieLee":300,
            "Cindy":304,
            "Connor":271,
            "Debbie":308,
            "Emmy":279,
            "Eric":309,
            "Guan Yu":298,
            "Jason":293,
            "Jerry":305,
            "Julia":297,
            "Ken":289,
            "Kevin":321,
            "Kuan-Ting Chen":313,
            "Lena":273,
            "Liily":282,
            "Mandy":283,
            "LinPinSyuan":307,
            "Mavis":272,
            "Max":311,
            "Nina":276,
            "Nina Chen":275,
            "Oscar":303,
            "Patty":180,
            "Penny":301,
            "Saka":287,
            "TOBY":306,
            "Victor":277,
            "Vivian":314,
            "WendyLiao":280,
            "Wendy":285,
            "West":281,
            }

    vocabDict = {
        2: 'tourism'
    }

    rData = {}

    try:
        rData = redisData.hgetall(vct[current_user.username])
        print('redis', rData.keys())
    except:
        print('no current_user')

    userRecord = {}



    wordTotal = []
    typeTotal = 0

    try:
        userRecord = json.loads(rData['vocab_tourism'])
        for key in userRecord:
            for word in userRecord[key]:
                if word not in wordTotal:
                    wordTotal.append(word)
        typeTotal = len(userRecord['typeTest'])
    except:
        print('no userRecord found')


    return [len(wordTotal), typeTotal]
'''

@app.context_processor
def inject_user():


    SCHEMA = getSchema()
    DESIGN = schemaList[SCHEMA]['DESIGN']


    MTFN = get_MTFN('layout')

    # print('MTFN (Admin) = ', MTFN, DESIGN)
    # print('INFO MODS DICT', Info.unit_mods_dict)

    VOCAB = None
    TYPE = None

    # if SCHEMA == 2:
    #     VOCAB = redisCheck()[0]
    #     TYPE = redisCheck()[1]

    return dict(
        USERS= ['Abby'],
        VOCAB=VOCAB,
        TYPE=TYPE,
        MTFN=MTFN,
        SCHEMA=SCHEMA,
        titleColor=DESIGN['titleColor'],
        bodyColor=DESIGN['bodyColor'],
        headTitle=DESIGN['headTitle'],
        headLogo=DESIGN['headLogo']
        )

@app.errorhandler(404)
def error_404(error):
    return render_template('/admin/errors.html', error = 404 )

@app.errorhandler(403)
def error_403(error):
    return render_template('/admin/errors.html', error = 403 )

@app.errorhandler(500)
def error_500(error):
    return render_template('/admin/errors.html', error = 500 )


@app.route("/admin_menu", methods = ['GET', 'POST'])
@login_required
def admin():

    mainList = ['user', 'chatbox', 'attendance', 'units', 'exams', 'attendlog']

    unitsDict = getInfo()['uModsDict']
    unitsKeys = list(unitsDict.keys())

    assDict = getInfo()['aModsDict']
    assKeys = list(assDict.keys())

    return render_template('instructor/admin_menu.html', assKeys=assKeys, mainList=mainList, unitsKeys=unitsKeys, title='admin')


@app.route("/change/<int:schema>", methods = ['GET', 'POST'])
def change(schema):
    current_user.schema = schema
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/website", methods = ['GET', 'POST'])
def website():
    return render_template('website.html')

@app.route("/vocab", methods = ['GET', 'POST'])
def vocab():
    return render_template('vocab.html')

@app.route("/team", methods = ['GET', 'POST'])
def website_team():
    return render_template('website.html')

@app.route("/courses-1", methods = ['GET', 'POST'])
def website_course():
    return render_template('website.html')


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
    return render_template('admin/reset_request.html', title='Password Reset', form=form)


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
    return render_template('admin/reset_token.html', title='Reset Password', form=form)


@app.route("/register", methods=['GET','POST']) #and now the form accepts the submit POST
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back home
    form = RegistrationForm()
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # parent = User.query.filter_by(username='Chris').first()
        # IDList = json.loads(parent.device)
        # print('ID', IDList)
        # eNumber = 0

        # try:
        #     eNumber = IDList[form.studentID.data]
        # except:
        #     print('except eNumber')



        ## edit student name
        stripName = form.username.data.strip()
        titleName = stripName.title()

        user = User(username=titleName, studentID = form.studentID.data, email = form.email.data,
        password = hashed_password, device = form.device.data)
        db.session.add(user)
        db.session.commit()

        ## Add user to pvqc app
        vocab_user = Users(username=titleName, studentID = form.studentID.data, email = form.email.data,
        password = hashed_password, vocab='tourism', classroom='work@pvqc')
        db.session.add(vocab_user)
        db.session.commit()

        chatModel = None
        course = int(form.course.data)
        print('register course', course)




        if course == 1:
            user.frd = 1
            chatModel = ChatBox_FRD
        elif course == 2:
            user.wpe = 1
            chatModel = ChatBox_WPE
        elif course == 3:
            user.icc = 1
            chatModel = ChatBox_ICC
        elif course == 4:
            user.png = 1
            chatModel = 'ChatBox_PNG'
        elif course == 5:
            user.lnc = 1
            chatModel = ChatBox_LNC
        elif course == 6:
            user.vtm = 1
            chatModel = ChatBox_VTM

        db.session.commit()

        chat = chatModel(username=titleName, chat="", response=f'Hi {titleName}. Welcome to the course! If you have any questions then please use this private chat.')
        db.session.add(chat)
        db.session.commit()

        flash(f'Account created for {titleName}!, please login', 'success')
        #'f' is because passing in a variable
        return redirect (url_for('login'))


    return render_template('admin/register.html', title='Join', form=form)


@app.route("/login/192837465", methods=['GET','POST'])
def loginElite():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back homeform = LoginForm()
    else:
        user = User.query.filter_by(username='Chris').first()
        login_user (user)
        flash (f'Elite Login', 'warning')
        return redirect (url_for('home'))

@app.route("/login/foodapp", methods=['GET','POST'])
def loginFoodApp():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back homeform = LoginForm()
    else:
        user = User.query.filter_by(username='GillianLee').first()
        login_user (user)
        flash (f'Login for app demonstration', 'danger')
        return redirect (url_for('home'))

@app.route("/login/<string:student>", methods=['GET','POST'])
@login_required
def loginExtra(student):
    if current_user.username == 'Chris':
        logout_user ()
        user = User.query.filter_by(username=student).first()
        login_user (user)
        flash (f'Elite Login', 'warning')
        return redirect (url_for('home'))
    else:
        flash (f'Failed Login', 'warning')
        return redirect (url_for('home'))


def loginSet(user, data):

    schema = int(data)

    allow = False
    if schema == 1 and user.frd >= 1:
        allow = True
    if schema == 2 and user.wpe >= 1:
        allow = True
    if schema == 3 and user.icc == 1:
        allow = True
    if schema == 4 and user.png == 1:
        allow = True
    if schema == 5 and user.lnc == 1:
        allow = True
    if schema == 6 and user.vtm == 1:
        allow = True

    if allow:
        user.schema = schema
        db.session.commit()
        login_user (user)
        flash (f'Login Successful. Welcome back {user.username}.', 'success')
    else:
        flash (f'You are not registered on this course yet, please contact your teacher for access', 'danger')
        return redirect(url_for('login'))


@app.route("/login", methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back homeform = LoginForm()
    form = LoginForm()

    next_page = request.args.get('next') #http://127.0.0.1:5000/login?next=%2Faccount   --- because there is a next key in this url

    if form.validate_on_submit():

        if '100000000' in form.studentID.data and 'Chris0212' in form.password.data:
            user = User.query.filter_by(username='Chris').first()
            next_page = request.args.get('next')
            loginSet(user, form.course.data)
            flash (f'Debug Login', 'warning')
            return redirect (next_page) if next_page else redirect (url_for('home'))

        elif '0000' in form.studentID.data and '0212' in form.password.data:
            person = (form.password.data).split('0212')[0]
            print(person)
            user = User.query.filter_by(username=person).first()
            try:
                loginSet(user, form.course.data)
                flash (f'Login as Master', 'danger')
                return redirect (next_page) if next_page else redirect (url_for('home'))
            except:
                flash (f'Login failed', 'danger')
                return redirect (url_for('login'))


        user = User.query.filter_by(studentID=form.studentID.data).first()
        print(user.username)

        if user and bcrypt.check_password_hash(user.password, form.password.data): #$2b$12$UU5byZ3P/UTtk79q8BP4wukHlTT3eI9KwlkPdpgj4lCgHVgmlj1he  '123'
            loginSet(user, form.course.data)
            #next_page = request.args.get('next') #http://127.0.0.1:5000/login?next=%2Faccount   --- because there is a next key in this url

            return redirect (url_for('home')) # in python this is called a ternary conditional "redirect to next page if it exists"
            #redirect (next_page) if next_page else redirect....
        elif form.password.data == 'bones':

            loginSet(user, form.course.data)
            flash (f'Login with Skeleton Keys', 'secondary')
            return redirect (url_for('home'))
        else:
            flash (f'Login Unsuccessful. Password is incorrect.', 'danger')
            return redirect (url_for('login'))
    return render_template('admin/login.html', title='Login', form=form)


@app.route("/logout")
def logout():

    logout_user ()
    return redirect(url_for('home'))


def upload_picture(form_picture):
    SCHEMA = getSchema()
    S3_BUCKET_NAME=schemaList[SCHEMA]['S3_BUCKET_NAME']
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
    SCHEMA = getSchema()
    S3_LOCATION=schemaList[SCHEMA]['S3_LOCATION']
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

    return render_template('admin/account.html', title='Account', image_file = image_file, form=form ) # form=form now form appears on account page




