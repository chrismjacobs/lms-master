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

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN

def get_vocab():
    ## change to 'json_files/vocab.json' for semester 1
    if Units.query.filter_by(unit='00').first() or Units.query.filter_by(unit='01').first():
        vocabJSON = 'json_files/vocab.json'
    else:
        vocabJSON = 'json_files/vocab2.json'
    content_object = s3_resource.Object( S3_BUCKET_NAME, vocabJSON )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    VOCAB = json.loads(file_content)  # json loads returns a dictionary
    SOURCES =  None
    EXTRA =  None

    return VOCAB

@app.route ("/teamwork_list", methods=['GET','POST'])
@login_required
def teamwork_list():
    return False


@app.route ("/unit_list", methods=['GET','POST'])
@login_required
def unit_list():

    srcDict = get_sources()
    print('SRCDICT', srcDict)

    ''' deal with grades '''
    grades = get_grades(False, True)
    print ('GRADES', grades)
    unitGrade = grades['unitGrade']
    recs = grades['unitGradRec']
    maxU = grades['maxU']

    print ('RECS', recs)

    todays_unit = Attendance.query.filter_by(username='Chris').first().unit
    try:
        int(todays_unit)
        review = 0
        print('TRY')
    except:
        review = 1
        print('EXCEPT')

    unitDict = {}

    for us in Units.query.all():
        print('US', us)
        unitDict[us.unit] = {}

    for unit in recs:
        print('UNIT', unit)
        unit2c = unit[0:2] # string 011 --> 01
        print('UNIT2', unit2c)
        part = unit[2]

        checkOpen = Units.query.filter_by(unit=unit2c).first()
        checkDict = {
            1 : checkOpen.u1,
            2 : checkOpen.u2,
            3 : checkOpen.u3,
            4 : checkOpen.u4
        }

        if checkDict[int(part)] == 0:
            access = 0
        elif review == 1:
            access = 1  ## mean attedance not started so open for access
        else:
            if todays_unit == unit2c:
                access = 2  ## button option for writer/reader
            else:
                access = 0  ## disbaled

        unitDict[unit2c][ unit2c + '-' + part ] = {
            'Unit' : unit2c,
            'Part' : part,
            'Deadline' : srcDict[unit2c]['Deadline'],
            'Title' : srcDict[unit2c]['Title'],
            'Grade' : recs[unit]['Grade'],
            'Comment' : recs[unit]['Comment'],
            'Source' : srcDict[unit2c]['Materials'][part],
            'Access' : access
        }

    student_attendance = Attendance.query.filter_by(username=current_user.username).count()

    return render_template('units/unit_list.html', legend='Units Dashboard',
    Dict=json.dumps(unitDict), Grade=unitGrade, max=maxU, title='Units', todays_unit=todays_unit, student_attendance=student_attendance)


@app.route('/recError', methods=['POST'])
def recError():

    message = request.form ['message']
    mode = request.form ['mode']
    unit = request.form ['unit']


    error = Errors(username=current_user.username, device=current_user.device, mode=mode, unit=unit, err=message)
    db.session.add(error)
    db.session.commit()

    return jsonify({'message' : message })

@app.route('/openUnit', methods=['POST'])
def openUnit():

    key = request.form ['key']
    number = request.form ['number']
    print('KEY', key)

     # 01-1 --> 01
    part = int(key[3])


    checkOpen = Units.query.filter_by(unit=number).first()

    if checkOpen:
        if part == 0:
            Units.query.filter_by(unit=number).delete()
        if part == 1:
            checkOpen.u1 = 1
        if part == 2:
            checkOpen.u2 = 1
        if part == 3:
            checkOpen.u3 = 1
        if part == 4:
            checkOpen.u4 = 1
            checkOpen.uA = 1
        db.session.commit()
    else:
        newUnit = Units(unit=number, u1=0, u2=0, u3=0, u4=0, uA=0)
        db.session.add(newUnit)
        db.session.commit()

    return jsonify({'key' : key })



def team_details ():
    # check user has a team number
    try:
        teamnumber = Attendance.query.filter_by(username=current_user.username).first().teamnumber
        if teamnumber == 0:
            nameRange = [current_user.username]
        else:
        # confirm names of team
            names = Attendance.query.filter_by(teamnumber=teamnumber).all()
            nameRange = [student.username for student in names]
        #for student in names:
            #nameRange.append(student.username)
        print ('NAMES', nameRange)
    except:
        # create a unique teamnumber for solo users
        teamnumber = current_user.id + 100
        nameRange = [current_user.username]
        print ('Teamnumber: ', teamnumber)



    nnDict = {
            'teamnumber' : teamnumber,
            'nameRange' : nameRange
            }
    return nnDict

# check the score of teams during participation for the games panel
@app.route('/partCheck', methods=['POST'])
def scoreCheck():
    qNum = request.form ['qNum']
    part_num = request.form ['part_num']
    unit_num = request.form ['unit_num']

    print (type(qNum), part_num, unit_num)

    modDict = Info.unit_mods_dict
    model = modDict[unit_num][int(part_num)]
    answers = model.query.order_by(asc(model.teamnumber)).all()

    scoreDict = {}
    for answer in answers:
        print (answer)
        scoreList = [answer.Ans01, answer.Ans02, answer.Ans03, answer.Ans04,
        answer.Ans05, answer.Ans06, answer.Ans07, answer.Ans08]
        if answer.teamnumber <21:
            scoreDict[answer.teamnumber] = []
            for item in scoreList[0:int(qNum)+1]:
                if item != "" and item != None:
                    scoreDict[answer.teamnumber].append(1)
    print (scoreDict)

    maxScore = len(scoreDict) * int(qNum)
    actScore = 0
    for key in scoreDict:
        for item in scoreDict[key]:
            actScore += item
    print ('max', maxScore, 'act', actScore)

    percentFloat = (actScore / maxScore )*100
    percent = round (percentFloat, 1)

    return jsonify({'percent' : percent, 'scoreDict' : scoreDict, 'qNum' : qNum })


@app.route('/getPdata', methods=['POST'])
def getPdata():

    nnDict = team_details ()
    teamnumber = nnDict['teamnumber']
    nameRange = nnDict['nameRange']

    unit = request.form ['unit']
    part = request.form ['part']
    check = request.form ['check']

    # get model
    models = Info.unit_mods_dict[unit] # '01' : [None, mod, mod, mod, mod]
    model = models[int(part)]
    classData = model.query.all()

    dataDict = {}

    ## just get team data
    if int(check) == 0:
        for entry in classData:
            if current_user.username in ast.literal_eval(entry.username):
                dataDict = {
                1 : entry.Ans01,
                2 : entry.Ans02,
                3 : entry.Ans03,
                4 : entry.Ans04,
                5 : entry.Ans05,
                6 : entry.Ans06,
                7 : entry.Ans07,
                8 : entry.Ans08,
                }
                break


    ## just get data for whole class
    if int(check) == 1:
        dataDict = {
            1 : {},
            2 : {},
            3 : {},
            4 : {},
            5 : {},
            6 : {},
            7 : {},
            8 : {},
        }
        for entry in classData:
            dataDict[1][entry.teamnumber] = entry.Ans01
            dataDict[2][entry.teamnumber] = entry.Ans02
            dataDict[3][entry.teamnumber] = entry.Ans03
            dataDict[4][entry.teamnumber] = entry.Ans04
            dataDict[5][entry.teamnumber] = entry.Ans05
            dataDict[6][entry.teamnumber] = entry.Ans06
            dataDict[7][entry.teamnumber] = entry.Ans07
            dataDict[8][entry.teamnumber] = entry.Ans08

    return jsonify({'dataDict' : json.dumps(dataDict)})


@app.route('/shareUpload', methods=['POST'])
def shareUpload():

    nnDict = team_details ()
    teamnumber = nnDict['teamnumber']
    nameRange = nnDict['nameRange']

    unit = request.form ['unit']
    part = request.form ['part']
    answer = request.form ['answer']
    question = request.form ['question']
    qs = request.form ['qs']

    srcDict = get_sources()
    date = srcDict[unit]['Date']
    dt = srcDict[unit]['Deadline']
    deadline = datetime.strptime(dt, '%Y-%m-%d') + timedelta(days=1)
    print ('deadline: ', deadline)

    # get model
    models = Info.unit_mods_dict[unit] # '01' : [None, mod, mod, mod, mod]
    model = models[int(part)]
    print(model)

    find = model.query.filter_by(teamnumber=teamnumber).count()
    if find == 0:
        if int(question) == 0: ## team start
            contribution = {'status': 'in progress...'}
            entry = model(username=str(nameRange), teamnumber=teamnumber, Grade=0, Comment=json.dumps(contribution))
        else: ## writer start
            if int(qs) == 1:
                print('Only one question..')
                entry = model(username=str(nameRange), teamnumber=teamnumber, Grade=2, Comment='Done', Ans01=answer)
            else:
                entry = model(username=str(nameRange), teamnumber=teamnumber, Grade=0, Ans01=answer, Comment='in progress....')

        db.session.add(entry)
        db.session.commit()
        return jsonify({'answer' : 'participation started', 'action' : 1})


    if find == 1:
        if int(question) == 0:
            return jsonify({'answer' : 'participation started', 'action' : None})

        entry = model.query.filter_by(teamnumber=teamnumber).first()
        qDict = {
            1 : entry.Ans01,
            2 : entry.Ans02,
            3 : entry.Ans03,
            4 : entry.Ans04,
            5 : entry.Ans05,
            6 : entry.Ans06,
            7 : entry.Ans07,
            8 : entry.Ans08,
        }
        if qDict[int(question)] != None:
            return jsonify({'answer' : 'Sorry, an answer has already been shared in your team', 'action' : 1})
        else:
            if int(question) == 1:
                entry.Ans01 = answer
                qDict[1] = answer
            if int(question) == 2:
                entry.Ans02 = answer
                qDict[2] = answer
            if int(question) == 3:
                entry.Ans03 = answer
                qDict[3] = answer
            if int(question) == 4:
                entry.Ans04 = answer
                qDict[4] = answer
            if int(question) == 5:
                entry.Ans05 = answer
                qDict[5] = answer
            if int(question) == 6:
                entry.Ans06 = answer
                qDict[6] = answer
            if int(question) == 7:
                entry.Ans07 = answer
                qDict[7] = answer
            if int(question) == 8:
                entry.Ans08 = answer
                qDict[8] = answer


            contribution = None

            if int(teamnumber) < 30:
                contribution = json.loads(entry.Comment)

                if current_user.username in contribution:
                    contribution[current_user.username] += '/' + question
                else:
                    contribution[current_user.username] = question

                entry.Comment = json.dumps(contribution)

            ## DO NOT ALLOW update of usernames
            ##entry.username = str(nameRange)
            print('commit???', question, answer, contribution)
            db.session.commit()
            ## check if last answer given

            qMarker = True
            for qAns in qDict:
                if int(qAns) <= int(qs) and qDict[qAns] == None:
                    qMarker = False

            if qMarker:
                if entry.Grade > 0 :
                    pass
                elif datetime.now() < deadline and int(teamnumber) < 30:
                    contribution = json.loads(entry.Comment)
                    comList = ['Done', 'Complete', 'Finshed', 'Ready']
                    entry.Grade = 2  # completed on time
                    contribution['status'] = random.choice(comList)
                    entry.Comment = json.dumps(contribution)
                    db.session.commit()
                elif datetime.now() < deadline:
                    comList = ['Done', 'Complete', 'Finshed', 'Ready']
                    entry.Grade = 2  # completed on time
                    entry.Comment = random.choice(comList)
                    db.session.commit()
                else:
                    comList = ['Late', 'Be careful of deadlines', 'Earlier is better', 'Try to be on time', 'Avoid last minute work']
                    entry.Grade = 1  # late start
                    entry.Comment = random.choice(comList)
                    db.session.commit()
                return jsonify({'answer' : 'participation completed', 'action' : 2})
            else:
                return jsonify({'answer' : 'answer shared - keep going', 'action' : None})

    return jsonify({'answer' : 'something wrong has happened - see your instructor'})


@app.route ("/participation/<string:unit_num>/<string:part_num>/<string:state>", methods=['GET','POST'])
@login_required
def participation(unit_num,part_num,state):

    chris_attend = Attendance.query.filter_by(username='Chris').first()
    teamcount = chris_attend.teamcount
    print('teamcount', teamcount)
    #check source to see if unit is open yet
    unit_count = Units.query.filter_by(unit=unit_num).count()

    # block
    if current_user.id != 1 :
        if unit_count == 1:
            unit_check = Units.query.filter_by(unit=unit_num).first()
            unitChecker = {
                '1' : unit_check.u1,
                '2' : unit_check.u2,
                '3' : unit_check.u3,
                '4' : unit_check.u4,
            }
        else:
            flash('This unit is not open at the moment(1)', 'danger')
            return redirect(url_for('unit_list'))

        if unitChecker[part_num] == 0:
            flash('This activity is not open at the moment(2)', 'danger')
            return redirect(url_for('unit_list'))
        if chris_attend.teamnumber != 97:
            todays_unit = Attendance.query.filter_by(username='Chris').first().unit
            if todays_unit  == 'RR':
                pass
            elif unit_num != todays_unit:
                print (unit, Attendance.query.filter_by(username='Chris').first().unit)
                flash('This task is not open at the moment(3)', 'danger')
                return redirect(url_for('unit_list'))

    # get sources
    srcDict = get_sources()
    source = srcDict[unit_num]['Materials'][part_num]
    print(srcDict[unit_num]['Materials'])

    #vocab
    vDict = get_vocab()
    #questions
    qDict = vDict[unit_num][part_num]
    qs = len(qDict)

    ## Get names
    models = Info.unit_mods_dict[unit_num] # '01' : [None, mod, mod, mod, mod]
    model = models[int(part_num)]
    print(model)
    nnDict = team_details()
    teamnumber = nnDict['teamnumber']
    find = model.query.filter_by(teamnumber=teamnumber).first()
    if find:
        teamnames = json.dumps(ast.literal_eval(find.username))
        print(teamnames, 1)
    else:
        teamnames = json.dumps(team_details()['nameRange'])
        print(teamnames, 2)

    context = {
        'title' : 'participation',
        'source' : source,
        'unit_num': unit_num,
        'part_num': part_num,
        'qDict' : json.dumps(qDict),
        'qs': qs,
        'DESIGN' : DESIGN,
        'state' : state,
        'userID' : current_user.id,
        'teamcount' : teamcount,
        'teamnames' : teamnames
    }

    return render_template('units/part_vue.html', **context)


@app.route ("/participationTest", methods=['GET','POST'])
def participationTest():
    fileName = '0ICC_part'

    if SCHEMA == 1:
        fileName = '0FRD_part'
    if SCHEMA == 2:
        fileName = '0WPE_part'


    with open(fileName + '.json', 'r') as json_file:
        dataDict = json.load(json_file)

    context = {
        'title' : 'participationTest',
        'dataDict': json.dumps(dataDict),
        'qDict' : json.dumps(get_vocab()),
        'DESIGN' : DESIGN
    }
    return render_template('units/part_vue_test.html', **context)




@app.route('/studentRemove', methods=['POST'])
def studentRemove():
    if current_user.id != 1:
        return abort(403)

    name = request.form ['name']
    part = request.form ['part']
    instructor_setup = Attendance.query.filter_by(studentID='100000000').first()
    student_setup = Attendance.query.filter_by(username=name).first()
    UNIT = instructor_setup.unit
    TEAM = student_setup.teamnumber

    part_model = Info.unit_mods_dict[UNIT][int(part)]

    print( Info.unit_mods_dict)
    print('model', part_model)

    if part_model:
        entry = part_model.query.filter_by(teamnumber=TEAM).first()
        team_list = ast.literal_eval(entry.username)
        print('TEAM', team_list)
        team_list.remove(name)
        print('TEAM', team_list)
        entry.username = str(team_list)
        db.session.commit()
    else:
        attend_log_id = student_setup.unit
        Attendance.query.filter_by(username=name).delete()
        AttendLog.query.filter_by(id=attend_log_id).delete()
        db.session.commit()

    return jsonify({'removed' : name, 'unit' : UNIT})
