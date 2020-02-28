import sys, boto3, random, os, json, ast, time
from sqlalchemy import asc, desc 
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *   
from models import *
from pprint import pprint

from meta import BaseConfig   
s3_resource = BaseConfig.s3_resource  
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN


def get_schedule():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    SOURCES = json.loads(file_content)  # json loads returns a dictionary
    #print(SOURCES)   
    return (SOURCES)
    

@app.route ("/about")
@login_required 
def about():     
    ## src explaining this course
    srcs = get_schedule()
    intro = srcs['1']['M1']      
    return render_template('instructor/about.html', intro=intro)


@app.route("/course", methods = ['GET', 'POST'])
@login_required
def course():  
    # json dumps returns a string
    course = json.dumps(get_schedule())   
    color = json.dumps(DESIGN)   

    return render_template('instructor/course.html', course=course, color=color)


@app.route ("/att_log")
@login_required
def att_log():  
    if current_user.id != 1:
        return abort(403)
    
    IDLIST = BaseConfig.IDLIST

    ## create a list of all course dates    
    course_dates = get_schedule()
    dateList = []
    for c in course_dates:
        date_string = course_dates[c]['Date']
        dt = datetime.strptime(date_string, '%Y-%m-%d')
        dateList.append(dt)    
    print('dateList:', dateList)   
    
    ## log all dates when attendance was complete (and show total att score)
    attLogDict = {}    
    for number in IDLIST:        
        attLogDict[number] = []

    for attLog in attLogDict:
        logs = AttendLog.query.filter_by(studentID=str(attLog)).all() 
        attGrade = 0        
        if logs:                        
            for log in logs:
                d = log.date_posted
                dStr = d.strftime("%m/%d")                
                attLogDict[attLog].append(dStr) 
                attGrade = attGrade + log.attScore
            attLogDict[attLog].insert(0, attGrade) 
        
    print('attLogDict', attLogDict)

    ##get names for all student IDs
    userDict = {}
    users = User.query.all()
    for user in users:
        userDict[int(user.studentID)] = user.username

    today = datetime.now()
    todayDate = today.strftime("%m/%d")  

    return render_template('instructor/att_log.html', title='att_log', attLogDict=attLogDict, dateList=dateList, todayDate=todayDate, userDict=userDict)  




@app.route("/openSet/<string:unit>/<string:part>", methods = ['POST'])
def openSet(unit,part):
    # set unit participation from sources page
    status = request.form['status' + unit + part]
    openSetModel = Sources.query.filter_by(unit=unit).filter_by(part=part).first()
    openSetModel.openSet = status
    db.session.commit() 
    return redirect(url_for('unit_list'))    


@app.route ("/studentRemove/<string:name>", methods = ['GET', 'POST'])
@login_required 
def studentRemove(name):
    if current_user.id != 1:
        return abort(403)   

    findSt = Attendance.query.filter_by(username=name).first()    
    
    #delete the attendances entries using ids
    Attendance.query.filter_by(id=findSt.id).delete()
    db.session.commit()

    AttendLog.query.filter_by(id=findSt.unit).delete()
    db.session.commit()
    
    #find the team work today
    todaysUnit = Attendance.query.filter_by(username='Chris').first().unit   
    studentTeam = Attendance.query.filter_by(username=name).first().teamnumber
    
    idNum = 0 
    for model in Info.unit_mods_list:
        # ie search for u061u
        if todaysUnit + '1' in str (model):
            try:
                idNum = model.query.filter_by(teamnumber=studentTeam).first().id
            except:
                pass
            

    string = [None, 'reading', 'workplace', 'icc']    
    lms = string[int(SCHEMA)]

    return jsonify({'removed' : name, 'unit' : todaysUnit, 'idNum' : idNum, 'lms': lms})



@app.route ("/teams")
@login_required 
def teams():  
    if current_user.id != 1:
        return abort(403)       

    try:
        teamcount = Attendance.query.filter_by(username='Chris').first().teamcount
    except:
        flash('Attendance not open yet', 'danger')
        return redirect(url_for('home')) 
    
    if teamcount > 0: 
        attDict = {}  #  teamnumber = fields, 1,2,3,4 names
        for i in range(1, teamcount+1):
            teamCall = Attendance.query.filter_by(teamnumber=i).all()
            attDict[i] = teamCall    
    # if team count set to zero ---> solo joining
    else:
        attDict = {}
        users = User.query.order_by(asc(User.studentID)).all()        
        for user in users:
            attStudent = Attendance.query.filter_by(username=user.username).first() 
            if attStudent:
                attDict[user.username] = [user.studentID, attStudent.date_posted]
            else:
                attDict[user.username] = [user.studentID, 0]
    print(attDict)

    tablesDict = {}
    
    return render_template('instructor/teams.html', attDict=attDict, teamcount=teamcount, title='teams')  


'''
@app.route('/upload/<string:assignment>', methods=['POST', 'GET'])
def upload(assignment):
    file = request.files['file']
    fn = file.filename
    file_name = current_user.username + '_' + fn + '_' + assignment + '.mp3'   
    my_bucket = s3_resource.Bucket(S3_BUCKET_NAME)
    my_bucket.Object(file_name).put(Body=file)

    return redirect(request.referrer)
'''

@app.route("/commentSet/<string:unit>/<string:name>", methods = ['POST'])
def commentSet(unit,name):    
    newComment = request.form['comment']
    mods = Info.ass_mods_dict
    studentAns = mods[unit].query.filter_by(username=name).first()

    studentAns.Comment = newComment
    db.session.commit()   
    
    grades = Grades.query.filter_by(username=name).first()
    string = grades.extraStr
    if string:
        gradeSet = eval(string)
        gradeSet.add(int(unit))
        grades.extraStr = str(gradeSet)
        db.session.commit()  
    else:        
        grades.extraStr = '{' + str(int(unit)) + '}'
        db.session.commit()  

    return jsonify({'comment' : newComment})

@app.route ("/dashboard")
@login_required 
def dashboard():  
    if current_user.id != 1:
        return abort(403)

    ansDict = {}
    for item in Info.ass_mods_dict:    
        ansDict[item] = [Info.ass_mods_dict[item]]
    # {'01': [<class 'models.A01A'>], '02': [<class 'models.A02A'>],  only used for dashboard
    
    for item in ansDict:
        model = ansDict[item][0]
        answers = model.query.order_by(desc(model.Grade)).all() # find that item model and query it
        count = len(answers)
        ansDict[item].append(answers)
        ansDict[item].append(count)
    
    ansRange = len(ansDict)     
    
    return render_template('instructor/dashboard.html', ansDict=ansDict, ansRange=ansRange, title='dashboard')  

@app.route ("/students")
@login_required 
def students():
    if current_user.id != 1:
        return abort(403) 

    sDict = {}
    students = User.query.order_by(asc(User.studentID)).all()  
    for student in students:  

        sDict[student.username] = {
            'idn' : student.studentID, 
            'img' : student.image_file,
            'eml' : student.email,
            'att' : 'Absent',
            'units' : 0,             
            'asses' : 0 
        }   

    #### attend todays attendance
    attendance = Attendance.query.all()
    for att in attendance: 
        sDict[att.username]['att'] = att.attend


    #### add student grading
    for model in Info.unit_mods_list:
        rows = model.query.all()   
        for row in rows:    
                                  
            names = ast.literal_eval(row.username)            
            for name in names:
                sDict[name]['units'] += row.Grade
    
    for model in Info.ass_mods_list:        
        rows = model.query.all()        
        for row in rows:
            
            sDict[row.username]['asses'] += row.Grade   

    print(sDict)   

    from routesUser import get_grades
    grades = get_grades(False, False)
    maxU = grades['maxU']
    maxA = grades['maxA']

    
    return render_template('instructor/students.html', students=students, S3_LOCATION=S3_LOCATION, 
    sDict=sDict, maxU=maxU, maxA=maxA, title='students')  



@app.route ("/inchat/<string:user_name>", methods = ['GET', 'POST'])
@login_required 
def inchat(user_name):
    from flask_mail import Message
    if current_user.id != 1:
        return abort(403)
    form = Chat() 
    email = User.query.filter_by(username=user_name).first().email    
    print (email)
    dialogues = ChatBox.query.filter_by(username=user_name).all()
    websites = ['blank', 'READING', 'WORKPLACE', 'ICC']
    website = 'https://' + websites[int(SCHEMA)] + '-lms.herokuapp.com'
    messText = 'New message for ' + websites[int(SCHEMA)] + ' English class'
    if form.validate_on_submit():
        chat = ChatBox(username = user_name, response=form.response.data, chat=form.chat.data)      
        db.session.add(chat)
        db.session.commit()  
        msg = Message(messText, 
                    sender='chrisflask0212@gmail.com', 
                    recipients=[email ,'cjx02121981@gmail.com'])
        msg.body = f'''You have a message from waiting for you at {website}. Please follow the link to read and reply. (DO NOT REPLY TO THIS EMAIL)'''
        #jinja2 template can be used to make more complex emails
        mail.send(msg)
        return redirect(url_for('inchat', user_name=user_name))
    else:
        form.name.data = current_user.username
        form.response.data = ""
        form.chat.data = ""
        image_file = S3_LOCATION + User.query.filter_by(username=user_name).first().image_file      
      
    image_chris = S3_LOCATION + User.query.filter_by(id=1).first().image_file

    return render_template('instructor/inchat.html', form=form, dialogues=dialogues, name=user_name, image_chris=image_chris, image_file=image_file)


def change_late():
    openData = Attendance.query.filter_by(username='Chris').first()
    if openData.teamnumber == 98:
        openData.teamnumber = 99
    elif openData.teamnumber == 50:
        openData.teamnumber = 51
    db.session.commit()

def set_timer():
    #https://docs.python.org/2/library/sched.html
    import time
    from threading import Timer
    
    print (time.time())
    Timer(1800, change_late, ()).start()
    time.sleep(7800)

    openData = Attendance.query.filter_by(username='Chris').first()
    openData.teamnumber = 100
    db.session.commit()

# set up the attendence for the day
@app.route("/att_int", methods = ['GET', 'POST'])
@login_required
def att_int():
    if current_user.id != 1:
        return abort(403)
    form = AttendInst()
    openData = Attendance.query.filter_by(username='Chris').first()

    if openData:    
        if form.validate_on_submit(): 

            openData.attend = form.attend.data 
            openData.teamnumber = form.teamnumber.data 
            openData.teamsize = form.teamsize.data 
            openData.teamcount = form.teamcount.data 
            openData.unit =  form.unit.data 

            set_timer()

            db.session.commit() 
            if form.teamnumber.data == 100:
                sourceCheck = Sources.query.filter_by(openSet='2').all()
                #return to normal state after attendence closed
                for sourceLine in sourceCheck:
                    sourceLine.openReset = 0
                    sourceLine.openSet = 1
                    db.session.commit() 
            
            flash('Attendance has been updated', 'secondary') 
            return redirect(url_for('att_team')) 
        else:
            form.username.data = 'Chris'
            form.studentID.data = '100000000'
            try:
                form.attend.data = openData.attend
                form.teamnumber.data = openData.teamnumber
                form.teamsize.data = openData.teamsize
                form.teamcount.data = openData.teamcount
                form.unit.data = openData.unit                
            except: 
                pass 
    else:
        flash('Attendance not set up', 'secondary') 
        return redirect(request.referrer)  

    return render_template('instructor/att_int.html', form=form, status=openData.teamnumber, title='controls')  


######## Attendance //////////////////////////////////////////////
@app.route("/att_team", methods = ['GET', 'POST'])
@login_required
def att_team():

    legend = 'Attendance: ' + time.strftime('%A %b, %d %Y %H:%M')

    # check if attendance is open 
    openData = Attendance.query.filter_by(username='Chris').first()
    if openData:
        openCheck = openData.teamnumber
        if openCheck == 98 or openCheck == 50:  # 98 open in normal state, 50 open in midterm state - all units can be done
            form = Attend()  
        elif openCheck == 99 or openCheck == 51:  # switch to late form
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
            attendLog = AttendLog(
                username = form.name.data, 
                attend=form.attend.data,teamnumber=form.teamnumber.data, 
                studentID=form.studentID.data, attScore=attScore
                )
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

        # check the last team is full eg team 12 == 4 students
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
    
    return render_template('instructor/att_team.html', legend=legend, count=count, fields=fields, 
    teamcount=teamcount, form=form, notice=notice, users=users)  