import random, base64, ast, json
from datetime import datetime, timedelta
from sqlalchemy import asc, desc, or_
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from app import app, db, bcrypt, mail
from flask_login import current_user, login_required
from forms import *
from models import *
from flask_mail import Message
import ast # eval literal for list str
from routesGet import get_grades, get_sources, get_MTFN, getUsers

from meta import *
s3_resource = BaseConfig.s3_resource


@app.route('/chatCheck', methods=['POST'])
@login_required
def chatCheck():
    # parse sqlalchemy bind parameters
    chatForm = request.form ['chat']
    if chatForm !='0':
        chat = (request.form ['chat'].split("'"))[5]
    else:
        chat = '0'

    dialogues = getModels()['ChatBox_'].query.filter_by(username=current_user.username).all()
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
    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']

    try:
        result = current_user.username
        print ('RESULT', result)
    except:
        return redirect(url_for('login'))


    ''' deal with chat '''
    form = Chat()
    dialogues = getModels()['ChatBox_'].query.filter_by(username=current_user.username).all()
    length = len(dialogues)-1
    if length >= 0:
        chat = dialogues[length]
    else:
        chat = 0
    if form.validate_on_submit():
            chat = getModels()['ChatBox_'](username = current_user.username, chat=form.chat.data, response=form.response.data)
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
        image_chris = S3_LOCATION + User.query.filter_by(username="Chris").first().image_file


    ''' deal with attendance '''
    attLog = getModels()['AttendLog_'].query.filter_by(username=current_user.username).all()

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


######## Exams //////////////////////////////////////////////

### randomize two questions from each section
def review_random(originalDict):
    examDict = {}
    for topic in originalDict:
        examDict[topic] = {}
        length = len(originalDict[topic])
        randArray = []
        for i in range(length):
            randArray.append(i)

        random.shuffle(randArray)
        ##print(topic, randArray)

        count = 0
        for question in originalDict[topic]:
            if count != randArray[0] and count != randArray[1]:
                pass
            else:
                examDict[topic][question] = originalDict[topic][question]
            count += 1

    return examDict


@app.route ("/exams/<string:test>/<string:unit>", methods=['GET','POST'])
@login_required
def exams(test, unit):
    SCHEMA = getSchema()
    DESIGN = schemaList[SCHEMA]['DESIGN']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    semester = User.query.filter_by(username='Chris').first().semester
    reviewClose = User.query.filter_by(username='Chris').first().extra
    examOpen = User.query.filter_by(username=current_user.username).first().extra

    if test == 'review' and reviewClose == SCHEMA and examOpen != SCHEMA:
        flash('This exam is not open yet', 'danger')
        return redirect(url_for('home'))

    if test == 'exam' and examOpen != SCHEMA:
        flash('This exam is not open yet', 'danger')
        return redirect(url_for('home'))

    if semester == 1:
        examString = 'json_files/exam.json'
    else:
        examString = 'json_files/exam2.json'


    ## redirect VTM to ICC exam
    if SCHEMA == 6:
        S3_BUCKET_NAME = 'icc-lms'


    content_object = s3_resource.Object( S3_BUCKET_NAME, examString )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    examAWS = json.loads(file_content)

    if test == 'review':
        originalDict = examAWS[unit]
        examDict = review_random(originalDict)
        html = 'units/exam_review.html'
    if test == 'exam':
        examDict = examAWS[unit]
        html = 'units/exam_review.html'

    theme=DESIGN['titleColor']

    exceptionList = ['TOBY', 'Evelyn']


    return render_template(html, legend='Exams',
    Dict=json.dumps(examDict), title=unit, theme=theme, exceptions=json.dumps(exceptionList))


@app.route ("/updateExam", methods=['POST', 'GET'])
@login_required
def updateExam():
    unit = request.form ['unit']
    test = request.form ['test']
    grade = request.form ['grade']
    tries = request.form ['tries']
    print(unit, test, grade, tries)

    user = getModels()['Exams_'].query.filter_by(username=current_user.username).first()

    # no action after 2 tries
    if int(tries) > 2:
        test = None

    if test == 'review':
        record = json.loads(user.j1)
        try:
            attempts = record[unit][2]
        except:
            record[unit] = [0,0,0,0] # 1st try 2nd try, total attempts, current attempt stage
    elif test == 'exam':
        record = json.loads(user.j2)
        print(record)
        try:
            attempts = record[unit][2]
            if attempts > 0:
                tries = 3 # exam cannot be completed again
        except:
            print('except')
            record[unit] = [0,0,0,0]


    if int(tries) == 1 and record[unit][3] == 0:
        print('ACTION 1')
        # safe - no cheating
        record[unit][0] = int(grade)
        record[unit][1] = 0
        record[unit][3] = 1
        if int(grade) == 20: # average is 20
            record[unit][0] = 20
            record[unit][1] = 20
            record[unit][2] = (record[unit][2] + 1)  # attempts
            record[unit][3] = 0 # reset try counter
    elif int(tries) == 1 and record[unit][3] == 1: # first try happened already
        print('ACTION 2')
        record[unit][1] = int(grade)
        record[unit][2] = (record[unit][2] + 1)
        record[unit][3] = 0 # reset try counter
        tries = 2
    elif int(tries) == 2:
        print('ACTION 3')
        record[unit][1] = int(grade)
        record[unit][2] = (int(attempts) + 1)
        record[unit][3] = 0 # reset try counter

    if test == 'review':
        user.j1 = json.dumps(record)
        db.session.commit()
    elif test == 'exam':
        user.j2 = json.dumps(record)
        db.session.commit()


    return jsonify({'unit' : unit, 'tries' : tries})


@app.route ("/openExam", methods=['POST', 'GET'])
@login_required
def openExam():

    u = User.query.filter_by(username=current_user.username).first()
    if u.extra != 3:
        u.extra = 3
    else:
        u.extra = 0
    db.session.commit()

    return jsonify({'status': u.extra})


@app.route ("/exam_list_midterm", methods=['GET','POST'])
@login_required
def exam_list_midterm():

    semester = int(User.query.filter_by(username='Chris').first().semester)

    ''' set exam practice '''
    try:
        user = getModels()['Exams_'].query.filter_by(username=current_user.username).first()
        reviewData = json.loads(user.j1)
        examData = json.loads(user.j2)
        print('exam_list_data_checked')
    except:
        if semester == 1:
            reviewDict = {
                    '1-1-2' : [],
                    '1-3-4' : [],
                    '1-5-6' : [],
                    '1-7-8' : []
                }
        else:
            reviewDict = {
                    '2-1-2' : [],
                    '2-3-4' : [],
                    '2-5-6' : [],
                    '2-7-8' : []
                }
        entry = getModels()['Exams_'](username=current_user.username, j1=json.dumps(reviewDict), j2=json.dumps(reviewDict))
        db.session.add(entry)
        db.session.commit()

        user = getModels()['Exams_'].query.filter_by(username=current_user.username).first()
        reviewData = json.loads(user.j1)
        examData = json.loads(user.j2)



    try:
        tries12 = round(   (reviewData[str(semester) + '-1-2'][0] + reviewData[str(semester) + '-1-2'][1])   /2  )
    except:
        tries12 = 0
        reviewData[str(semester) + '-1-2'] = [0,0,0]
    try:
        tries34 = round(   (reviewData[str(semester) + '-3-4'][0] + reviewData[str(semester) + '-3-4'][1])   /2  )
    except:
        tries34 = 0
        reviewData[str(semester) + '-3-4'] = [0,0,0]

    ex12 = 0
    ex34 = 0


    if len(examData[str(semester) + '-1-2']) > 0:
        ex12 = round(   (examData[str(semester) + '-1-2'][0] + examData[str(semester) + '-1-2'][1])   /2  )
    if len(examData[str(semester) + '-3-4']) > 0:
        ex34 = round(   (examData[str(semester) + '-3-4'][0] + examData[str(semester) + '-3-4'][1])   /2  )



    examDict = {
        'total' : 0,
        'units' : 0,
        'asses' : 0,
        'tScore12': tries12,
        'tScore34': tries34,
        'tries12' : str(tries12) + '/20% - tries: ' + str(reviewData[str(semester) + '-1-2'][2]),
        'tries34' : str(tries34) + '/20% - tries: ' + str(reviewData[str(semester) + '-3-4'][2]),
        'ex12' : ex12,
        'ex34' : ex34
    }


    grades = get_grades(True, True)


    if grades['unitGrade'] > 0:
        u = grades['unitGrade'] * 30 / grades['maxU']
        examDict['units'] = round(u, 1)
    if grades['assGrade'] > 0:
        a = grades['assGrade'] * 30 / grades['maxA']
        examDict['asses'] = round(a, 1)


    examDict['total'] = examDict['units'] + examDict['asses'] + examDict['ex12'] + examDict['ex34']


    setDict = {
        '12' : 0,
        '34' : 0,
        'ex' : current_user.extra
    }


    if getModels()['Units_'].query.filter_by(unit='02').first():
        setDict['12'] = getModels()['Units_'].query.filter_by(unit='02').first().uA
    if getModels()['Units_'].query.filter_by(unit='04').first():
        setDict['34'] = getModels()['Units_'].query.filter_by(unit='04').first().uA

    counts = completeStatus('MT', current_user.username)

    SCHEMA = getSchema()
    DESIGN = schemaList[SCHEMA]['DESIGN']

    context = {
    'schema' : getSchema(),
    'Practice' : User.query.filter_by(id=1).first().extra,
    'title' : 'Exams',
    'theme' : DESIGN['titleColor'],
    'examString' : json.dumps(examDict),
    'setString' : json.dumps(setDict),
    'semester' : semester,
    'aCount': counts[0],
    'uCount': counts[1]
    }


    #return examDict['total']
    return render_template('units/exam_list_midterm.html', **context )



def completeStatus(time, name):

    print('COMPLETE STATUS', time, name)
    SCHEMA = getSchema()

    ICC = [3,6]

    partList = []

    if time == 'MT':
        if SCHEMA in ICC:
            partList = getInfo()['unit_mods_list'][0:20]
        else:
            partList = getInfo()['unit_mods_list'][0:16]
    else:
        if SCHEMA in ICC:
            partList = getInfo()['unit_mods_list'][20:40]
        else:
            partList = getInfo()['unit_mods_list'][16:32]

    if SCHEMA not in ICC:
        assignments = {
            'FN': ['05', '06', '07', '08'],
            'MT': ['01', '02', '03', '04']
        }
    else:
        assignments = {
            'FN': ['06', '07', '08', '09', '10'],
            'MT': ['01', '02', '03', '04', '05']
        }


    aCount = 0
    uCount = 0

    for model in getInfo()['aModsDict']:
        if model in assignments[time]:
            if getInfo()['aModsDict'][model].query.filter_by(username=name).first() and getInfo()['aModsDict'][model].query.filter_by(username=name).first().Grade > 0:
                aCount += 1

    for model in partList:
        #print (model)
        rows = model.query.all()
        block = False
        for row in rows:
            if name in ast.literal_eval(row.username) and block == False and int(row.Grade) > 0:
                uCount +=1
                block = True

    print('status', aCount, uCount)
    return [aCount, uCount]




@app.route ("/exam_list_final", methods=['GET','POST'])
@login_required
def exam_list_final():
    SCHEMA = getSchema()

    semester = int(User.query.filter_by(username='Chris').first().semester)

    ''' set exam practice '''
    try:
        user = getModels()['Exams_'].query.filter_by(username=current_user.username).first()
        reviewData = json.loads(user.j1)
        examData = json.loads(user.j2)
        print('exam_list_data_checked')
    except:
        if semester == 1:
            reviewDict = {
                    '1-1-2' : [],
                    '1-3-4' : [],
                    '1-5-6' : [],
                    '1-7-8' : []
                }
        else:
            reviewDict = {
                    '2-1-2' : [],
                    '2-3-4' : [],
                    '2-5-6' : [],
                    '2-7-8' : []
                }
        entry = getModels()['Exams_'](username=current_user.username, j1=json.dumps(reviewDict), j2=json.dumps(reviewDict))
        db.session.add(entry)
        db.session.commit()

        user = getModels()['Exams_'].query.filter_by(username=current_user.username).first()
        reviewData = json.loads(user.j1)
        examData = json.loads(user.j2)

    try:
        tries56 = round(   (reviewData[str(semester) + '-5-6'][0] + reviewData[str(semester) + '-5-6'][1])   /2  )
    except:
        tries56 = 0
        reviewData[str(semester) + '-5-6'] = [0,0,0,]
    try:
        tries78 = round(   (reviewData[str(semester) + '-7-8'][0] + reviewData[str(semester) + '-7-8'][1])   /2  )
    except:
        tries78 = 0
        reviewData[str(semester) + '-7-8'] = [0,0,0,]

    ex56 = 0
    ex78 = 0
    if len(examData[str(semester) + '-5-6']) > 0:
        ex56 = round(   (examData[str(semester) + '-5-6'][0] + examData[str(semester) + '-5-6'][1])   /2  )
    if len(examData[str(semester) + '-7-8']) > 0:
        ex78 = round(   (examData[str(semester) + '-7-8'][0] + examData[str(semester) + '-7-8'][1])   /2  )



    midterm = grades_midterm()[current_user.username]['Total']

    examDict = {
        'total' : 0,
        'units' : 0,
        'asses' : 0,
        'tries56' : str(tries56) + '/20% - tries: ' + str(reviewData[str(semester) + '-5-6'][2]),
        'tries78' : str(tries78) + '/20% - tries: ' + str(reviewData[str(semester) + '-7-8'][2]),
        'ex56' : ex56,
        'ex78' : ex78,
        'midterm' : midterm
    }

    grades = get_grades(True, True)

    if grades['unitGrade'] > 0:
        u = grades['unitGrade'] * 30 / grades['maxU']
        examDict['units'] = round(u, 1)
    if grades['assGrade'] > 0:
        a = grades['assGrade'] * 30 / grades['maxA']
        examDict['asses'] = round(a, 1)

    examDict['total'] = examDict['units'] + examDict['asses'] + examDict['ex56'] + examDict['ex78']

    setDict = {
        '56' : 0,
        '78' : 0,
        'ex' : current_user.extra
    }

    if getModels()['Units_'].query.filter_by(unit='06').first():
        setDict['56'] = getModels()['Units_'].query.filter_by(unit='06').first().uA
    if getModels()['Units_'].query.filter_by(unit='08').first():
        setDict['78'] = getModels()['Units_'].query.filter_by(unit='08').first().uA

    counts = completeStatus('FN', current_user.username)

    DESIGN = schemaList[SCHEMA]['DESIGN']

    context = {
    'schema' : getSchema(),
    'title' : 'Exams',
    'theme' : DESIGN['titleColor'],
    'examString' : json.dumps(examDict),
    'setString' : json.dumps(setDict),
    'SCHEMA' : SCHEMA,
    'semester' : semester,
    'aCount': counts[0],
    'uCount': counts[1]
    }

    return render_template('units/exam_list_final.html', **context)


@app.route ("/setStatus", methods=['POST'])
@login_required
def setStatus():

    username = request.form ['username']
    student = User.query.filter_by(username=username).first()

    if not student.extra:
        print('set 1')
        student.extra = 1
        db.session.commit()
    elif student.extra < 3:
        student.extra += 1
        db.session.commit()
    elif student.extra == 3:
        student.extra = 6
        db.session.commit()
    elif student.extra == 6:
        student.extra = 0
        db.session.commit()
    else:
        student.extra = 0
        db.session.commit()

    return jsonify({'student' : username, 'set' : student.extra})

@app.route ("/resetExam", methods=['POST'])
@login_required
def resetExam():

    username = request.form ['username']
    exam = request.form ['head']

    semester = User.query.filter_by(username='Chris').first().semester
    student = getModels()['Exams_'].query.filter_by(username=username).first()

    exams = {}

    if get_MTFN('grades') == 'MT':
        exams = {
            'exam1' : str(semester) + '-1-2',
            'exam2' : str(semester) + '-3-4'
        }
    if get_MTFN('grades') == 'FN':
        exams = {
            'exam1' : str(semester) + '-5-6',
            'exam2' : str(semester) + '-7-8'
        }

    examData = json.loads(student.j2)

    print('examData', semester, username, exam, examData, exams[exam], examData[exams[exam]] )


    examData[exams[exam]] = []
    newData = json.dumps(examData)
    print(newData)
    student.j2 = newData
    db.session.commit()

    return jsonify({'student' : username})

@app.route ("/resetAll", methods=['POST'])
@login_required
def resetAll():



    users = getUsers(getSchema())

    for u in users:
        if u.username != 'Chris':
            u.extra = 0
            db.session.commit()


    return jsonify({'result' : True})

@app.route ("/participation_check", methods=['GET','POST'])
@login_required
def participation_check():

    ICC = [3,6]

    SCHEMA = getSchema()
    time = get_MTFN('grades')

    if time == 'MT':
        if SCHEMA in ICC:
            partList = getInfo()['unit_mods_list'][0:20]
        else:
            partList = getInfo()['unit_mods_list'][0:16]
    else:
        if SCHEMA in ICC:
            partList = getInfo()['unit_mods_list'][20:40]
        else:
            partList = getInfo()['unit_mods_list'][16:32]

    checkDict = {}
    for model in partList:
        rows = model.query.all()
        m = str(model).split('U')[1]
        if m not in checkDict:
            checkDict[m] = {}
        for row in rows:
            if len(ast.literal_eval(row.username)) == 1:
                checkDict[m][row.username] = [ row.id, row.Grade, row.Ans01, row.Ans02, row.Ans03, row.Ans04, row.Ans05, row.Ans06, row.Ans07, row.Ans08]

    return render_template('instructor/check.html', checkString=json.dumps(checkDict))




@app.route ("/grades_final", methods=['GET','POST'])
@login_required
def grades_final():
    SCHEMA = getSchema()

    if current_user.id != 1:
        return redirect(url_for('home'))

    semester = int(User.query.filter_by(username='Chris').first().semester)

    gradesDict = {}
    completeDict = {}

    users = getUsers(SCHEMA)

    for user in users:
        gradesDict[user.username] = {
            'Status' : user.extra,
            'Name' : user.username,
            'ID' : user.studentID,
            'Total' : 0,
            'units' : 0,
            'uP' : 0,
            'asses' : 0,
            'aP' : 0,
            'tries1' : 0,
            'pscore1' : 0,
            'tries2' : 0,
            'pscore2' : 0,
            'exam1' : 0,
            'exam2' : 0,
            'rscore1' : '',
            'rscore2' : ''
        }
        completeDict[user.username] = completeStatus('FN', user.username)

    attendance = getModels()['Attendance_'].query.all()

    for a in attendance:
        if a.username in gradesDict:
            gradesDict[a.username]['Name'] += ' ='

    ### set max grades
    total_units = 0
    maxU = 0
    maxA = 0
    units = getModels()['Units_'].query.all()
    for unit in units:
        total = unit.u1 + unit.u2 + unit.u3 + unit.u4
        maxU += total*2
        maxA += unit.uA*2
        total_units += 1

    model_check = total_units*4 ## 4 units for each unit

    if SCHEMA == 9:
        uStart = 20
        aStart = 5
    else:
        uStart = 16
        aStart = 4

    for model in getInfo()['unit_mods_list'][uStart:(uStart + model_check)]:
        rows = model.query.all()
        unit = str(model).split('U')[1]
        for row in rows:
            names = ast.literal_eval(row.username)
            for name in names:
                gradesDict[name]['units'] += row.Grade

    model_check = total_units

    for model in getInfo()['ass_mods_list'][aStart:(aStart+ model_check)]:
        unit = str(model).split('A')[1]
        print(unit)
        rows = model.query.all()
        for row in rows:
            gradesDict[row.username]['asses'] += row.Grade


    practices = getModels()['Exams_'].query.all()
    for practice in practices:
        reviewData = ast.literal_eval(practice.j1)
        if len(reviewData[str(semester) + '-5-6']) > 2:
            gradesDict[practice.username]['tries1'] = reviewData[str(semester) + '-5-6'][2]
            gradesDict[practice.username]['pscore1'] = (reviewData[str(semester) + '-5-6'][0] + reviewData[str(semester) + '-5-6'][1])/2

        if len(reviewData[str(semester) + '-7-8']) > 2:
            gradesDict[practice.username]['tries2'] = reviewData[str(semester) + '-7-8'][2]
            gradesDict[practice.username]['pscore2'] = (reviewData[str(semester) + '-7-8'][0] + reviewData[str(semester) + '-7-8'][1])/2


        examData =  ast.literal_eval(practice.j2)
        if len(examData[str(semester) + '-5-6']) > 0 :
            gradesDict[practice.username]['exam1'] = round( (examData[str(semester) + '-5-6'][0] + examData[str(semester) + '-5-6'][1])/2 )
            gradesDict[practice.username]['rscore1'] = [examData[str(semester) + '-5-6'][0], examData[str(semester) + '-5-6'][1]]
        if len(examData[str(semester) + '-7-8']) > 0 :
            gradesDict[practice.username]['exam2'] = round( (examData[str(semester) + '-7-8'][0] + examData[str(semester) + '-7-8'][1])/2 )
            gradesDict[practice.username]['rscore2'] = [examData[str(semester) + '-7-8'][0], examData[str(semester) + '-7-8'][1]]


        print('exam_list_data_checked')


    maxE1 = 20
    maxE2 = 20

    for entry in gradesDict:
        if gradesDict[entry]['units'] > 0:
            percent = gradesDict[entry]['units']*30/maxU
            gradesDict[entry]['uP'] = round(percent, 1)
        if gradesDict[entry]['asses'] > 0:
            percent = gradesDict[entry]['asses']*30/maxA
            gradesDict[entry]['aP'] = round(percent, 1)

    for entry in gradesDict:
        sumTotal = gradesDict[entry]['uP'] + gradesDict[entry]['aP'] + gradesDict[entry]['exam1'] + gradesDict[entry]['exam2']
        gradesDict[entry]['Total'] = round(sumTotal)

    MTgrades = grades_midterm ()
    # print(MTgrades)
    for mt_student in MTgrades:
        gradesDict[mt_student]['MT'] = round(MTgrades[mt_student]['Total'], 1)

    bData = User.query.filter_by(id=1).first().info

    return render_template('instructor/grades.html', SCHEMA=SCHEMA, ansString=json.dumps(gradesDict), compString =json.dumps(completeDict), title="Grades", bonus=bData)


@app.route ("/grades_midterm", methods=['GET','POST'])
@login_required
def grades_midterm ():
    SCHEMA = getSchema()

    semester = int(User.query.filter_by(username='Chris').first().semester)

    gradesDict = {}
    completeDict = {}

    users = getUsers(SCHEMA)

    for user in users:
        gradesDict[user.username] = {
            'Status' : user.extra,
            'Name' : user.username,
            'ID' : user.studentID,
            'Total' : 0,
            'units' : 0,
            'uP' : 0,
            'asses' : 0,
            'aP' : 0,
            'tries1' : 0,
            'pscore1' : 0,
            'tries2' : 0,
            'pscore2' : 0,
            'exam1' : 0,
            'exam2' : 0,
            'rscore1' : '',
            'rscore2' : ''
        }
        completeDict[user.username] = completeStatus('MT', user.username)

    attendance = getModels()['Attendance_'].query.all()

    for a in attendance:
        if a.username in gradesDict:
            gradesDict[a.username]['Name'] += ' ='

    MT_marker = False
    ### set max grades

    total_units = 0
    if SCHEMA == 6 or SCHEMA == 3:
        midterm_unit_list = ['01', '02', '03', '04', '05']

    else:
        midterm_unit_list = ['01', '02', '03', '04']

    maxU = 0
    maxA = 0
    units = getModels()['Units_'].query.all()
    for un in units:
        if un.unit in midterm_unit_list:
            total = un.u1 + un.u2 + un.u3 + un.u4
            maxU += total*2
            maxA += un.uA*2
            total_units += 1
        else:
            print('Midterm Term Set')## we are now in final mode so ...
            if SCHEMA == 6 or SCHEMA == 3:
                total_units = 5
                maxU = 40
                maxA = 10
                MT_marker = True
            else:
                total_units = 4
                maxU = 32
                maxA = 8
                MT_marker = True


    model_check = total_units*4 ## 4 parts for each unit

    print('modelCheck ', model_check, getInfo()['unit_mods_list'] )

    for model in getInfo()['unit_mods_list'][0:model_check]:
        rows = model.query.all()
        unit = str(model).split('U')[1]
        for row in rows:
            names = ast.literal_eval(row.username)
            for name in names:
                try:
                    gradesDict[name]['units'] += row.Grade
                except:
                    print('user deleted')


    model_check = total_units

    for model in getInfo()['ass_mods_list'][0:model_check]:
        unit = str(model).split('A')[1]
        rows = model.query.all()
        for row in rows:
            gradesDict[row.username]['asses'] += row.Grade



    practices = getModels()['Exams_'].query.all()
    for practice in practices:
        reviewData = ast.literal_eval(practice.j1)
        if len(reviewData[str(semester) + '-1-2']) > 2:
            gradesDict[practice.username]['tries1'] = reviewData[str(semester) + '-1-2'][2]
            gradesDict[practice.username]['pscore1'] = (reviewData[str(semester) + '-1-2'][0] + reviewData[str(semester) + '-1-2'][1])/2
        if len(reviewData[str(semester) + '-3-4']) > 2:
            gradesDict[practice.username]['tries2'] = reviewData[str(semester) + '-3-4'][2]
            gradesDict[practice.username]['pscore2'] = (reviewData[str(semester) + '-3-4'][0] + reviewData[str(semester) + '-3-4'][1])/2


        examData =  ast.literal_eval(practice.j2)
        if len(examData[str(semester) + '-1-2']) > 0 :
            gradesDict[practice.username]['exam1'] = round( (examData[str(semester) + '-1-2'][0] + examData[str(semester) + '-1-2'][1])/2 )
            gradesDict[practice.username]['rscore1'] = [examData[str(semester) + '-1-2'][0], examData[str(semester) + '-1-2'][1]]
        if len(examData[str(semester) + '-3-4']) > 0 :
            gradesDict[practice.username]['exam2'] = round( (examData[str(semester) + '-3-4'][0] + examData[str(semester) + '-3-4'][1])/2 )
            gradesDict[practice.username]['rscore2'] = [examData[str(semester) + '-3-4'][0], examData[str(semester) + '-3-4'][1]]


        #print('exam_list_data_checked')


    maxE1 = 20
    maxE2 = 20

    for entry in gradesDict:
        if gradesDict[entry]['units'] > 0:
            percent = gradesDict[entry]['units']*30/maxU
            gradesDict[entry]['uP'] = round(percent, 1)
        if gradesDict[entry]['asses'] > 0:
            percent = gradesDict[entry]['asses']*30/maxA
            gradesDict[entry]['aP'] = round(percent, 1)

    for entry in gradesDict:
        sumTotal = gradesDict[entry]['uP'] + gradesDict[entry]['aP'] + gradesDict[entry]['exam1'] + gradesDict[entry]['exam2']
        gradesDict[entry]['Total'] = round(sumTotal)

    print(gradesDict)

    if MT_marker:
        return gradesDict
    else:
        if current_user.id != 1:
            return redirect(url_for('home'))
        else:
            return render_template('instructor/grades.html', SCHEMA=SCHEMA, title='Grades', ansString=json.dumps(gradesDict), compString=json.dumps(completeDict))


@app.route ("/updateClasswork", methods=['POST', 'GET'])
@login_required
def updateClasswork():

    unit = request.form ['unit']
    name = request.form ['name']
    team = request.form ['team']

    print(unit, name, team)

    print(getInfo()['uModsDict'][unit[0:2]])

    model = getInfo()['uModsDict'][unit[0:2]][int(unit[2])]

    data = model.query.filter_by(teamnumber=team).first()

    comment = None
    cDict = False

    try:
        comment = json.loads(data.Comment)
        cDict = True
        print('cDICT = True', data.Comment)
    except:
        comment = data.Comment
        print('cDICT = False', data.Comment)

    print(name, data.Grade, cDict)

    if name == 'grade' and cDict:
        if data.Grade == 0:
            data.Grade = 2
            comment['status'] = "Updated"
            data.Comment = json.dumps(comment)
            print('commit')
            db.session.commit()
        elif data.Grade == 2:
            data.Grade = 0
            comment['status'] = "Reopened"
            data.Comment = json.dumps(comment)
            db.session.commit()

    elif name == 'grade' and not cDict:
        if data.Grade > 0:
            data.Grade = 0
            data.Comment = 'Not completed correctly'
            db.session.commit()
        elif data.Grade == 0:
            data.Grade = 2
            data.Comment = 'Done'
            db.session.commit()

    else:
        teamArray = ast.literal_eval(data.username)
        if name in teamArray:
            teamArray.remove(name)
        else:
            teamArray.append(name)
        data.username = json.dumps(teamArray)
        db.session.commit()

    return jsonify({'unit' : unit, 'name' : name})


@app.route ("/resetAnswer", methods=['POST', 'GET'])
@login_required
def resetAnswer():

    unit = request.form ['unit']
    team = request.form ['team']
    question = request.form ['question']

    print(unit, team, question)

    print(getInfo()['uModsDict'][unit[0:2]])

    model = getInfo()['uModsDict'][unit[0:2]][int(unit[2])]

    data = model.query.filter_by(teamnumber=team).first()

    q = int(question)

    if q == 1:
        data.Ans01 = None
    elif q == 2:
        data.Ans02 = None
    elif q == 3:
        data.Ans03 = None
    elif q == 4:
        data.Ans04 = None
    elif q == 5:
        data.Ans05 = None
    elif q == 6:
        data.Ans06 = None
    elif q == 7:
        data.Ans07 = None
    elif q == 8:
        data.Ans08 = None

    if data.Grade == 2:
        data.Grade = 0
        ## change comment {} status?
    db.session.commit()

    return jsonify({'unit' : unit, 'team' : team, 'questions': question})



@app.route ("/classwork", methods=['GET','POST'])
@login_required
def classwork():
    if current_user.id != 1:
        return abort(403)

    SCHEMA = getSchema()

    cwDict = {}

    unitList = []

    ICC = [3,6]


    if get_MTFN('grades') == 'MT':
        if SCHEMA in ICC:
            unitList = getInfo()['unit_mods_list'][0:20]
        else:
            unitList = getInfo()['unit_mods_list'][0:16]
    else:
        if SCHEMA in ICC:
            unitList = getInfo()['unit_mods_list'][20:40]
        else:
            unitList = getInfo()['unit_mods_list'][16:32]


    for model in unitList:
        rows = model.query.all()
        unit = str(model).split('U')[1]
        cwDict[unit] = {}

        for row in rows:
            cwDict[unit][row.id] = {}
            cwDict[unit][row.id]['ID'] = row.id
            try:
                cwDict[unit][row.id]['names'] = ast.literal_eval(row.username)
                print('TRY classwork', cwDict[unit][row.id]['names'])
            except:
                cwDict[unit][row.id]['names'] = [row.username]

            cwDict[unit][row.id]['team'] = row.teamnumber
            cwDict[unit][row.id]['1'] = row.Ans01
            cwDict[unit][row.id]['2'] = row.Ans02
            cwDict[unit][row.id]['3'] = row.Ans03
            cwDict[unit][row.id]['4'] = row.Ans04
            cwDict[unit][row.id]['5'] = row.Ans05
            cwDict[unit][row.id]['6'] = row.Ans06
            cwDict[unit][row.id]['7'] = row.Ans07
            cwDict[unit][row.id]['8'] = row.Ans08
            cwDict[unit][row.id]['Comment'] = row.Comment
            cwDict[unit][row.id]['Grade'] = row.Grade



    return render_template('instructor/classwork.html', ansString=json.dumps(cwDict), title='Classwork', SCHEMA=SCHEMA)




######## Assignments //////////////////////////////////////////////

@app.route ("/assignments", methods=['GET','POST'])
@login_required
def assignment_list():

    srcDict = get_sources()
    print(srcDict)

    ''' deal with grades '''
    grades = get_grades(True, False) # ass / unit
    assGrade = grades['assGrade']
    recs = grades['assGradRec']
    maxA = grades['maxA']
    print ('RECS', recs)

    assDict = {}
    for unit in recs:
        assDict[unit] = {
            'Deadline' : srcDict[unit]['Deadline'],
            'Title' : srcDict[unit]['Title'],
            'Grade' : recs[unit]['Grade'],
            'Comment' : recs[unit]['Comment']
        }

    SCHEMA = getSchema()
    DESIGN = schemaList[SCHEMA]['DESIGN']

    return render_template('units/assignment_list.html', legend='Assignments Dashboard',
    Dict=json.dumps(assDict), Grade=assGrade, max=maxA, title='Assignments', theme=DESIGN)


@app.route('/audioUpload', methods=['POST', 'GET'])
def audioUpload():
    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

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


    model = getInfo()['aModsDict'][unit]
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


@app.route("/ass/<string:unit>", methods = ['GET', 'POST'])
@login_required
def ass(unit):
    SCHEMA = getSchema()
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    srcDict = get_sources()
    source = srcDict[unit]['Materials']['A']


    setting =  getModels()['Units_'].query.filter_by(unit=unit).first().uA
    if setting != 1:
        flash('This assignment is not open yet', 'danger')
        return redirect(request.referrer)

    # models update
    assDict = getInfo()['aModsDict']
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


