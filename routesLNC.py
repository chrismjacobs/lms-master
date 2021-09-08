import sys, boto3, random, base64, os, time, ast, json
from datetime import datetime, timedelta
from sqlalchemy import asc, desc, or_
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *
from models import *
from flask_mail import Message
import ast # eval literal for list str
from pprint import pprint

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN


def get_sources():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    sDict = json.loads(file_content)  # json loads returns a dictionary
    unitDict = {}
    for week in sDict:
        try:
            if int(sDict[week]['Unit']) > 0 or SCHEMA == 9: ## this or condition will add unit 00 for the reading class practice
                unitNumber = sDict[week]['Unit']
                unitDict[unitNumber] = {}
                section = sDict[week]
                #unitDict[unitNumber] = sDict[week]

                unitDict[unitNumber]['Title'] = section['Title']
                unitDict[unitNumber]['Date'] = section['Date']
                unitDict[unitNumber]['Deadline'] = section['Deadline']
                unitDict[unitNumber]['Materials'] = {}
                unitDict[unitNumber]['Materials']['1'] = section['M1']
                unitDict[unitNumber]['Materials']['2'] = section['M2']
                unitDict[unitNumber]['Materials']['3'] = section['M3']
                unitDict[unitNumber]['Materials']['4'] = section['M4']
                unitDict[unitNumber]['Materials']['A'] = section['MA']

        except:
            print('except', sDict[week]['Unit'])
            pass

    pprint(unitDict)

    return unitDict


@app.route('/chatCheck', methods=['POST'])
@login_required
def chatCheck():
    # parse sqlalchemy bind parameters
    chatForm = request.form ['chat']
    if chatForm !='0':
        chat = (request.form ['chat'].split("'"))[5]
    else:
        chat = '0'

    dialogues = ChatBox.query.filter_by(username=current_user.username).all()
    length = len(dialogues)-1
    if length >= 0:
        # parse sqlalchemy bind parameters
        string = str(dialogues[length])
        data = string.split("'")
        lastChat = data[5]
    else:
        lastChat = '0'

    print (chat)
    print (lastChat)

    if chat == lastChat:
        print('No new messages')
        return jsonify({'error' : 'No new messages'})
    else:
        return jsonify({'new' : lastChat})



@app.route ("/", methods = ['GET', 'POST'])
@app.route ("/home", methods = ['GET', 'POST'])
def home():
    try:
        print('TRY HOME')
        result = current_user.username
        print ('RESULT', result)
    except:
        return redirect(url_for('login'))


    ''' deal with chat '''
    form = Chat()
    dialogues = ChatBox.query.filter_by(username=current_user.username).all()
    length = len(dialogues)-1
    if length >= 0:
        chat = dialogues[length]
    else:
        chat = 0
    if form.validate_on_submit():
            chat = ChatBox(username = current_user.username, chat=form.chat.data, response=form.response.data)
            db.session.add(chat)
            db.session.commit()
            if form.chat.data != "":
                msg = Message('LMS Message',
                sender='chrisflask0212@gmail.com',
                recipients=['cjx02121981@gmail.com'])
                msg.body = f'''Message from {current_user.username} says {form.chat.data}'''
                #jinja2 template can be used to make more complex emails
                mail.send(msg)
            return redirect(url_for('home'))
    else:
        form.name.data = current_user.username
        form.response.data = ""
        form.chat.data = ""
        image_file = S3_LOCATION + current_user.image_file
        image_chris = S3_LOCATION + User.query.filter_by(id=1).first().image_file


    ''' deal with attendance '''
    attLog = AttendLog.query.filter_by(username=current_user.username).all()

    context = {
    'form' : form,
    'dialogues' : dialogues,
    'image_chris' : image_chris,
    'image_file' : image_file,
    'chat' : chat,
    'attLog' : attLog,
    'title' : 'Home'
    }

    return render_template('admin/home.html', **context )


######## teamwork //////////////////////////////////////////////

workDict = {
    '00' : {
        'Unit' : '00',
        'Title': 'Test',
        'Status': 1,
        'ppt': 'https://docs.google.com/presentation/d/e/2PACX-1vTFhtOmlR9vGT04Rez8Gvpp3HJiy2Y9dqabSQ_P7VhkLISLNYesLLMvpAfcljT03g0jQQXou_FWcmPa/embed',
        'Worksheet' : {
            '1' : '',
            '2' : ''
        },
        'Note' : {
            '1' : '',
            '2' : ''
        },
        'Audio' : {
            '1' : '',
            '2' : ''
        }
    },
    '01' : {
        'Unit' : '01',
        'Title': 'What is Culture?'
    }
}

@app.route ("/teamwork", methods=['GET','POST'])
@login_required
def teamwork_list():

    theme=DESIGN['titleColor']


    return render_template('lnc/teamwork_list.html', legend='Teamwork Dashboard',
    Dict=json.dumps(workDict), title='Teamwork', theme=theme)


@app.route("/tw/<string:unit>", methods = ['GET', 'POST'])
@login_required
def tw(unit):

    srcDict = get_sources()
    source = srcDict[unit]['Materials']['A']

    setting =  Units.query.filter_by(unit=unit).first().uA
    if setting != 1:
        return redirect(request.referrer)
        flash('This assignment is not open yet', 'danger')

    # models update
    assDict = Info.ass_mods_dict
    model = assDict[unit]

    #model = models[unitInt]
    count = model.query.filter_by(username=current_user.username).count()
    fields = model.query.filter_by(username=current_user.username).first()

    if count == 0:
        ansDict = {
        'Unit' : unit,
        1 : {
            'AudioData' : None,
            'Length' : None
            },
        2 : {
            'AudioData' : None,
            'Length' : None
            },
        3 : {
            'Notes' : "",
            'TextOne' : "",
            'TextTwo' : "",
            }
        }
    elif count == 1:
        ansDict = {
        'Unit' : unit,
        1 : {
            'AudioData' : fields.AudioDataOne,
            'Length' : fields.LengthOne
            },
        2 : {
            'AudioData' : fields.AudioDataTwo,
            'Length' :  fields.LengthTwo
            },
        3 : {
            'Notes' : fields.Notes,
            'TextOne' : fields.TextOne,
            'TextTwo' : fields.TextTwo,
            }
        }
    else:
        firstEntry = model.query.filter_by(username=current_user.username).first()
        #model.query.get(firstEntry.id).delete()
        db.session.delete(firstEntry)
        db.session.commit()
        fields = model.query.filter_by(username=current_user.username).first()
        ansDict = {
        'Unit' : unit,
        1 : {
            'AudioData' : fields.AudioDataOne,
            'Length' : fields.LengthOne
            },
        2 : {
            'AudioData' : fields.AudioDataTwo,
            'Length' :  fields.LengthTwo
            },
        3 : {
            'Notes' : fields.Notes,
            'TextOne' : fields.TextOne,
            'TextTwo' : fields.TextTwo,
            }
        }


    try:
        speechModel = model.query.filter_by(username='Chris').first()
        ansDict[1]['model'] = speechModel.AudioDataOne
        ansDict[2]['model']  = speechModel.AudioDataTwo
    except:
        speechModel = None
        ansDict[1]['model'] = None
        ansDict[2]['model']  = None

    context = {
        'count' : count,
        'fields' : fields,
        'unit' : unit,
        'source' : source,
        'speechModel' : speechModel,
        'ansDict' : json.dumps(ansDict),
        'siteName' : S3_BUCKET_NAME,
        'title' : 'Unit_' + unit
    }

    return render_template('units/assignment_vue.html', **context)


@app.route('/audioUpload', methods=['POST', 'GET'])
def audioUpload():

    unit = request.form ['unit']
    task = request.form ['task']
    title = request.form ['title']
    audio_string = request.form ['base64']
    ansDict = request.form ['ansDict']
    Notes = request.form ['Notes']
    TextOne = request.form ['TextOne']
    TextTwo = request.form ['TextTwo']

    answers = json.loads(ansDict)
    print(answers)

    srcDict = get_sources()
    date = srcDict[unit]['Date']
    dt = srcDict[unit]['Deadline']
    deadline = datetime.strptime(dt, '%Y-%m-%d') + timedelta(days=1)
    print ('deadline: ', deadline)

    if title == 'text':
        newTitle = None
    elif title == 'link':
        newTitle = audio_string
        print('LINK DETECTED')
    else:
        print('PROCESSING AUDIO')
        audio = base64.b64decode(audio_string)
        newTitle = S3_LOCATION + 'assignments/' + current_user.username + '/' + title + '.mp3'
        filename = 'assignments/' + current_user.username + '/' + title + '.mp3'
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)


    model = Info.ass_mods_dict[unit]
    com = 'in progress...'

    ## start assignment
    if model.query.filter_by(username=current_user.username).count() == 0:
        entry = model(username=current_user.username, Grade=0, Comment=com)
        db.session.add(entry)
        db.session.commit()

    ## add task data
    user = model.query.filter_by(username=current_user.username).first()
    if task == '1':
        user.AudioDataOne = newTitle
        user.LengthOne = answers['1']['Length']
    if task == '2':
        user.AudioDataTwo = newTitle
        user.LengthTwo = answers['2']['Length']
    if task == '3':
        user.Notes = Notes
        user.TextOne = TextOne
        user.TextTwo = TextTwo
    db.session.commit()

    ## check grade
    grade_status = 0
    if user.AudioDataOne and user.AudioDataTwo and user.TextOne and user.TextTwo:
        if user.Grade > 0 :
            grade_status = user.Grade
        elif  datetime.now() < deadline:
            user.Grade = 2  # completed on time
            grade_status = 2
            user.Comment = 'Completed on time - Great!'
        else:
            user.Grade = 1  # late start
            grade_status = 1
            user.Comment = 'This assignment has been completed late'
    db.session.commit()

    return jsonify({'title' : newTitle, 'grade' : grade_status})