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


unitDict = {
        '00' : U001U,
        '01' : U011U,
        '02' : U012U,
        '03' : U013U,
        '04' : U014U,
        '05' : U021U,
        '06' : U022U,
        '07' : U023U,
        '08' : U024U,
        '09' : U031U,
        '10' : U032U,
        '11' : U033U,
        '12' : U034U
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


@app.route ("/fse/make_teams/<string:unit>/<string:number>/", methods=['GET','POST'])
@login_required
def project_teams(unit, number):
    if current_user.id != 1:
        return abort(403)

    print('make team unit', unit)
    print('make team number', number)

    project = unitDict[unit]
    print (project, project.query.all())

    #create a dictionary of teams
    attTeams = Attendance.query.all()
    teamsDict = {}
    for att in attTeams:
        if att.teamnumber in teamsDict:
            teamsDict[att.teamnumber].append(att.username)
        else:
            teamsDict[att.teamnumber] = [att.username]

    print(teamsDict)

    manualTeams = {

        #10: ['Fiona', 'Ann', 'Penny Lai', 'Yui'],
        1 : ['Chris'],

    }

    '''control which teams are added'''

    if DEBUG == False:
        team_dict = teamsDict
    else:
        team_dict = manualTeams

    # prepare answers for QNA
    qnaDict = {}
    for i in range (1, 7):
        qnaDict[i] = {
            'question' : None,
            'answer' : None,
            'user' : None
        }

    snlDict = {}
    for i in range (1, 7):
        snlDict[i] = {
            'word' : None,
            'sentence' : None,
            'imageLink' : None,
            'audioLink' : None,
            'user' : None,
        }

    rpDict = {'rpAudio': None}
    for i in range (1, 4):
        rpDict[i] = {
            'question' : None,
            'answer' : [ None, None, None ],
            'user' : None
        }

    #make a list of teams already set up
    teams = []
    for pro in project.query.all():
        teams.append(pro.teamnumber)

    print('teams', teams)

    returnStr = str(team_dict)
    for team in team_dict:
        if team in teams:
            returnStr = 'Error - check table'
            break
        print(unit, team_dict)
        create_folder(unit, str(team), team_dict[team])
        teamStart = project(
            teamnumber=int(team),
            username=str(team_dict[team]),
            Ans01=str(json.dumps(qnaDict)),
            Ans02=str(json.dumps(snlDict)),
            Ans03=str(json.dumps(rpDict))
            )
        db.session.add(teamStart)
        db.session.commit()

    return returnStr


def get_projects():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    sDict = json.loads(file_content)  # json loads returns a dictionary
    projectDict = {}
    for week in sDict:
        try:
            if int(sDict[week]['Unit']) >= 0:
                #print('2')
                unitNumber = sDict[week]['Unit']
                projectDict[unitNumber] = {}
                section = sDict[week]
                #projectDict[unitNumber] = sDict[week]

                projectDict[unitNumber]['Title'] = section['Title']
                projectDict[unitNumber]['Date'] = section['Date']
                projectDict[unitNumber]['M1'] = section['M1']
                projectDict[unitNumber]['M2'] = section['M2']
        except:
            #print('except', sDict[week]['Unit'])
            pass

    #pprint(projectDict)

    return projectDict


def get_tests(unit, team):
    user = midtermGrades()

    qna = json.loads(user.j1)
    snl = json.loads(user.j2)
    rp = json.loads(user.j3)
    #qna = json.loads(user.j3)
    #snl = json.loads(user.j4)

    qnaCount = 0
    for test in qna:
        #print ('CHECK', qna[test]['unit'], unit ,  qna[test]['team'], team)
        if qna[test]['unit'] == str(unit) and qna[test]['team'] == str(team):
            qnaCount = 1
    snlCount = 0
    for test in snl:
        if snl[test]['unit'] == str(unit) and snl[test]['team'] == str(team):
            snlCount = 1
    rpCount = 0
    for test in rp:
        if rp[test]['unit'] == str(unit) and rp[test]['team'] == str(team):
            rpCount = 1

    return { 'snlCount' : snlCount, 'qnaCount' : qnaCount, 'rpCount' : rpCount }



@app.route ("/fse_list", methods=['GET','POST'])
@login_required
def fse_list():
    srcDict = get_projects()
    print('srcDict', srcDict)

    unitList = []
    #unitList = ['04', '05', '06', '07','08']
    fseDict = {}
    for src in srcDict:
        # check sources against open units in model
        # src == unit
        if src in unitList:
            pass
        elif Units.query.filter_by(unit=src).count() == 1:
            fseDict[src] = {
                'Title' : srcDict[src]['Title'],
                'Team'  : 'Not set up yet',
                'Number' : 0,
                'QTotal' : 0,
                'STotal' : 0,
                'RTotal' : 0,
                'QTest' : 0,
                'STest' : 0,
                'RTest' : 0,
            }

            projects = unitDict[src].query.all()
            for proj in projects:
                tests = get_tests(src, proj.teamnumber)
                if current_user.username in ast.literal_eval(proj.username):
                    fseDict[src]['Team'] = proj.username
                    fseDict[src]['Number'] = proj.teamnumber
                    fseDict[src]['QTotal'] = proj.Ans04
                    fseDict[src]['STotal'] = proj.Ans05
                    fseDict[src]['RTotal'] = proj.Ans06
                    fseDict[src]['QTest'] = tests['qnaCount']
                    fseDict[src]['STest'] = tests['snlCount']
                    fseDict[src]['RTest'] = tests['rpCount']
                    #pass

    #pprint (fseDict)

    examDict = {}

    '''
    for src in srcDict:
        if int(src) < 4: # change to match number of units
            pass
        else:
            examDict[src] = {}
            try:
                teamCheck = int(fseDict[src]['Number'])
                selector = teamCheck % 2
                #print('selector', selector)
            except:
                selector = 0

            if Units.query.filter_by(unit=src).count() == 1:
                projects = unitDict[src].query.all()

                for proj in projects:

                    if int(proj.teamnumber) > 20:
                        pass
                    elif fseDict[src]['Number'] == proj.teamnumber:
                        pass
                    elif selector == 0 and proj.teamnumber % 2 != 0:
                        pass
                    elif selector != 0 and proj.teamnumber % 2 == 0:
                        pass
                    else:
                        examDict[src][proj.teamnumber] = {
                            'QTotal' : proj.Ans03,
                            'STotal' : proj.Ans04,
                            'Qscore' : 0,
                            'Sscore' : 0,
                            }

    user = midtermGrades()
    #qna = json.loads(user.j1)
    #snl = json.loads(user.j2)
    qna = json.loads(user.j3)
    snl = json.loads(user.j4)
    #print (qna)
    #print (snl)

    for entry in qna:
        unit = qna[entry]['unit']
        team = qna[entry]['team']
        grade = qna[entry]['grade']
        try:
            #print(examDict[unit][int(team)]['Qscore'])
            examDict[unit][int(team)]['Qscore'] = grade
        except:
            print('FAIL QNA')

    for entry in snl:
        unit = snl[entry]['unit']
        team = snl[entry]['team']
        grade = snl[entry]['grade']
        try:
            #print(examDict[unit][int(team)]['Sscore'])
            examDict[unit][int(team)]['Sscore'] = grade
        except:
            print('FAIL QNA')
    '''

    source = srcDict['00']['M2']

    return render_template('fse/fse_list.html', legend='FSE Projects', source=source, fseDict=json.dumps(fseDict),  examDict=json.dumps(examDict))


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

def countTotal(ansOBJ):
    total = 0
    data = json.loads(ansOBJ)
    print(data)
    for key in data:
        if key == 'rpAudio':
            if data[key] != None:
                total += 1
        else:
            score = True
            for item in data[key]:
                if type(data[key][item]) == list and "" in data[key][item]:
                    score = False
                elif data[key][item] == None:
                    score = False
            if score:
                total += 1

    return total

@app.route('/FSEstoreB64', methods=['POST'])
def storeB64():
    unit = request.form ['unit']
    team = request.form ['team']
    mode = request.form ['mode']
    b64 = request.form ['b64']
    question = request.form ['question']
    b64data = request.form ['b64data']
    fileType = request.form ['fileType']

    project = unitDict[unit]
    project_data = project.query.filter_by(teamnumber=team).first()
    if b64 == 'rp':
        project_answers = json.loads(project_data.Ans03)
    else:
        project_answers = json.loads(project_data.Ans02)

    if b64 == 'a':
        link = 'audioLink'
        file_key = project_answers[question][link]
    elif b64 == 'i':
        link = 'imageLink'
        file_key = project_answers[question][link]
    elif b64 == 'rp':
        link = 'rpAudio'
        file_key = project_answers[link]

    print('PROCESSING: ' + link)
    data = base64.b64decode(b64data)
    if file_key:
        print('file_key_found ', file_key)
        file_key_split = file_key.split('com/')[1]
        s3_resource.Object(S3_BUCKET_NAME, file_key_split).delete()
    else:
        print('no file_key found')
    now = datetime.now()
    time = now.strftime("_%M%S")
    print("time:", time)
    filename = unit + '/' + team + '/' + question + time + '_' + link + '.' + fileType
    fileLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=data)

    aORi = ['a', 'i']
    if b64 in aORi:
        project_answers[question][link] = fileLink
        project_data.Ans02 = json.dumps(project_answers)
        project_data.Ans05 = countTotal(json.dumps(project_answers))
    else:
        project_answers[link] = fileLink
        project_data.Ans03 = json.dumps(project_answers)
        project_data.Ans06 = countTotal(json.dumps(project_answers))
    db.session.commit()

    return jsonify({'question' : question})


@app.route('/FSEstoreAnswer', methods=['POST'])
def storeAnswer():
    unit = request.form ['unit']
    team = request.form ['team']
    mode = request.form ['mode']
    question = request.form ['question']
    ansOBJ = request.form ['ansOBJ']

    project = unitDict[unit]
    project_answers = project.query.filter_by(teamnumber=team).first()

    if mode == 'qna':
        project_answers.Ans01 = ansOBJ
        project_answers.Ans04 = countTotal(ansOBJ)
    if mode == 'snl':
        project_answers.Ans02 = ansOBJ
        project_answers.Ans05 = countTotal(ansOBJ)
    if mode == 'rp':
        project_answers.Ans03 = ansOBJ
        project_answers.Ans06 = countTotal(ansOBJ)

    db.session.commit()

    return jsonify({'question' : question})


@app.route('/FSEupdateAnswers', methods=['POST'])
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
    if mode == 'rp':
        ansString = str(project_answers.Ans03)



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



@app.route ("/fse/<string:qs>/<string:unit>/<int:team>", methods=['GET','POST'])
@login_required
def fse_setup(qs, unit, team):

    srcDict = get_projects()
    meta = srcDict[unit]
    print(meta['M1'])

    data = get_team_data(unit, team)
    project_answers = data['project_answers']
    teamMembers = data['teamMembers']


    if current_user.username not in teamMembers :
        flash('You are not on the team for this project', 'warning')
        return (redirect (url_for('fse_dash')))

    if qs == 'qna':
        testDict = {}
        for i in range (1, 7):
            testDict[i] = {
                'question' : None,
                'answer' : None,
                'user' : None
            }
        html = 'fse/fse_qna.html'
        ansDict = project_answers.Ans01
        current_score = project_answers.Ans04

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
        html = 'fse/fse_snl.html'
        ansDict = project_answers.Ans02
        current_score = project_answers.Ans05

    if qs == 'rp':
        testDict = {'audio': None}
        for i in range (1, 4):
            testDict[i] = {
            'question' : None,
            'answer' : None,
            'user' : None
            }
        html = 'fse/fse_rp.html'
        ansDict = project_answers.Ans03
        current_score = project_answers.Ans06


    return render_template(html, legend='Questions & Answers',
    meta=meta,
    teamMembers=teamMembers,
    ansDict=ansDict,
    current_score=current_score,
    testDict=str(json.dumps(testDict))
    )


'''Instructor dashboard'''
@app.route ("/fse_dash", methods=['GET','POST'])
@login_required
def fse_dash():
    taList = ['Chris', 'Robin', 'William']

    if current_user.username not in taList:
        return redirect('home')

    srcDict = get_projects()
    pprint(srcDict)
    fseDict = { }
    for src in srcDict:
        # check sources against open units in model
        # src = unit
        if Units.query.filter_by(unit=src).count() == 1:
            fseDict[src] = {
                'Title' : srcDict[src]['Title'],
                'Unit' : src,
                'Teams' : {}
            }

            projects = unitDict[src].query.all()
            for proj in projects:
                fseDict[src]['Teams'][proj.teamnumber] = {'team' : proj.username,
                                                          'QNA' : proj.Ans03,
                                                          'SNL' : proj.Ans04
                                                          }

    pprint (fseDict)

    return render_template('fse/fse_dash.html', legend='FSE Dash', fseString = json.dumps(fseDict))

# instructor check
@app.route ("/fse_check/<string:unit>", methods=['GET','POST'])
@login_required
def fse_check(unit):
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

    return render_template('fse/fse_check.html', legend='QNA Check', title=title, fseString = json.dumps(checkDict))



'''Exam '''
@app.route ("/fse_exam/<string:qORs>/<string:unit>/<string:team>", methods=['GET','POST'])
@login_required
def fse_exam(qORs, unit, team):

    ## get_team_data will check if user is exam ready or not
    team_data = get_team_data(unit, team)
    teamMembers = team_data['teamMembers']

    if current_user.extra == 3:
        print('exam user')
    elif current_user.username not in teamMembers:
        flash('Exam not ready - Please see instructor', 'warning')
        return redirect(url_for('fse_list'))

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
        html = 'fse/fse_exam_qna.html'
    else:
        html = 'fse/fse_exam_snl.html'

    return render_template(html, legend='FSE Exam', title=unit, meta=meta, orderDict=json.dumps(orderDict), qnaString=qnaString, snlString=snlString)
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


@app.route ("/fse_grades", methods=['GET','POST'])
@login_required
def fse_grades():

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


    return render_template('fse/fse_grades.html', ansString=json.dumps(gradesDict))