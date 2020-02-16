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
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/vocab.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    VOCAB = json.loads(file_content)  # json loads returns a dictionary  
    SOURCES =  None        
    EXTRA =  None

    return VOCAB    

@app.route ("/unit_list", methods=['GET','POST'])
@login_required
def unit_list():    
    
    srcDict = get_sources()
    #print(srcDict)

    ''' deal with grades ''' 
    grades = get_grades(False, True) 
    print (grades)
    unitGrade = grades['unitGrade'] 
    recs = grades['unitGradRec']
    maxU = grades['maxU']

    print ('RECS', recs)

    todays_unit = Attendance.query.filter_by(username='Chris').first().unit
    try: 
        int(todays_unit)
        review = 0 
    except:
        review = 1 

    unitDict = {}
    for unit in recs:
        unit2c = unit[0:2] # 011 --> 01 
        part = unit[2]
        
        checkOpen = Units.query.filter_by(unit=unit2c).first()
        checkDict = {
            1 : checkOpen.u1, 
            2 : checkOpen.u2, 
            3 : checkOpen.u3, 
            4 : checkOpen.u4
        }    

        if review == 1:
            access = 1  ## go to review
        elif checkDict[int(part)] == 0:
            access = 0
        else:
            if todays_unit == unit2c:
                access = 2  ## button option for writer/reader
            else:
                access = 0  ## disbaled
        
        unitDict[ unit2c + '-' + part ] = { 
            'Unit' : unit2c, 
            'Part' : part,           
            'Deadline' : srcDict[unit2c]['Deadline'],
            'Title' : srcDict[unit2c]['Title'],
            'Grade' : recs[unit]['Grade'],
            'Comment' : recs[unit]['Comment'],
            'Source' : srcDict[unit2c]['Materials'][part],
            'Access' : access
        }    

    return render_template('units/unit_list.html', legend='Units Dashboard', 
    Dict=json.dumps(unitDict), Grade=unitGrade, max=maxU, title='Units')


@app.route('/openUnit', methods=['POST'])
def openUnit():

    key = request.form ['key']
    print('KEYYYYYYYY', key)    

    unit2c = key[0:2] # 01-1 --> 01 
    part = int(key[3])

    checkOpen = Units.query.filter_by(unit=unit2c).first() 

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

    dataDict = {}

    ## just get team data
    if int(check) == 0: 
        find = model.query.filter_by(teamnumber=teamnumber).count()
        if find == 0:
            dataDict = {}
        else:
            entry = model.query.filter_by(teamnumber=teamnumber).first()
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
        classData = model.query.all() 
        for entry in classData:
            dataDict[1][entry.teamnumber] = entry.Ans01 
            dataDict[2][entry.teamnumber] = entry.Ans02 
            dataDict[3][entry.teamnumber] = entry.Ans03 
            dataDict[4][entry.teamnumber] = entry.Ans01 
            dataDict[5][entry.teamnumber] = entry.Ans05 
            dataDict[6][entry.teamnumber] = entry.Ans06 
            dataDict[7][entry.teamnumber] = entry.Ans07 
            dataDict[8][entry.teamnumber] = entry.Ans08 
            dataDict[7][entry.teamnumber] = entry.Ans07  

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
        entry = model(username=str(nameRange), teamnumber=teamnumber, Ans01=answer, Grade=0, Comment='in progress..')
        db.session.add(entry)
        db.session.commit()
        return jsonify({'answer' : 'participation started', 'action' : 1})
    
    
    if find == 1:       
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
            if int(question) == 2:                    
                entry.Ans02 = answer                    
            if int(question) == 3:
                entry.Ans03 = answer
            if int(question) == 4:
                entry.Ans04 = answer
            if int(question) == 5:
                entry.Ans05 = answer
            if int(question) == 6:
                entry.Ans06 = answer
            if int(question) == 7:
                entry.Ans07 = answer
            if int(question) == 8:
                entry.Ans08 = answer                

            entry.username = str(nameRange)                
            print('commit???', question, answer)
            db.session.commit()   
            ## check if last answer given
            if int(question) == int(qs):                
                if entry.Grade > 0 :
                    pass            
                elif  datetime.now() < deadline:
                    comList = ['Nice work', 'Done', 'Complete', 'Great', 'Finshed'] 
                    entry.Grade = 2  # completed on time
                    entry.Comment = random.choice(comList) 
                    db.session.commit()    
                else: 
                    comList = ['Late', 'Be careful of deadlines', 'Earlier is better', 'Try to be on time', 'Avoid last minute work'] 
                    entry.Grade = 1  # late start  
                    entry.Comment = random.choice(comList) 
                    db.session.commit()
                return jsonify({'answer' : 'participation completed', 'action' : 1})
            else:
                return jsonify({'answer' : 'answer shared - keep going', 'action' : None})     

    return jsonify({'answer' : 'something wrong has happened'})


@app.route ("/participation/<string:unit_num>/<string:part_num>/<string:state>", methods=['GET','POST'])
@login_required
def participation(unit_num,part_num,state):

    teamcount = Attendance.query.filter_by(username='Chris').first().teamcount
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
            flash('This unit is not open at the moment', 'danger')
            return redirect(url_for('unit_list'))
        if unitChecker[part_num] == 0:
            flash('This activity is not open at the moment', 'danger')
            return redirect(url_for('unit_list'))  
        if unit_num != Attendance.query.filter_by(username='Chris').first().unit:
            print (unit, Attendance.query.filter_by(username='Chris').first().unit)
            flash('This task is not open at the moment', 'danger')
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
    }

    return render_template('units/part_vue.html', **context)

