import sys, boto3, random, base64, os, secrets, httplib2, json, ast
from sqlalchemy import asc, desc
from datetime import datetime, timedelta, date
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *
from models import *
from routesGet import getUsers
from pprint import pprint
from flask_mail import Message

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource

"""S3 CONNECTIONS """
def loadAWS(file, unit):
    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    if unit == 0 :
        key = file
        content_object = s3_resource.Object(  S3_BUCKET_NAME, key  )
        print('LOAD_AWS_SEARCH', content_object)
    else:
        key = str(unit) + '/' + file
        content_object = s3_resource.Object(  S3_BUCKET_NAME, key   )
        print('LOAD_AWS_SEARCH', content_object)
    try:
        file_content = content_object.get()['Body'].read().decode('utf-8')
        jload = json.loads(file_content)
        print(type(jload))
    except:
        print('AWS return NONE')
        jload = None

    return jload

# def loadAWS(file, unit):
#     if unit == 0 :
#         jList = [S3_BUCKET_NAME, file]
#         content_object = s3_resource.Object(  jList[0], jList[1]   )
#     else:
#         jList = [S3_BUCKET_NAME, file]
#         content_object = s3_resource.Object(  jList[0], jList[1]   )

#     file_content = content_object.get()['Body'].read().decode('utf-8')
#     jload = json.loads(file_content)
#     print(type(jload))

#     return jload


@app.route("/tips", methods = ['GET', 'POST'])
@login_required
def tips():

    with open('static/topics.json', 'r') as f:
        srcJSON = json.load(f)

    tips = json.dumps(srcJSON['tips'])

    return render_template('work/tips.html', tips=tips)


@app.route('/upload/<string:assignment>', methods=['POST', 'GET'])
def upload(assignment):
    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    file = request.files['file']
    fn = file.filename
    file_name = current_user.username + '_' + fn + '_' + assignment + '.mp3'
    my_bucket = s3_resource.Bucket(S3_BUCKET_NAME)
    my_bucket.Object(file_name).put(Body=file)

    return redirect(request.referrer)


''' new style '''
@app.route('/storeData', methods=['POST'])
def storeData():
    unit = request.form ['unit']
    obj = request.form ['obj']
    stage = request.form ['stage']
    work = request.form ['work']

    if work == 'edit':
        student = request.form ['student']
    else:
        student = current_user.username

    print('STAGE WORK OBJ', stage, work, obj)
    classModel = getInfo()['aModsDict'][unit]
    entry = classModel.query.filter_by(username=student).first()
    info = json.loads(entry.info)

    if work == 'plan':
        if int(stage) == 0:
            info[work + "_date_start"] = str(date.today())
        if int(stage) == 1:
            info[work + "_date_finish"] = str(date.today())
            info['stage'] = 1
            entry.grade = stage
        entry.info = json.dumps(info)
        entry.plan = obj
        db.session.commit()

    if work == 'draft':
        if int(stage) == 1:
            info[work + "_date_start"] = str(date.today())
        if int(stage) == 2:
            info[work + "_date_finish"] = str(date.today())
            info['stage'] = 2
        entry.info = json.dumps(info)
        entry.draft = obj
        entry.grade = stage
        db.session.commit()

    if work == 'edit':
        dataDict = {
            'html' : request.form ['html'],
            'text' : request.form ['text'],
            'revised' : None,
        }
        info['stage'] = stage
        entry.info = json.dumps(info)
        entry.revise = json.dumps(dataDict)
        entry.grade = 3
        db.session.commit()
        studentEmail = User.query.filter_by(username=student).first().email
        msg = Message('Message from Writing LMS',
                sender='chrisflask0212@gmail.com',
                recipients=['cjx02121981@gmail.com', studentEmail ])
        msg.body = 'Dear ' + student + ',  Your writing draft for topic ' + unit + ' has been checked. Please move to the revise stage to see the correction and fix them before publishing. Thanks, Chris'
        mail.send(msg)

    if work == 'revise':
        print(student)
        info[work + "_date_finish"] = str(date.today())

        if int(info['stage']) == 3:
            info['stage'] = 4
            entry.grade = 4
        entry.info = json.dumps(info)
        print(entry.info)
        dataDict = json.loads(entry.revise)
        dataDict['revised'] = obj ## actually a string
        entry.revise = json.dumps(dataDict)
        print(entry.revise)
        db.session.commit()

    if work == 'publish':
        info[work + "_date_finish"] = str(date.today())
        info['stage'] = stage
        entry.info = json.dumps(info)
        dataDict = {
            'title' :  request.form ['title'],
            'imageLink' :  request.form ['imageLink'],
            'final' :  request.form ['final'],
        }
        entry.publish = json.dumps(dataDict)
        entry.grade = 5
        db.session.commit()


    name = current_user.username

    return jsonify({'name' : name, 'work' : work})
''' new style '''

@app.route('/updateInfo', methods=['POST'])
def updateInfo():

    unit = request.form ['unit']
    theme = request.form ['theme']
    name = request.form ['name']
    avatar = request.form ['avatar']
    partner = request.form ['partner']



    print('UInfo', unit, theme, partner)
    classModel = getInfo()['aModsDict'][unit]
    entry = classModel.query.filter_by(username=current_user.username).first()

    info = json.loads(entry.info)

    info['theme'] = theme
    info['name'] = name
    info['avatar'] = avatar

    entry.info = json.dumps(info)
    entry.partner = partner.strip().title()

    db.session.commit()

    return jsonify({'name' : name})


@app.route('/sendImage', methods=['POST'])
def sendImage():
    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    b64String = request.form ['b64String']
    print(b64String)
    print('SENDIMAGE ACTIVE')
    unit = request.form ['unit']
    fileType = request.form ['fileType']
    print (b64String, fileType)

    image = base64.b64decode(b64String)
    imageLink = S3_LOCATION + 'images/' + unit + '/' + current_user.username + '.' + fileType
    filename = 'images/' + unit + '/' + current_user.username + '.' + fileType
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=image)

    return jsonify({'name' : current_user.username, 'imageLink' : imageLink})


def getWriteUsers():
    ### sperate for vietnam class

    vs = []
    es = []
    userList = []

    for u in getUsers(6):
        vs.append(u.username)

    for u in getUsers(8):
        if 'Chris' in vs:
            userList = vs
            break

        else:
            es.append(u.username)
        userList = es

    print(userList)

    return userList

""" ### TOPICS ### """

@app.route("/topic_list", methods = ['GET', 'POST'])
@login_required
def topic_list():
    topDict = {}
    infoDict = {}

    with open('static/topics.json', 'r') as f:
        srcJSON = json.load(f)

    sources = srcJSON['sources']

    pprint(sources)



    userList = getWriteUsers()


    for unit in sources:
        src = sources[unit]
        if src['Set'] == 1:
            ## add to topics list
            topDict[unit] = {
                'Title' : src['Title'],
                'Deadline' : src['Deadline']
            }
            model = getInfo()['aModsDict'][unit]
            user = model.query.filter_by(username=current_user.username).first()
            ## add info details if available
            if user and user.username in userList:
                infoDict = json.loads(user.info)
                topDict[unit]['Theme'] = infoDict['theme']
                topDict[unit]['Stage'] = int(infoDict['stage'])
                topDict[unit]['Avatar'] = infoDict['avatar']
                topDict[unit]['Partner'] = user.partner
            else:
                topDict[unit]['Theme'] = 'white'
                topDict[unit]['Stage'] = 0
                topDict[unit]['Avatar'] = 'none'

    print('DICT', topDict)
    topJS = json.dumps(topDict)
    topInfo = json.dumps(infoDict)

    return render_template('work/topic_list.html', topJS=topJS, topInfo=topInfo)


## AJAX
@app.route('/topicCheck/<string:unit>', methods=['POST'])
def topicCheck(unit):
    print('TOPIC CHECK ACTIVE')

    stage = 0
    dataList =  []

    userList = getWriteUsers()

    model = getInfo()['aModsDict'][unit]
    entryUser = model.query.filter_by(username=current_user.username).first()
    entries = model.query.all()

    for entry in entries:
        info = json.loads(entry.info)
        if entry.username == current_user.username:
            stage = info['stage']
            print('CURRENT USER FOUND', current_user.username, stage)
        elif entry.username in userList:
            plan = json.loads(entry.plan)
            draft = json.loads(entry.draft)
            publish = json.loads(entry.publish)


            entryDict = {
                'info' : json.loads(entry.info),
                'plan' : plan,
                'draft' : draft,
                'publish' : publish,
            }

            dataList.append( json.dumps(entryDict)  )

    #print('XXXXXX', dataList)
    random.shuffle(dataList)


    with open('static/topics.json', 'r') as f:
        srcJSON = json.load(f)


    sources = json.dumps(srcJSON['sources'])

    #print('DATA', type(dataList), dataList)
    return jsonify({'dataList' : dataList, 'sources' : sources, 'stage' : stage, 'info' : entryUser.info, 'partner': entryUser.partner })

## AJAX
@app.route('/getHTML/<string:unit>', methods=['POST'])
def getHTML(unit):
    print('GET HTML ACTIVE')

    try:
        name = request.form ['name']
        print('NAME', name, unit)
    except:
        name = current_user.username


    model = getInfo()['aModsDict'][unit]
    entry = model.query.filter_by(username=name).first()
    info = entry.info
    revise = entry.revise
    stage = entry.grade
    print(name, unit, stage, revise[0:5])

    #print('DATA', type(dataList), dataList)
    return jsonify({'revise' : revise, 'stage' : stage, 'info' : info})


""" ### PLAN/WORK/REVISE/PUBLISH ### """

@app.route("/work/<string:part>/<string:unit>", methods = ['GET', 'POST'])
@login_required
def part(part, unit):

    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    classModel = getInfo()['aModsDict'][unit]
    entryCount = classModel.query.filter_by(username=current_user.username).count()
    if entryCount == 0:
        info = {
            'avatar' : 1,
            'theme' : 'white',
            'name' : current_user.username,
            'image' : S3_LOCATION + current_user.image_file,
            'stage' : 0
        }
        # start assignment
        entry = classModel(username=current_user.username,
        info=json.dumps(info),
        plan=json.dumps({}),
        draft=json.dumps({}),
        revise=json.dumps({}),
        publish=json.dumps({})
        )
        db.session.add(entry)
        db.session.commit()


    entry = classModel.query.filter_by(username=current_user.username).first()

    fullDict = {
        'info' : entry.info,
        'plan' : entry.plan,
        'draft' : entry.draft,
        'revise' : entry.revise,
        'publish' : entry.publish,
    }

    #print(fullDict)

    #SOURCES = loadAWS('json_files/sources.json', 0)
    #sources = json.dumps(SOURCES['sources'])
    with open('static/topics.json', 'r') as f:
        srcJSON = json.load(f)

    sources = json.dumps(srcJSON['sources'])

    return render_template('work/' + part + '.html', unit=unit, fullDict=json.dumps(fullDict), sources=sources)


""" ### INSTRUCTOR DASHBOARD ### """

@app.route("/write_dash", methods = ['GET', 'POST'])
@login_required
def write_dash():
    if current_user.id != 1:
        return redirect(url_for('home'))


    models_list = ['01', '02', '03', '04']
    # models_list = ['05', '06', '07', '08', '09']
    recDict = {}

    for model in getInfo()['aModsDict']:
        #print(recDict)
        if str(model) in models_list:
            recDict[model] = {}
            for entry in getInfo()['aModsDict'][model].query.all():
                recDict[str(model)][entry.username] = {
                    'info' : json.loads(entry.info),
                    'partner' : entry.partner,
                    'plan' : json.loads(entry.plan),
                    'draft' : json.loads(entry.draft),
                    'revise' : json.loads(entry.revise),
                    'publish' : json.loads(entry.publish),
                }

    return  render_template('work/dashboard.html', recOBJ=str(json.dumps(recDict)))

@app.route("/published_work", methods = ['GET', 'POST'])
@login_required
def published():

    recDict = {}

    for model in getInfo()['aModsDict']:
        recDict[model] = {}
        #print(recDict)
        for entry in getInfo()['aModsDict'][model].query.all():
            recDict[str(model)][entry.username] = {
                'info' : json.loads(entry.info),
                'publish' : json.loads(entry.publish),
            }

    return  render_template('work/published_work.html', recOBJ=str(json.dumps(recDict)))



@app.route("/published_check", methods = ['POST'])
@login_required
def publish_API():

    recDict = {}

    for model in getInfo()['aModsDict']:
        recDict[model] = {}
        #print(recDict)
        for entry in getInfo()['aModsDict'][model].query.all():
            if entry.grade == 5 and int(model) > 4: # check models after topic 4
                reviseDict = json.loads(entry.revise)
                #print('xxxx', reviseDict)
                recDict[str(model)][entry.username] = {
                    'info' : json.loads(entry.info),
                    'publish' : json.loads(entry.publish),
                    'revise' : json.loads(entry.revise),
                    'plan' : json.loads(entry.plan),
                    'htmltext' : reviseDict['html'],
                }

    return jsonify({'revise' : revise, 'stage' : stage, 'info' : info})




@app.route("/published_check/<string:mode>", methods = ['GET', 'POST'])
@login_required
def pCheck(mode):
    taCheck = ['Chris', 'TA']

    recCount = 0
    recDict = {}

    for model in getInfo()['aModsDict']:
        recDict[model] = {}
        #print(recDict)
        for entry in getInfo()['aModsDict'][model].query.all():
            if current_user.username in taCheck:
                add = True
            elif current_user.username == entry.username:
                add = True
            else:
                add = False
            if entry.grade == 5 and add == True: # and int(model) > 4 -- check models after topic 4
                reviseDict = json.loads(entry.revise)
                #print('xxxx', reviseDict)
                recDict[str(model)][entry.username] = {
                    'info' : json.loads(entry.info),
                    'publish' : json.loads(entry.publish),
                    'revise' : json.loads(entry.revise),
                    'plan' : json.loads(entry.plan),
                    'htmltext' : reviseDict['html'],
                }
                recCount += 1


    return  render_template('work/published_check.html', instructor=mode, recCount=recCount, recOBJ=str(json.dumps(recDict)))


@app.route("/editor/<string:student>/<string:unit>", methods = ['GET', 'POST'])
@login_required
def editor(student, unit):
    if current_user.id != 1:
        return redirect(url_for('home'))

    model = getInfo()['aModsDict'][unit]
    print(model)
    jStrings = model.query.filter_by(username=student).first()

    student_revise = jStrings.revise
    student_plan = jStrings.plan

    student_draft = json.loads(jStrings.draft)
    ## build the student text
    text = ''
    for part in student_draft:
        text += (student_draft[part] + ' ' )

    return  render_template('work/editor.html', text=text, student=student, unit=unit, student_revise=student_revise, student_plan=student_plan)




