import sys, boto3, random, base64, os, time, datetime, ast
from sqlalchemy import asc, desc, or_
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import * 
from models import *
from flask_mail import Message
import ast # eval literal for list str
try:
    from aws import Settings    
    s3_resource = Settings.s3_resource  
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME
    COLOR_SCHEMA = Settings.COLOR_SCHEMA   
except:
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME'] 
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 


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

    form = Chat()    
    if current_user.is_authenticated:
        name = current_user.username 
        dialogues = ChatBox.query.filter_by(username=current_user.username).all()
        length = len(dialogues)-1
        if length >= 0:
            chat = dialogues[length]
        else:
            chat = 0  
        if form.validate_on_submit():
                chat = ChatBox(username = current_user.username, 
                chat=form.chat.data, response=form.response.data)      
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

        fieldsGrade = Grades.query.filter_by(username=current_user.username).first() 
        attLog = AttendLog.query.filter_by(username=current_user.username).all()
        # Update attendance score     
        scoreCounter = 0 
        for score in attLog:            
            scoreCounter += score.attScore
        if fieldsGrade.attend == scoreCounter:
            pass
        else: 
            fieldsGrade.attend = scoreCounter
            db.session.commit()

        # set up color chart
        maxUni = Grades.query.order_by(desc(Grades.units)).first().units
        maxAss = Grades.query.order_by(desc(Grades.assignments)).first().assignments
        maxAtt = Grades.query.order_by(desc(Grades.attend)).first().attend
    
        #set up colors/scoring
        colorDict = {
            'color1' :  [0, fieldsGrade.attend, maxAtt],
            'color2' :  [0, fieldsGrade.units, maxUni],
            'color3' :  [0, fieldsGrade.assignments, maxAss]
        }
        for key in colorDict:
            try:
                colorDict[key][0] = colorDict[key][1] / colorDict[key][2]
            except:
                pass
        

        #practiceDict = ast.literal_eval(fieldsGrade.practice)
        #tries = len(practiceDict[1]) + len(practiceDict[2])
        #if tries != fieldsGrade.tries:
            #fieldsGrade.tries = tries
            #db.session.commit()
        
        

        context = {
        'form' : form, 
        'dialogues' : dialogues, 
        'name' :name, 
        'image_chris' : image_chris, 
        'image_file' :image_file, 
        'chat' : chat, 
        'fieldsGrade' : fieldsGrade,
        'color1' : colorDict['color1'][0], 
        'color2' : colorDict['color2'][0],
        'color3' : colorDict['color3'][0],          
        'attLog' : attLog,
        
        }
    else:
        context = {
        'form' : None, 
        'dialogues' : None, 
        'name' :None, 
        'image_chris' : None, 
        'image_file' :None, 
        'chat' : None , 
        'fieldsGrade' : None,
        'color1' : 0, 
        'color2' : 0,
        'color3' : 0,          
        'attLog' : None,
        
        }
    

    return render_template('user/home.html', **context )
   
######## Attendance //////////////////////////////////////////////
@app.route("/attend_team", methods = ['GET', 'POST'])
@login_required
def att_team():

    legend = 'Attendance: ' + time.strftime('%A %b, %d %Y %H:%M')

    # check if attendance is open 
    openData = Attendance.query.filter_by(username='Chris').first()
    if openData:
        openCheck = openData.teamnumber
        if openCheck == 98 or openCheck == 50:  # 98 open in normal state, 50 open in midterm state - all units can be done
            form = Attend()  
        elif openCheck == 99:  # switch to late form
            form = AttendLate() 
        elif openCheck == 100:   # delete all rows
            db.session.query(Attendance).delete()
            db.session.commit()
            attendance = Attendance(username = 'Chris', 
            attend='Notice', teamnumber=97, studentID='100000000')      
            db.session.add(attendance)
            db.session.commit()
            flash('Attendance is not open yet, please try later', 'danger')
            return redirect(url_for('home')) 
        else: # openData has return None
            flash('Attendance is not open yet, please try later', 'danger')
            return redirect(url_for('home'))  
    else:
        flash('Attendance is not open yet, please try later', 'danger')
        return redirect(url_for('home'))  

        
    # set up page data 
    teamcount = openData.teamcount
    teamsize = openData.teamsize 
    print('teamsizexxxxxxxx', teamsize) 
    notice = openData.attend     

    # set up student data   
    count = Attendance.query.filter_by(username=current_user.username).count()
    fields = Attendance.query.filter_by(username=current_user.username).first()     
    
    # set teamnumber to be zero by default (or not Zero in the case of solo classes)
    if teamsize == 0:
        teamNumSet = current_user.id + 100
    else:
        teamNumSet = 0 

    # set up team info 
    users = {}
    if count == 1: 
        teammates = Attendance.query.filter_by(teamnumber=fields.teamnumber).all()        
        for teammate in teammates:            
            image = User.query.filter_by(username=teammate.username).first().image_file
            users[teammate.username] = [teammate.username, S3_LOCATION + image]
    else:        
        users = None     

    # prepare initial form
    if count == 0:               
        if form.validate_on_submit():            
            # check last id for AttendLog 
            lastID = AttendLog.query.order_by(desc(AttendLog.id)).first().id   
            # team maker
            attendance = Attendance(username = form.name.data, 
            attend=form.attend.data, teamnumber=form.teamnumber.data, 
            teamcount=form.teamcount.data, studentID=form.studentID.data, unit=lastID+1)      
            db.session.add(attendance)
            db.session.commit()
            # long term log 
            if form.attend.data == 'On time':
                attScore = 3
            elif form.attend.data == 'Late': 
                attScore = 2
            else:
                attScore = 1          
            attendLog = AttendLog(username = form.name.data, 
            attend=form.attend.data,teamnumber=form.teamnumber.data, 
            studentID=form.studentID.data, attScore=attScore)
            db.session.add(attendLog)
            # commit both
            db.session.commit()
            return redirect(url_for('att_team'))
        else:
            form.name.data = current_user.username
            form.studentID.data = current_user.studentID
            form.teamcount.data = 0
            form.teamnumber.data = teamNumSet  
    
    #after attendance is complete teamnumber 0 is reassigned to a team  
    elif fields.teamnumber == 0: 
        # { 1 : 1,  2 : 1  ,  3 :  0 }
        teamDict = {}  
        for i in range (1,teamcount+1):
            count = Attendance.query.filter_by(teamnumber=i).count()
            if count: 
                teamDict[i] = count
            else:   
                teamDict[i] = 0
        print (teamDict)

        # all teams are full so make a new team
        if teamDict[teamcount] == teamsize:
            countField = Attendance.query.filter_by(username='Chris').first()
            countField.teamcount = teamcount +1            
            db.session.commit() 
            return redirect(url_for('att_team'))
        # all teams have the same number (first and last) of students so start from beginning
        elif teamDict[1] == teamDict[teamcount]:
            fields.teamnumber = 1
            db.session.commit()
            flash('Your attendance has been recorded', 'info')
            return redirect(url_for('att_team'))
        else:
            for key in teamDict:
                # search each group until one needs to be filled
                if teamDict[key] > teamDict[key+1]:
                    fields.teamnumber = key+1
                    db.session.commit()
                    flash('Your attendance has been recorded', 'info')
                    return redirect(url_for('att_team'))                 
                else: 
                    pass
    
    return render_template('user/attTeam.html', legend=legend, count=count, fields=fields, 
    teamcount=teamcount, form=form, notice=notice, users=users)  
     

######## Assignments //////////////////////////////////////////////

@app.route ("/assignments", methods=['GET','POST'])
@login_required
def assignment_list():     
    assList = Sources.query.order_by(asc(Sources.id)).all()  # also remember .limit(3).all()  
    assList2 = Sources.query.filter_by(part='1').filter(or_(Sources.openSet=='1', Sources.openSet=='2')).order_by(asc(Sources.unit)).order_by(asc(Sources.part)).all()  # also remember .limit(3).all()     
        
    urls = [None, 
        'https://reading-lms.herokuapp.com/ass', 
        'https://workplace-lms.herokuapp.com/ass', 
        'https://icc-lms.herokuapp.com/ass'
    ]  

    href = urls[int(COLOR_SCHEMA)]

    #list of models used to create 
    modDict = Info.modDictAss  
    
    # create dictionary of assignment sources with integers for scoreDict calling
    srcDict = {}   # 0 : ass , grade, comment
    srcCount = 0 
    for ass in assList2:         
        modFields = modDict[ass.unit].query.filter_by(username=current_user.username).first()
        if modFields:     
            srcDict[srcCount] = [ass , modFields.Grade, modFields.Comment]
        else:
            srcDict[srcCount] = [ass , 0, 'Not started yet']
        srcCount += 1   
    srcDictList = list(srcDict.keys())

    
    # count points for assignments and record student grades 
    pointCounter = 0 
    for src in srcDict:
        pointCounter += srcDict[src][1]
    
    fieldsGrade = Grades.query.filter_by(username=current_user.username).first() 
    if fieldsGrade.assignments == pointCounter:
        pass
    else:
        fieldsGrade.assignments = pointCounter
        db.session.commit() 

    total = (len(srcDictList))*2 # number of avaiable points per assignment
    
    try:
        color = pointCounter/(total) 
    except:
        color = 0

    return render_template('units/assignment_list.html', legend='Assignments Dashboard', 
    href=href, assList=assList, srcDict=srcDict, srcDictList=srcDictList,
    pointCounter=pointCounter, total=total, color=color)



@app.route('/audioUpload', methods=['POST', 'GET'])
def audioUpload():

    title = request.form ['title']
    audio_string = request.form ['base64']    

    if title and base64:         
        audio = base64.b64decode(audio_string)
        newTitle = S3_LOCATION + current_user.username + title + '.mp3'
        filename = current_user.username + title + '.mp3'        
        print(S3_BUCKET_NAME)
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)
        return jsonify({'title' : newTitle})
    
    return jsonify ({'error' : 'no upload'})


@app.route("/ass/<string:unit>", methods = ['GET', 'POST'])
@login_required
def ass(unit):
     
    #unitInt = int(unit)
    source = Sources.query.filter_by(unit=unit).filter_by(part='1').first()
    
    forms = [None, AssBasic()]
    form = AssBasic()

    # models update
    modDict = Info.modDictAss

    #check source to see if unit is open yet
    if source.openSet > 0:    
        pass
    else:
        flash('This assignment is not open at the moment', 'danger')
        return redirect(request.referrer)

    #set up model data
    model = modDict[unit]

    #model = models[unitInt]
    count = model.query.filter_by(username=current_user.username).count()
    fields = model.query.filter_by(username=current_user.username).first()
    d = source.assDate
        

    if count == 0:          
        if form.validate_on_submit():
            ##Setting grade 0 in progress 1 late 2 completed              
            assignment = model(username = current_user.username, 
                AudioDataOne = form.AudioDataOne.data, 
                AudioDataTwo = form.AudioDataTwo.data,
                LengthOne = form.LengthOne.data, 
                LengthTwo = form.LengthTwo.data, 
                Notes=form.Notes.data, 
                TextOne= form.TextOne.data, 
                TextTwo= form.TextTwo.data, 
                TextThr= form.TextThr.data,
                DateStart= datetime.now(), # mark date started
                Grade = 0,
                Comment = ""
                )       
            db.session.add(assignment)
            db.session.commit()
            flash('Your assignment has been updated', 'warning') 
            return redirect(request.referrer)
        elif request.method == 'GET': 
            form.AudioDataOne.data = ""
            form.AudioDataTwo.data = ""
            form.LengthOne.data = 0  
            form.LengthTwo.data = 0
            form.TextOne.data = "" 
            form.TextTwo.data = "" 
            form.TextThr.data = "" 
           
            
    if count == 1:         
        if form.validate_on_submit():             
             # set Grade...................
            if form.AudioDataOne.data == "" or form.AudioDataTwo.data == "" or form.TextOne.data == "" or form.TextTwo.data == "":
                fields.Grade = 0
                fields.Comment = 'In progress...' #in progress 
            else:
                if fields.DateStart < source.assDate:
                    fields.Grade = 2  # complete on time
                    fields.Comment = 'Completed on time - Great!'     
                else: 
                    fields.Grade = 1  # late start  
                    fields.Comment = 'This assignment has been completed late'   
            fields.AudioDataOne = form.AudioDataOne.data 
            fields.AudioDataTwo = form.AudioDataTwo.data                                                           
            fields.LengthOne = form.LengthOne.data
            fields.LengthTwo = form.LengthTwo.data 
            fields.Notes = form.Notes.data 
            fields.TextOne = form.TextOne.data
            fields.TextTwo = form.TextTwo.data
            fields.TextThr = form.TextThr.data
            
            
            db.session.commit()
            flash('Your assignment has been updated', 'warning') 
            return redirect(request.referrer)
        elif request.method == 'GET':  
            form.AudioDataOne.data = fields.AudioDataOne  
            form.AudioDataTwo.data = fields.AudioDataTwo    
            form.LengthOne.data = fields.LengthOne  
            form.LengthTwo.data = fields.LengthTwo
            form.Notes.data = fields.Notes
            form.TextOne.data = fields.TextOne
            form.TextTwo.data = fields.TextTwo 
            form.TextThr.data = fields.TextThr 
    
    try:        
        speechModel = model.query.filter_by(username='Chris').first()
    except:
        speechModel = None
    
    return render_template('units/assignment_layout.html', 
         form=form, count=count, fields=fields, unit=unit, source=source, speechModel=speechModel, siteName=S3_BUCKET_NAME)


