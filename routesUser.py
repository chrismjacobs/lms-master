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

    unitGrade = 0 
    print ('1', unitGrade)
    unitGradRec = {}     
    model_check = total_units*4 ## 4 units for each unit
    print ('check units: ', unt, maxU)
    if unt == True:    
        for model in Info.unit_mods_list[0:model_check]:
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
        for model in Info.ass_mods_list[0:model_check]:        
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


@app.route ("/grades", methods = ['GET', 'POST'])
@login_required
def grades():
       
    ''' deal with grades ''' 
    if SCHEMA < 3:
        grades = get_grades(True, True) 
    else:
        grades = {'unitGrade': None, 'assGrade': None,'maxA':None, 'maxU':None  }    

    
    context = {    
    'unitGrade' : grades['unitGrade'], 
    'assGrade' :  grades['assGrade'], 
    'maxA' : grades['maxA'],
    'maxU' : grades['maxU'], 
    'title' : 'Grades'    
    } 

    return render_template('admin/grades.html', **context )
  

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
   
    ''' deal with grades ''' 
    if SCHEMA < 3:
        grades = get_grades(True, True) 
    else:
        grades = {'unitGrade': None, 'assGrade': None,'maxA':None, 'maxU':None  }    

    ''' deal with attendance '''          
    attLog = AttendLog.query.filter_by(username=current_user.username).all()   
         
    context = {
    'form' : form, 
    'dialogues' : dialogues,     
    'image_chris' : image_chris, 
    'image_file' : image_file, 
    'chat' : chat,
    'attLog' : attLog,
    'unitGrade' : grades['unitGrade'], 
    'assGrade' :  grades['assGrade'], 
    'maxA' : grades['maxA'],
    'maxU' : grades['maxU'], 
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
        html = 'units/exam_form.html'        
    
    theme=DESIGN['titleColor']

    return render_template(html, legend='Exams', 
    Dict=json.dumps(examDict), title=unit, theme=theme)


@app.route ("/updateExam", methods=['POST', 'GET'])
@login_required
def updateExam(): 
    unit = request.form ['unit']
    test = request.form ['test']
    grade = request.form ['grade']    
    
    user = Exams.query.filter_by(username=current_user.username).first()

    if test == 'review':
        record = json.loads(user.j1)
        record[unit].append(grade)
        tries = len(record[unit])
        user.j1 = json.dumps(record)
        db.session.commit()

    if test == 'exam':
        tries = None
        record = json.loads(user.j2)
        record[unit].append(grade)
        user.j1 = json.dumps(record)
        db.session.commit()

    return jsonify({'unit' : unit, 'tries' : tries})


@app.route ("/exam_list", methods=['GET','POST'])
@login_required
def exam_list(): 

    try: 
        user = Exams.query.filter_by(username=current_user.username).first()
        reviewData = user.j1
        examData = user.j2
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
        reviewData = user.j1
        examData = user.j2    
    
    theme=DESIGN['titleColor']

    return render_template('units/exam_list.html', title='Exams', theme=theme, reviewData=reviewData, examData=examData)






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

