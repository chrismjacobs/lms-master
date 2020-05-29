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
            if int(sDict[week]['Unit']) > 0:
                print('2') 
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
       

def get_grades(ass, unt):

    

    ### set max grades
    total_units = 0
    maxU = 0 
    maxA = 0 
    units = Units.query.all()
    for unit in units:
        total = unit.u1 + unit.u2 + unit.u3 + unit.u4
        maxU += total
        maxA += unit.uA
        total_units += 1
    maxU = maxU*2
    maxA = maxA*2  

    MTFN = 'FN'
    # set number for counting throught the lists of units and asses
    if MTFN == 'MT':
        unit_start = 0
        ass_start = 0
        unit_check = total_units*4
        ass_check = total_units
    elif MTFN == 'FN':
        unit_start = 16
        ass_start = 4
        unit_check = unit_start + total_units*4
        ass_check = ass_start + total_units


    unitGrade = 0 
    print ('1', unitGrade)
    unitGradRec = {}     
    print ('check units: ', unt, maxU)
    if unt == True:    
        for model in Info.unit_mods_list[unit_start:unit_check]: # a list of all units (so MT will be the first 4x4=16 units)
            rows = model.query.all()
            unit = str(model).split('U')[1]
            unitGradRec[unit] = {
                'Grade' : 0, 
                'Comment' : ''
            }
            
            for row in rows:                       
                names = ast.literal_eval(row.username)            
                if current_user.username in names:
                    unitGrade += row.Grade
                    unitGradRec[unit] = {
                        'Grade' : row.Grade, 
                        'Comment' : row.Comment
                        }
    assGrade = 0 
    assGradRec = {}   


    model_check = total_units
    if ass == True:  
        for model in Info.ass_mods_list[ass_start:ass_check]:        
            unit = str(model).split('A')[1]
            rec = model.query.filter_by(username=current_user.username).first()
            if rec:
                assGrade += rec.Grade
                assGradRec[unit] = {
                    'Grade' : rec.Grade, 
                    'Comment' : rec.Comment
                }
            else:
                assGradRec[unit] = {
                    'Grade' : 0, 
                    'Comment' : 'Not started yet'
                }
                        
    return {
        'unitGrade' : unitGrade, 
        'assGrade' : assGrade,
        'assGradRec' :  assGradRec,
        'unitGradRec' :  unitGradRec,
        'maxU' : maxU, 
        'maxA' : maxA
    }
 

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

    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/exam.json' )
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

    return render_template(html, legend='Exams', 
    Dict=json.dumps(examDict), title=unit, theme=theme)


@app.route ("/updateExam", methods=['POST', 'GET'])
@login_required
def updateExam(): 
    unit = request.form ['unit']
    test = request.form ['test']
    grade = request.form ['grade']    
    tries = request.form ['tries'] 
    print(unit, test, grade, tries)   
    
    user = Exams.query.filter_by(username=current_user.username).first()
    
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


@app.route ("/exam_list_midterm", methods=['GET','POST'])
@login_required
def exam_list_midterm(): 
    
    ''' set exam practice '''
    try: 
        user = Exams.query.filter_by(username=current_user.username).first()
        reviewData = json.loads(user.j1)
        examData = json.loads(user.j2) 
        print('exam_list_data_checked')
    except:
        reviewDict = {        
                '1-2' : [], 
                '3-4' : [], 
                '5-6' : [], 
                '7-8' : [] 
            }        
        entry = Exams(username=current_user.username, j1=json.dumps(reviewDict), j2=json.dumps(reviewDict))
        db.session.add(entry)
        db.session.commit()

        user = Exams.query.filter_by(username=current_user.username).first()   
        reviewData = json.loads(user.j1)        
        examData = json.loads(user.j2)   
    
    try:
        tries12 = round(   (reviewData['1-2'][0] + reviewData['1-2'][1])   /2  )
    except:
        tries12 = 0 
        reviewData['1-2'] = [0,0,0,]
    try:
        tries34 = round(   (reviewData['3-4'][0] + reviewData['3-4'][1])   /2  )
    except:
        tries34 = 0
        reviewData['3-4'] = [0,0,0,]

    ex12 = 0 
    ex34 = 0 
    if len(examData['1-2']) > 0: 
        ex12 = round(   (examData['1-2'][0] + examData['1-2'][1])   /2  )
    if len(examData['3-4']) > 0: 
        ex34 = round(   (examData['3-4'][0] + examData['3-4'][1])   /2  )
        
    
    
    examDict = {
        'total' : 0, 
        'units' : 0, 
        'asses' : 0, 
        'tries12' : str(tries12) + '/20% - tries: ' + str(reviewData['1-2'][2]), 
        'tries34' : str(tries34) + '/20% - tries: ' + str(reviewData['3-4'][2]),  
        'ex12' : ex12, 
        'ex34' : ex34, 
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

    if Units.query.filter_by(unit='02').first():
        setDict['12'] = Units.query.filter_by(unit='02').first().uA
    if Units.query.filter_by(unit='04').first():
        setDict['34'] = Units.query.filter_by(unit='04').first().uA
        
    context = {  
    'title' : 'Exams', 
    'theme' : DESIGN['titleColor'], 
    'examString' : json.dumps(examDict), 
    'setString' : json.dumps(setDict)   
    }    

    return render_template('units/exam_list_midterm.html', **context )


@app.route ("/exam_list_final", methods=['GET','POST'])
@login_required
def exam_list_final(): 
    
    ''' set exam practice '''
    try: 
        user = Exams.query.filter_by(username=current_user.username).first()
        reviewData = json.loads(user.j1)
        examData = json.loads(user.j2) 
        print('exam_list_data_checked')
    except:
        reviewDict = {        
                '1-2' : [], 
                '3-4' : [], 
                '5-6' : [], 
                '7-8' : [] 
            }        
        entry = Exams(username=current_user.username, j1=json.dumps(reviewDict), j2=json.dumps(reviewDict))
        db.session.add(entry)
        db.session.commit()

        user = Exams.query.filter_by(username=current_user.username).first()   
        reviewData = json.loads(user.j1)        
        examData = json.loads(user.j2)   
    
    try:
        tries56 = round(   (reviewData['5-6'][0] + reviewData['5-6'][1])   /2  )
    except:
        tries56 = 0 
        reviewData['5-6'] = [0,0,0,]
    try:
        tries78 = round(   (reviewData['7-8'][0] + reviewData['7-8'][1])   /2  )
    except:
        tries78 = 0
        reviewData['7-8'] = [0,0,0,]

    ex56 = 0 
    ex78 = 0 
    if len(examData['5-6']) > 0: 
        ex56 = round(   (examData['5-6'][0] + examData['5-6'][1])   /2  )
    if len(examData['7-8']) > 0: 
        ex78 = round(   (examData['7-8'][0] + examData['7-8'][1])   /2  )
        
    
    
    examDict = {
        'total' : 0, 
        'units' : 0, 
        'asses' : 0, 
        'tries56' : str(tries56) + '/20% - tries: ' + str(reviewData['5-6'][2]), 
        'tries78' : str(tries78) + '/20% - tries: ' + str(reviewData['7-8'][2]),  
        'ex56' : ex56, 
        'ex78' : ex78, 
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

    if Units.query.filter_by(unit='06').first():
        setDict['56'] = Units.query.filter_by(unit='06').first().uA
    if Units.query.filter_by(unit='08').first():
        setDict['78'] = Units.query.filter_by(unit='08').first().uA
        
    context = {  
    'title' : 'Exams', 
    'theme' : DESIGN['titleColor'], 
    'examString' : json.dumps(examDict), 
    'setString' : json.dumps(setDict)   
    }    

    return render_template('units/exam_list_final.html', **context )


@app.route ("/setStatus", methods=['POST'])
@login_required
def setStatus():
    username = request.form ['username']

    student = User.query.filter_by(username=username).first()
    if student.extra != 3:
        print('set')
        student.extra = 3         
        db.session.commit()
    else:
        print('reset')
        student.extra = 0 
        db.session.commit()

    return jsonify({'student' : username, 'set' : student.extra})


@app.route ("/grades_final", methods=['GET','POST'])
@login_required
def grades_final():

    gradesDict = {}

    users = User.query.all()    

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
            'tries2' : 0,
            'exam1' : 0,             
            'exam2' : 0   
        }

    ### set max grades
    total_units = 0
    maxU = 0 
    maxA = 0 
    units = Units.query.all()
    for unit in units:
        total = unit.u1 + unit.u2 + unit.u3 + unit.u4
        maxU += total*2
        maxA += unit.uA*2
        total_units += 1
         
    model_check = total_units*4 ## 4 units for each unit    

    for model in Info.unit_mods_list[16:(16 + model_check)]:
        rows = model.query.all()
        unit = str(model).split('U')[1]        
        for row in rows:                       
            names = ast.literal_eval(row.username)            
            for name in names:
                gradesDict[name]['units'] += row.Grade          
    
    model_check = total_units
    
    for model in Info.ass_mods_list[4:(4+ model_check)]:        
        unit = str(model).split('A')[1]
        rows = model.query.all()
        for row in rows:
            gradesDict[row.username]['asses'] += row.Grade
            
     
    practices = Exams.query.all()
    for practice in practices:
        reviewData = ast.literal_eval(practice.j1)
        if len(reviewData['5-6']) > 2:
            gradesDict[practice.username]['tries1'] = reviewData['5-6'][2]
        if len(reviewData['7-8']) > 2:
            gradesDict[practice.username]['tries2'] = reviewData['7-8'][2]        

        examData =  ast.literal_eval(practice.j2)
        if len(examData['5-6']) > 0 :
            gradesDict[practice.username]['exam1'] = round( (examData['5-6'][0] + examData['5-6'][1])/2 )
        if len(examData['7-8']) > 0 :
            gradesDict[practice.username]['exam2'] = round( (examData['7-8'][0] + examData['7-8'][1])/2 )


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
        gradesDict[entry]['Total'] = gradesDict[entry]['uP'] + gradesDict[entry]['aP'] + gradesDict[entry]['exam1'] + gradesDict[entry]['exam2'] 



    return render_template('instructor/grades.html', ansString=json.dumps(gradesDict))


@app.route ("/grades_midterm", methods=['GET','POST'])
@login_required
def grades_midterm ():

    gradesDict = {}

    users = User.query.all()    

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
            'tries2' : 0,
            'exam1' : 0,             
            'exam2' : 0   
        }

    ### set max grades

    total_units = 0
   

    midterm_unit_list = ['01', '02', '03', '04']
    maxU = 0 
    maxA = 0 
    units = Units.query.all()
    for un in units:
        if un.unit in midterm_unit_list:
            total = un.u1 + un.u2 + un.u3 + un.u4
            maxU += total*2
            maxA += un.uA*2
            total_units += 1
        elif un.unit == '05':
            ## we are now in final mode so ...
            total_unit = 4

    
         
    model_check = total_units*4 ## 4 units for each unit    

    for model in Info.unit_mods_list[0:model_check]:
        rows = model.query.all()
        unit = str(model).split('U')[1]        
        for row in rows:                       
            names = ast.literal_eval(row.username)            
            for name in names:
                gradesDict[name]['units'] += row.Grade          
    
    model_check = total_units
    
    for model in Info.ass_mods_list[0:model_check]:        
        unit = str(model).split('A')[1]
        rows = model.query.all()
        for row in rows:
            gradesDict[row.username]['asses'] += row.Grade
            
     
    practices = Exams.query.all()
    for practice in practices:
        reviewData = ast.literal_eval(practice.j1)
        if len(reviewData['1-2']) > 2:
            gradesDict[practice.username]['tries1'] = reviewData['1-2'][2]
        if len(reviewData['3-4']) > 2:
            gradesDict[practice.username]['tries2'] = reviewData['3-4'][2]        

        examData =  ast.literal_eval(practice.j2)
        if len(examData['1-2']) > 0 :
            gradesDict[practice.username]['exam1'] = round( (examData['1-2'][0] + examData['1-2'][1])/2 )
        if len(examData['3-4']) > 0 :
            gradesDict[practice.username]['exam2'] = round( (examData['3-4'][0] + examData['3-4'][1])/2 )


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
        gradesDict[entry]['Total'] = gradesDict[entry]['uP'] + gradesDict[entry]['aP'] + gradesDict[entry]['exam1'] + gradesDict[entry]['exam2'] 



    return render_template('instructor/grades.html', ansString=json.dumps(gradesDict))







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
    
    theme=DESIGN['titleColor']

    return render_template('units/assignment_list.html', legend='Assignments Dashboard', 
    Dict=json.dumps(assDict), Grade=assGrade, max=maxA, title='Assignments', theme=theme)




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


@app.route("/ass/<string:unit>", methods = ['GET', 'POST'])
@login_required
def ass(unit): 

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
            
    if count == 1: 
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

