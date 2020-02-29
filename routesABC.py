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
s3_client = BaseConfig.s3_client
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN


unitDict = {
        '00' : U001U, 
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


@app.route ("/abc/make_teams/<string:unit>/<string:number>/", methods=['GET','POST'])
@login_required
def project_teams(unit, number):
    if current_user.id != 1:
        return abort(403)
    
    project = unitDict[unit]
    print (project.query.all())

    #create a dictionary of teams
    attTeams = Attendance.query.all()
    teamsDict = {}
    for att in attTeams:
        if att.teamnumber in teamsDict:
            teamsDict[att.teamnumber].append(att.username)
        else: 
            teamsDict[att.teamnumber] = [att.username]    
    
    manualTeams = {
        20: ['Chris', 'Test', 'Victor', 'Winnie'],        
    }

    '''control which teams are added'''
    controller = 2
   
    if controller == 1:
        team_dict = attTeams
    elif controller == 2:
        team_dict = manualTeams
    
    # prepare answers for QNA
    qnaDict = {}
    for i in range (1, 7):
        qnaDict[i] = {
            'topic' : None, 
            'question' : None, 
            'answer' : None, 
            'writer' : None 
        }
    
    snlDict = {}           

    #make a list of team already set up 
    teams = []
    for pro in project.query.all():
        teams.append(pro.teamnumber) 
    

    returnStr = str(team_dict)
    for team in team_dict:
        if team in teams:
            returnStr = 'Error - check table' 
            break    
        create_folder(unit, str(team), team_dict[team])
        teamStart = project(
            teamnumber=int(team), 
            username=str(team_dict[team]),
            Ans01=str(json.dumps(qnaDict)),
            Ans02=str(json.dumps(snlDict))               
            )        
        db.session.add(teamStart)
        db.session.commit()  

    return returnStr 


def get_projects():    
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    sDict = json.loads(file_content)  # json loads returns a dictionary 
    unitDict = {}  
    for week in sDict:
        try:      
            if int(sDict[week]['Unit']) >= 0:
                print('2') 
                unitNumber = sDict[week]['Unit']
                unitDict[unitNumber] = {}
                section = sDict[week]
                #unitDict[unitNumber] = sDict[week]  

                unitDict[unitNumber]['Title'] = section['Title']
                unitDict[unitNumber]['Date'] = section['Date']
                unitDict[unitNumber]['Deadline'] = section['Deadline']                
                unitDict[unitNumber]['M1'] = section['M1']
                unitDict[unitNumber]['M2'] = section['M2']                
        except:
            print('except', sDict[week]['Unit'])
            pass
            
    pprint(unitDict)
        
    return unitDict   

@app.route ("/abc_list", methods=['GET','POST'])
@login_required
def abc_list():        
    srcDict = get_projects()       
    pprint(srcDict)
    abcDict = { }
    for src in srcDict:
        if Units.query.filter_by(unit=src).count() == 1:
            abcDict[src] = {                
                'Title' : srcDict[src]['Title'],
                'Team'  : 'Not set up yet',
                'Number' : 0,
                'QTotal' : 0,
                'STotal' : 0
            }

            projects = unitDict[src].query.all()
            for proj in projects:                
                if current_user.username in ast.literal_eval(proj.username):                    
                    abcDict[src]['Team'] = proj.username
                    abcDict[src]['Number'] = proj.teamnumber
                    abcDict[src]['QTotal'] = proj.Ans03
                    abcDict[src]['STotal'] = proj.Ans04  
                    pass     
        
    pprint (abcDict)        
       
    source = srcDict['00']['M2']
        
    return render_template('abc/abc_list.html', legend='ABC Projects', source=source, abcDict=json.dumps(abcDict))



@app.route('/storeQNA', methods=['POST'])
def storeQNA():  
    unit = request.form ['unit']  
    team = request.form ['team']      
    question = request.form ['question']      
    ansOBJ = request.form ['ansOBJ']  
    total = request.form ['total']  

    project = unitDict[unit]           
    project_answers = project.query.filter_by(teamnumber=team).first()    
    project_answers.Ans01 = ansOBJ    
    project_answers.Ans03 = total  #12 will be the maximum 
    db.session.commit()   
    
    return jsonify({'question' : question})



@app.route('/updateAnswers', methods=['POST'])
def updateAnswers():  
    unit = request.form ['unit']  
    team = request.form ['team'] 

    project = unitDict[unit]           
    project_answers = project.query.filter_by(teamnumber=team).first()    
       
    
    return jsonify({'ansString' : str(project_answers.Ans01)})



def setUpProject(unit, team):
    srcDict = get_projects()
    meta = srcDict[unit]

    project = unitDict[unit]    
    questions = project.query.filter_by(teamnumber=team).first()   
    teamMembers = ast.literal_eval(questions.username)

    if current_user.username not in teamMembers:
        return abort(403)  
    
    teamDict = {}
    for member in teamMembers:
        try:   
            teamDict[member] = S3_LOCATION + User.query.filter_by(username=member).first().image_file
        except:
            teamDict[member] = None
    
    project_answers = unitDict[unit].query.filter_by(teamnumber=team).first()

    return {
        'project_answers' : project_answers, 
        'meta' : meta, 
        'teamMembers' : json.dumps(teamDict)
    }



@app.route ("/abc/qna/<string:unit>/<int:team>", methods=['GET','POST'])
@login_required
def abc_qna(unit, team): 

    data = setUpProject(unit, team)  
    project_answers = data['project_answers'] 
    meta = data['meta'] 
    teamMembers = data['teamMembers'] 
    
    ansDict = project_answers.Ans01

    testDict = {}
    for i in range (1, 7):
        testDict[i] = {
            'topic' : None, 
            'question' : None, 
            'answer' : None, 
            'writer' : None 
        }    
    
    
    return render_template('abc/abc_qna.html', legend='Questions & Answers', 
    meta=meta, 
    teamMembers=teamMembers,
    ansDict=ansDict,
    testDict=str(json.dumps(testDict))
    )


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

@app.route('/deleteWord', methods=['POST'])
def deleteWord():
    word = request.form ['word'] 
    unit = request.form ['unit']  
    team = request.form ['team'] 

    project = unitDict[unit].query.filter_by(teamnumber=team).first()   
    
    ansDict = ast.literal_eval(project.Ans02)

    try:
        ansDict.pop(word)
        ansString = json.dumps(ansDict)
        project.Ans02 = ansString 
        project.Ans04 = len(ansDict)
        db.session.commit()
    except:
        pass        

    qCount = len(ansDict)
    print('qCount', qCount)
    
    return jsonify({'word' : word, 'newDict' : json.dumps(ansDict), 'qCount' : qCount })



@app.route ("/abc/snl/<string:unit>/<int:team>", methods=['GET','POST'])
@login_required
def abc_snl(unit, team): 
    data = setUpProject(unit, team)  
    project_answers = data['project_answers'] 
    meta = data['meta'] 
    teamMembers = data['teamMembers'] 
    
    ansDict = project_answers.Ans02

    
    
    return render_template('abc/abc_snl.html', legend='Questions & Answers', 
    meta=meta, 
    teamMembers=teamMembers,
    ansDict=ansDict, 
    testDict=None
    )






