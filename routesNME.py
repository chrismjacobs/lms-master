import sys, boto3, random, base64, os, secrets, time, datetime, json
from sqlalchemy import asc, desc, func, or_
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *
from models import *
import ast
from pprint import pprint
from routesUser import get_grades, get_sources
from random import shuffle

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource
s3_client = BaseConfig.s3_client
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN
DEBUG = BaseConfig.DEBUG


projectDict = {
        '01' : U011U,
        '02' : U021U,
        '03' : U031U,
        '04' : U041U,
        '05' : U051U,
        '06' : U061U,
        '07' : U071U,
        '08' : U081U,
    }

def create_folder(unit, teamnumber, nameRange):
    keyName = (unit + '/' + teamnumber + '/')  #adding '/' makes a folder object
    print (keyName)
    try:
        # use s3_client instead of resource to use head_object or list_objects
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=keyName)
        print('Folder Located')
    except:
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=keyName)
        object = s3_resource.Object(S3_BUCKET_NAME, keyName + str(nameRange) + '.txt')
        object.put(Body='some_binary_data')
        print('Folder Created for', teamnumber, nameRange)
    else:
        print('Create_Folder_Pass')
        pass

    return keyName


@app.route ("/nme_novels", methods=['GET','POST'])
@login_required
def nme_novels():

    novels = ['01', '02', '03']

    completed = 0
    nCount = 0
    nDict = {}
    for n in novels:
        project = projectDict[n].query.filter_by(username=current_user.username).first()
        if project:
            nCount +=1
            nDict[n] = json.loads(project.Ans01)

    nString = json.dumps(nDict)


    return render_template('nme/nme_novels.html', completed=completed, nCount=nCount, nString=nString, legend='NME Projects')

@app.route ("/addNovel", methods=['GET','POST'])
@login_required
def addNovel():
    print('ADD_NOVEL')
    novel = request.form ['novel']
    number = json.loads(novel)['number']

    project = projectDict[number]
    sums = {}
    recs = {}

    entry = project(username=current_user.username, Ans01=novel, Ans02=json.dumps(sums), Ans03=json.dumps(recs))
    db.session.add(entry)
    db.session.commit()

    return jsonify({'nValue' : novel, 'nKey':number })

@app.route ("/addSum", methods=['GET','POST'])
@login_required
def addSum():
    print('ADD_SUM')
    novel = request.form ['novel']
    chapter = request.form ['chapter']
    novel_number = novel['number']
    chap_number = chapter['number']

    project = projectDict[novel_number]

    current_sums = json.loads(project.Ans02)
    current_sums[chap_number] = json.loads(chapter)
    project.Ans02 = json.dumps(current_sums)

    return jsonify({'sObj' : current_sums})

@app.route ("/sum/<string:index>", methods=['GET','POST'])
@login_required
def nme_sum(index):

    project = projectDict[index].query.filter_by(username=current_user.username).first()
    novel = json.loads(project.Ans01)
    sums = json.loads(project.Ans02)

    html = 'nme/nme_sums.html'


    return render_template(html, legend='Chapter Summaries', nString=project.Ans01, sString=project.Ans02)

def get_all_snl_values(nested_dictionary):
    detected = 0
    for key, value in nested_dictionary.items():
        if type(value) is dict:
            print ('DICT FOUND', value)
            if get_all_snl_values(value) != 0:
                detected += get_all_snl_values(value)
        else:
            if value == None or value == "":
                print('CHECK', key, value)
                detected += 1

    return detected


@app.route('/storeB64', methods=['POST'])
def storeB64():
    unit = request.form ['unit']
    team = request.form ['team']
    mode = request.form ['mode']
    b64 = request.form ['b64']
    question = request.form ['question']
    b64data = request.form ['b64data']
    fileType = request.form ['fileType']
    total = request.form ['total']

    project = unitDict[unit]
    project_data = project.query.filter_by(teamnumber=team).first()
    project_answers = json.loads(project_data.Ans02)

    if b64 == 'i':
        print('PROCESSING IMAGE')
        image = base64.b64decode(b64data)
        file_key = project_answers[question]['imageLink']
        if file_key:
            print('file_key_found ', file_key)
            file_key_split = file_key.split('com/')[1]
            s3_resource.Object(S3_BUCKET_NAME, file_key_split).delete()
        else:
            print('no file_key found')
        now = datetime.now()
        time = now.strftime("_%M%S")
        print("time:", time)
        filename = unit + '/' + team + '/' + question + time + '_image.' + fileType
        imageLink = S3_LOCATION + filename
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=image)

        project_answers[question]['imageLink'] = imageLink
        project_data.Ans02 = json.dumps(project_answers)
        project_data.Ans04 = total
        db.session.commit()

    if b64 == 'a':
        print('PROCESSING AUDIO')
        audio = base64.b64decode(b64data)
        file_key = project_answers[question]['audioLink']
        if file_key:
            print('file_key_found ', file_key)
            file_key_split = file_key.split('com/')[1]
            s3_resource.Object(S3_BUCKET_NAME, file_key_split).delete()
        else:
            print('no file_key found')
        now = datetime.now()
        time = now.strftime("_%M%S")
        print("time:", time)
        filename = unit + '/' + team + '/' + question + time + '_audio.mp3'
        audioLink = S3_LOCATION + filename
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)

        project_answers[question]['audioLink'] = audioLink
        project_data.Ans02 = json.dumps(project_answers)
        project_data.Ans04 = total
        db.session.commit()

    return jsonify({'question' : question})

@app.route('/storeAnswer', methods=['POST'])
def storeAnswer():
    unit = request.form ['unit']
    team = request.form ['team']
    mode = request.form ['mode']
    question = request.form ['question']
    ansOBJ = request.form ['ansOBJ']
    total = request.form ['total']

    project = unitDict[unit]
    project_answers = project.query.filter_by(teamnumber=team).first()

    if mode == 'qna':
        project_answers.Ans01 = ansOBJ
        project_answers.Ans03 = total  #12 will be the maximum
    if mode == 'snl':
        project_answers.Ans02 = ansOBJ
        project_answers.Ans04 = total

    db.session.commit()

    return jsonify({'question' : question})


@app.route('/updateAnswers', methods=['POST'])
def updateAnswers():
    unit = request.form ['unit']
    team = request.form ['team']
    mode = request.form ['mode']

    project = unitDict[unit]
    project_answers = project.query.filter_by(teamnumber=team).first()

    if mode == 'qna':
        ansString = str(project_answers.Ans01)
    if mode == 'snl':
        ansString = str(project_answers.Ans02)



    return jsonify({'ansString' : ansString})



def get_team_data(unit, team):
    project = unitDict[unit]
    questions = project.query.filter_by(teamnumber=team).first()
    teamMembers = ast.literal_eval(questions.username)

    teamDict = {}
    for member in teamMembers:
        try:
            teamDict[member] = S3_LOCATION + User.query.filter_by(username=member).first().image_file
        except:
            teamDict[member] = None

    project_answers = unitDict[unit].query.filter_by(teamnumber=team).first()

    return {
        'project_answers' : project_answers,
        'teamMembers' : json.dumps(teamDict)
    }



@app.route('/addWord', methods=['POST'])
def addWord():
    b64Dict = json.loads(request.form ['b64String'])
    print(b64Dict)
    print('ADDWORD ACTIVE')
    word = b64Dict ['word']
    user = request.form ['user']
    sentence= b64Dict ['sentence']
    unit = request.form ['unit']
    team = request.form ['team']

    project = unitDict[unit].query.filter_by(teamnumber=team).first()

    ansDict = ast.literal_eval(project.Ans02)

    qCount = len(ansDict)
    print('qCount', qCount)

    print('PROCESSING IMAGE')
    image = base64.b64decode(b64Dict['image_b64'])
    filename = unit + '/' + team + '/' + word + '_image.' + b64Dict['fileType']
    imageLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=image)

    print('PROCESSING AUDIO')
    audio = base64.b64decode(b64Dict['audio_b64'])
    filename = unit + '/' + team + '/' + word + '_audio.mp3'
    audioLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)

    ansDict[word] = {
            'word' : word,
            'sentence' : sentence,
            'audioLink' : audioLink,
            'imageLink' : imageLink,
            'user' : user
        }

    ansString = json.dumps(ansDict)

    project.Ans02 = ansString
    project.Ans04 = len(ansDict)
    db.session.commit()


    return jsonify({'word' : word, 'newDict' : ansString, 'qCount' : qCount })



@app.route ("/abc/<string:qs>/<string:unit>/<int:team>", methods=['GET','POST'])
@login_required
def abc_setup(qs, unit, team):

    srcDict = get_projects()
    meta = srcDict[unit]
    print(meta['M1'])

    data = get_team_data(unit, team)
    project_answers = data['project_answers']
    teamMembers = data['teamMembers']


    if current_user.username not in teamMembers :
        flash('You are not on the team for this project', 'warning')
        return (redirect (url_for('abc_dash')))

    if qs == 'qna':
        testDict = {}
        for i in range (1, 7):
            testDict[i] = {
                'topic' : None,
                'question' : None,
                'answer' : None,
                'writer' : None
            }
        html = 'abc/abc_qna.html'
        ansDict = project_answers.Ans01
        current_score = None

    if qs == 'snl':
        testDict = {}
        for i in range (1, 7):
            testDict[i] = {
            'word' : None,
            'sentence' : None,
            'imageLink' : None,
            'audioLink' : None,
            'user' : None,
            }
        html = 'abc/abc_snl.html'
        ansDict = project_answers.Ans02
        current_score = project_answers.Ans04


    return render_template(html, legend='Questions & Answers',
    meta=meta,
    teamMembers=teamMembers,
    ansDict=ansDict,
    current_score=current_score,
    testDict=str(json.dumps(testDict))
    )


'''Instructor dashboard'''
@app.route ("/abc_dash", methods=['GET','POST'])
@login_required
def abc_dash():
    taList = ['Chris', 'Robin', 'William']

    if current_user.username not in taList:
        return redirect('home')

    srcDict = get_projects()
    pprint(srcDict)
    abcDict = { }
    for src in srcDict:
        # check sources against open units in model
        # src = unit
        if Units.query.filter_by(unit=src).count() == 1:
            abcDict[src] = {
                'Title' : srcDict[src]['Title'],
                'Unit' : src,
                'Teams' : {}
            }

            projects = unitDict[src].query.all()
            for proj in projects:
                abcDict[src]['Teams'][proj.teamnumber] = {'team' : proj.username,
                                                          'QNA' : proj.Ans03,
                                                          'SNL' : proj.Ans04
                                                          }

    pprint (abcDict)

    return render_template('abc/abc_dash.html', legend='ABC Dash', abcString = json.dumps(abcDict))

# instructor check
@app.route ("/abc_check/<string:unit>", methods=['GET','POST'])
@login_required
def abc_check(unit):
    taList = ['Chris', 'Robin', 'William']

    if current_user.username not in taList:
        return redirect('home')

    srcDict = get_projects()
    title = srcDict[unit]['Title']


    checkDict = { }

    projects = unitDict[unit].query.all()
    for proj in projects:
        print(proj.teamnumber)
        checkDict[proj.teamnumber] = {
            'team' : ast.literal_eval(proj.username),
            'qna_list' : json.loads(proj.Ans01),
            'qna_score' : proj.Ans03,
            'snl_list' : json.loads(proj.Ans02),
            'snl_score' : proj.Ans04,
            }

    pprint (checkDict)

    return render_template('abc/abc_check.html', legend='QNA Check', title=title, abcString = json.dumps(checkDict))



'''Exam '''
@app.route ("/abc_exam/<string:qORs>/<string:unit>/<string:team>", methods=['GET','POST'])
@login_required
def abc_exam(qORs, unit, team):

    ## get_team_data will check if user is exam ready or not
    team_data = get_team_data(unit, team)
    teamMembers = team_data['teamMembers']

    if current_user.extra == 3:
        print('exam user')
    elif current_user.username not in teamMembers:
        flash('Exam not ready - Please see instructor', 'warning')
        return redirect(url_for('abc_list'))

    srcDict = get_projects()
    meta = srcDict[unit]

    print('exam', unit, team)


    data = team_data['project_answers']
    print(team_data)
    source = meta['M1']
    print(source)
    qnaString = data.Ans01
    snlString = data.Ans02
    snlDict = json.loads(data.Ans02)

    orderList = ['1','2','3','4','5','6']
    random.shuffle(orderList)

    print('orderList', orderList)

    count = 1
    orderDict = {}
    for number in orderList:
        orderDict[count] = [number, snlDict[number]['audioLink']]
        count +=1

    print('orderDict', orderDict)

    if qORs == 'qna':
        html = 'abc/abc_exam_qna.html'
    else:
        html = 'abc/abc_exam_snl.html'

    return render_template(html, legend='ABC Exam', title=unit, meta=meta, orderDict=json.dumps(orderDict), qnaString=qnaString, snlString=snlString)
# exam format

def midtermGrades():
    try:
        checkUser = Exams.query.filter_by(username=current_user.username).first().username
    except:
        user = Exams(username=current_user.username, j1='{}', j2='{}', j3='{}', j4='{}')
        db.session.add(user)
        db.session.commit()

    user = Exams.query.filter_by(username=current_user.username).first()

    return user


@app.route('/updateGrades', methods=['POST'])
def updateGrades():
    qORs = request.form ['qORs']
    unit = request.form ['unit']
    team = request.form ['team']
    grade = request.form ['grade']

    user = midtermGrades()

    if qORs == 'qna':
        #examDict = json.loads(user.j1)
        examDict = json.loads(user.j3)
    elif qORs == 'snl':
        #examDict = json.loads(user.j2)
        examDict = json.loads(user.j4)

    print('before', examDict)

    entryChecker = True
    for entry in examDict:
        if examDict[entry]['team'] == team and examDict[entry]['unit'] == unit:
            entryChecker = False

    if entryChecker:
        count = len(examDict)
        examDict[count+1] = {
            'unit' : unit,
            'team' : team,
            'grade' : grade
            }

        if qORs == 'qna':
            #user.j1 = json.dumps(examDict)
            user.j3 = json.dumps(examDict)
            db.session.commit()
            print('qnaCommit')
        elif qORs == 'snl':
            #user.j2 = json.dumps(examDict)
            user.j4 = json.dumps(examDict)
            db.session.commit()
            print('snlCommit')

    print('after', examDict)

    return jsonify({'grade' : grade})


@app.route ("/abc_grades", methods=['GET','POST'])
@login_required
def abc_grades():

    gradesDict = {}

    users = User.query.all()

    for user in users:
        gradesDict[user.username] = {
            'Student' : {
                'name' :user.username,
                'id' : user.studentID,
                'Status' : user.extra
             },
            '04' : {
                'team' : 0,
                'QNA' : 0,
                'SNL' : 0,
                'QNA_check' : 0,
                'SNL_check' : 0,
                'QNA_grades' : [],
                'SNL_grades' : []
            },
            '05' : {
                'team' : 0,
                'QNA' : 0,
                'SNL' : 0,
                'QNA_check' : 0,
                'SNL_check' : 0,
                'QNA_grades' : [],
                'SNL_grades' : []
            },
            '06' : {
                'team' : 0,
                'QNA' : 0,
                'SNL' : 0,
                'QNA_check' : 0,
                'SNL_check' : 0,
                'QNA_grades' : [],
                'SNL_grades' : []
            },
            '07' : {
                'team' : 0,
                'QNA' : 0,
                'SNL' : 0,
                'QNA_check' : 0,
                'SNL_check' : 0,
                'QNA_grades' : [],
                'SNL_grades' : []
            },
            '08' : {
                'team' : 0,
                'QNA' : 0,
                'SNL' : 0,
                'QNA_check' : 0,
                'SNL_check' : 0,
                'QNA_grades' : [],
                'SNL_grades' : []
            },

        }

    exams = Exams.query.all()

    models = {
        #'00' : U001U,
        #'01' : U011U,
        #'02' : U021U,
        #'03' : U031U,
        '04' : U041U,
        '05' : U051U,
        '06' : U061U,
        '07' : U071U,
        '08' : U081U,
    }

    for model in models:
        projects = models[model].query.all()
        for proj in projects:
            team = ast.literal_eval(proj.username)
            for stu in team:
                gradesDict[stu][model]['QNA'] = proj.Ans03
                gradesDict[stu][model]['SNL'] = proj.Ans04
                gradesDict[stu][model]['team'] = str(proj.teamnumber)

    for exam in exams:
        #break
       #QNA = json.loads(exam.j1)
        QNA = json.loads(exam.j3)
        for record in QNA:
            entry = QNA[record]
            print(exam.username, entry)
            if entry['team'] == gradesDict[exam.username][entry['unit']]['team']:
                gradesDict[exam.username][entry['unit']]['QNA_check'] = 1
            else:
                gradesDict[exam.username][ entry['unit'] ]['QNA_grades'].append(entry['grade'])

        #SNL = json.loads(exam.j2)
        SNL = json.loads(exam.j4)
        for record in SNL:
            entry = SNL[record]
            print(exam.username, entry)
            if entry['team'] == gradesDict[exam.username][entry['unit']]['team']:
                gradesDict[exam.username][entry['unit']]['SNL_check'] = 1
            else:
                gradesDict[exam.username][ entry['unit'] ]['SNL_grades'].append(entry['grade'])


    return render_template('abc/abc_grades.html', ansString=json.dumps(gradesDict))