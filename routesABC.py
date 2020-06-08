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
        '02' : U021U, 
        '03' : U031U, 
        '04' : U041U, 
        '05' : U051U, 
        '06' : U061U, 
        '07' : U071U, 
        '08' : U081U, 
        ##'09' : U091U, 
        ##'10' : U101U, 
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
        11 : ['Fiona', 'Jessica', 'Yui'],
              
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
            'topic' : None, 
            'question' : None, 
            'answer' : None, 
            'writer' : None 
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

    #make a list of team already set up 
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
            Ans02=str(json.dumps(snlDict))               
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
                projectDict[unitNumber]['Deadline'] = section['Deadline']                
                projectDict[unitNumber]['M1'] = section['M1']
                projectDict[unitNumber]['M2'] = section['M2']                
        except:
            #print('except', sDict[week]['Unit'])
            pass
            
    #pprint(projectDict)
        
    return projectDict  


def get_tests(unit, team):
    user = midtermGrades()

    #qna = json.loads(user.j1)
    #snl = json.loads(user.j2)    
    qna = json.loads(user.j3)
    snl = json.loads(user.j4)    

    qnaCount = 0
    for test in qna:
        #print ('CHECK', qna[test]['unit'], unit ,  qna[test]['team'], team)        
        if qna[test]['unit'] == str(unit) and qna[test]['team'] == str(team):
            qnaCount = 1
    snlCount = 0        
    for test in snl:
        if snl[test]['unit'] == str(unit) and snl[test]['team'] == str(team):
            snlCount = 1

    return { 'snlCount' : snlCount, 'qnaCount' : qnaCount }
    


@app.route ("/abc_list", methods=['GET','POST'])
@login_required
def abc_list():        
    srcDict = get_projects()       
    #pprint(srcDict)

    unitList = ['00', '01', '02', '03']
    abcDict = {}
    for src in srcDict:
        # check sources against open units in model
        # src == unit
        if src in unitList:
            pass
        elif Units.query.filter_by(unit=src).count() == 1:
            abcDict[src] = {                
                'Title' : srcDict[src]['Title'],
                'Team'  : 'Not set up yet',
                'Number' : 0,
                'QTotal' : 0,
                'STotal' : 0,
                'QTest' : 0,
                'STest' : 0,
            }

            projects = unitDict[src].query.all()
            for proj in projects:                 
                tests = get_tests(src, proj.teamnumber )
                if current_user.username in ast.literal_eval(proj.username):                    
                    abcDict[src]['Team'] = proj.username
                    abcDict[src]['Number'] = proj.teamnumber
                    abcDict[src]['QTotal'] = proj.Ans03
                    abcDict[src]['STotal'] = proj.Ans04  
                    abcDict[src]['QTest'] = tests['qnaCount']
                    abcDict[src]['STest'] = tests['snlCount']
                    #pass    
        
    #pprint (abcDict)       

    examDict = {} 
    '''
    for src in srcDict:
        if int(src) > 3:
            pass
        else:
            examDict[src] = {}
            try:
                teamCheck = int(abcDict[src]['Number'])
                selector = teamCheck % 2
                #print('selector', selector)
            except:
                selector = 0
            
            if Units.query.filter_by(unit=src).count() == 1:     
                projects = unitDict[src].query.all()
                
                for proj in projects:

                    if int(proj.teamnumber) > 20:
                        pass
                    elif abcDict[src]['Number'] == proj.teamnumber:
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
        
    return render_template('abc/abc_list.html', legend='ABC Projects', source=source, abcDict=json.dumps(abcDict),  examDict=json.dumps(examDict))


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
                'id' : user.studentID
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