import sys, boto3, random, base64, os, secrets, httplib2, json, ast
from sqlalchemy import asc, desc 
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *   
from models import *


try:
    from aws import Settings    
    s3_resource = Settings.s3_resource  
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME  
    COLOR_SCHEMA = Settings.COLOR_SCHEMA
    STUDENTID = Settings.STUDENTID
except:
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME'] 
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 
    STUDENTID = []

@app.route("/webrtc3", methods = ['GET', 'POST'])
def webrtc3():       
    return render_template('instructor/gersonrosales3.html')    


@app.route ("/about")
@login_required 
def about():     
    about = Sources.query.filter_by(unit='00').filter_by(part='1').first().notes   

    return render_template('instructor/about.html', about=about, siteName=S3_BUCKET_NAME)

@app.route("/course", methods = ['GET', 'POST'])
@login_required
def course():
    course = Course.query.order_by(asc(Course.date)).all()   
    return render_template('instructor/course.html', course=course)

@app.route("/purge", methods = ['GET', 'POST'])
@login_required
def purge():
    if current_user.id != 1:
        return abort(403)  
    
    newModList = [Info.modListUnits[0]]

    purgeDict = {}
    for mod in Info.modListUnits:
        lines = mod.query.filter_by(Grade=0).all()
        names = []
        for line in lines:
            if line.Ans01 == "":  
                names.append(line.username) 
                mod.query.filter_by(id=line.id).delete()                
                db.session.commit()
            else:
                purgeDict[line.username] = ['check', mod ] 
        purgeDict[mod] = names
    
    print (purgeDict)

    return render_template('instructor/purge.html', purgeDict=purgeDict)

@app.route("/reset4562", methods = ['GET', 'POST'])
@login_required
def reset():
    if current_user.id != 1:
        return abort(403)  
    
    grades = Grades.query.all()
    
    for grad in grades: 
        grad.assignments = 0 
        grad.units = 0 
        grad.attend = 0 
        grad.bonus = 0 
        grad.extraInt = 0 
        grad.examList = None
        grad.tries = 0 
        grad.practice = None
        db.session.commit()    


    return 'reset complete'

@app.route ("/att_log")
@login_required
def att_log():  
    if current_user.id != 1:
        return abort(403)
    
    FRDID = [120454132,120512208, 120512220, 120512225, 120514112, 120554035, 120554038,120554051,120554054,120554062,120554102,120554125,120654029,120654033,120654042,120770904,120854002,120854003,120854004,120854005,120854006,120854007,120854008,120854009,120854010,120854011,120854012,120854013,120854015,120854016,120854017,120854018,120854019,120854020,120854021,120854022,120854023,120854025,120854026,120854028,120854029,120854030,120854031,120854032,120854033,120854034,120854037,120854040,120854041,120854044,120854045,120854047,120854048,120854049,120854050,120854051,120854052,320612314,320852201,320852202,320852203,320852204,320852205,320852207,320852208,320852209,320852210,320852212,320852214,320852215,320852216,320852217,320852218,320852219,320852220,320852221] 
    WPEID = [120454062,120454111,120454115,120454132,120454138,120454142,120454149,120514112,120554009,120554014,120554062,120554102,120554103,120554118,120554125,120654055,120714160,120735608,120754002,120754003,120754004,120754006,120754009,120754011,120754012,120754013,120754015,120754016,120754018,120754019,120754020,120754021,120754023,120754024,120754026,120754029,120754030,120754031,120754034,120754037,120754038,120754040,120754041,120754044,120754045,120754047,120754050,120754051,120754053,120754054,120754055,120754057,120754058,120754059,120754060,120754061,120754062,120754063,120754065,120754066,120754502,120754505,120754509,120754510,120754514,120754515,320612314] 
    ICCID = [120433033,120454111,120454138,120536002,120536011,120536019,120614035,120614055,120614102,120614103,120614105,120614116,120614118,120614119,120614125,120614132,120614133,120615233,120654003,120654005,120654006,120654007,120654008,120654009,120654010,120654012,120654013,120654014,120654018,120654019,120654022,120654026,120654028,120654029,120654030,120654031,120654033,120654034,120654039,120654040,120654041,120654042,120654045,120654051,120654052,120654055,120654056,120654064,120654065,120654066,120654067,120654068,120654505,120715231,320451002,320451349]     
    IDLIST = [0, FRDID, WPEID, ICCID]

    ## create a list of all course dates
    course = Course.query.order_by(asc(Course.date)).all()   
    dateList = []
    for c in course:
        date = c.date
        dateList.append(date.strftime("%m/%d"))    
    print('dateList', dateList)   
    
    ## log all dates when attendance was complete (and show total att score)
    attLogDict = {}    
    for number in IDLIST[int(COLOR_SCHEMA)]:        
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






def loadAWS():
    jList = [
        [None, None],
        ['reading-lms', "profiles/ExamFRD.json"],
        ['workplace-lms', "profiles/ExamWPE.json"],
        ['icc-lms', "profiles/ExamICC.json"]
    ]   
    content_object = s3_resource.Object(
        jList[int(COLOR_SCHEMA)][0],
        jList[int(COLOR_SCHEMA)][1]
    )

    file_content = content_object.get()['Body'].read().decode('utf-8')
    jload = json.loads(file_content)
    print(type(jload))

    return jload

 
@app.route("/exams", methods = ['GET', 'POST'])
@login_required
def exams():    
    course = Course.query.order_by(asc(Course.date)).all()    
    review = Course.query.filter_by(unit='E1').first()       
    reviewList = eval(str(review.linkTwo))
    try: 
        bonusList = eval(str(review.embed))
    except: 
        bonusList = []

    jload = loadAWS()    
    try:
        
        tries = [None, 
                list(jload[current_user.studentID]["P1"].values()), 
                list(jload[current_user.studentID]["P2"].values())                
                ]
        print ('TRY')   
    except:
        tries = [None, [],[]]
        print ('EXCEPT')

    print (reviewList)
    displayDict = {}
    for i in range (1,3):
        displayDict[i] = [reviewList[i-1], tries[i]]
    
   

    return render_template('instructor/exams.html', title='exams', reviewList=reviewList, bonusList=bonusList, displayDict=displayDict, COLOR_SCHEMA=COLOR_SCHEMA)





def loadExam():
    gradesList = [
    [None, None],
    ['reading-lms', "profiles/GradesFRD.json"],
    ['workplace-lms', "profiles/GradesWPE.json"],
    ['icc-lms', "profiles/GradesICC.json"]
    ]
    
    content_object = s3_resource.Object(
        gradesList[int(COLOR_SCHEMA)][0],
        gradesList[int(COLOR_SCHEMA)][1]
    )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    jload = json.loads(file_content)
    return jload

@app.route("/MTGrades", methods = ['GET', 'POST'])
@login_required
def MTGrades():
    finalGrades = loadExam()
     
    print(finalGrades)
    
    finalDict = {}
    
    
    for student in finalGrades:
        NAME = finalGrades[student]['NAME']
        MT = int(finalGrades[student]['MT'])/2
        PART = (   int(finalGrades[student]['PART'])    /32    )*15
        ASSN = (   int(finalGrades[student]['ASSN'])    /8     )*15 
        EXAM = 10
        TOTAL = MT + PART + ASSN + EXAM 

        finalDict[int(student)] = [TOTAL, NAME, MT, PART, ASSN, EXAM ]

    print (finalDict)
        
    return render_template('instructor/midGrades.html', title='MTGrades', midGrades=finalGrades, mtDict=finalDict)


@app.route("/openSet/<string:unit>/<string:part>", methods = ['POST'])
def openSet(unit,part):
    # set unit participation from sources page
    status = request.form['status' + unit + part]
    openSetModel = Sources.query.filter_by(unit=unit).filter_by(part=part).first()
    openSetModel.openSet = status
    db.session.commit() 
    return redirect(url_for('unit_list'))    


@app.route("/sources", methods = ['GET', 'POST'])
@login_required
def sources():
    
    sources = Sources.query.order_by(asc(Sources.unit)).order_by(asc(Sources.part)).all()    

    return render_template('instructor/sources.html', sources=sources, title='sources')


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
    for model in Info.modListUnits:
        # ie search for u061u
        if todaysUnit + '1' in str (model):
            try:
                idNum = model.query.filter_by(teamnumber=studentTeam).first().id
            except:
                pass
            

    string = [None, 'reading', 'workplace', 'icc']    
    lms = string[int(COLOR_SCHEMA)]

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


@app.route ("/s3console")
@login_required 
def s3console():   
    if current_user.id != 1:
        return abort(403)     
    
    my_bucket = s3_resource.Bucket(S3_BUCKET_NAME)
    files = my_bucket.objects.all()        

    return render_template('instructor/s3console.html', my_bucket=my_bucket, files=files, location=S3_LOCATION)  


@app.route('/upload/<string:assignment>', methods=['POST', 'GET'])
def upload(assignment):
    file = request.files['file']
    fn = file.filename
    file_name = current_user.username + '_' + fn + '_' + assignment + '.mp3'   
    my_bucket = s3_resource.Bucket(S3_BUCKET_NAME)
    my_bucket.Object(file_name).put(Body=file)

    return redirect(request.referrer)


@app.route("/commentSet/<string:unit>/<string:name>", methods = ['POST'])
def commentSet(unit,name):    
    newComment = request.form['comment']
    mods = Info.modDictAss
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

    ### replace this with modDictAss
    ansDict = Info.ansDict
    
    for item in ansDict:
        model = ansDict[item][0]
        answers = model.query.order_by(desc(model.Grade)).all() # find that item model and query it
        count = len(answers)
        ansDict[item].append(answers)
        ansDict[item].append(count)
        #ansDict[item][1] = answers
        #ansDict[item][2] = count
        # dictionary set to model, answer, number of answers

    gradesDict = {}
    grades = Grades.query.all()
    for grade in grades:
        gradesDict[grade.username] = grade.extraStr

    
    ansRange = len(ansDict)     
    
    return render_template('instructor/dashboard.html', ansDict=ansDict, ansRange=ansRange, grades=gradesDict, title='dashboard')  

@app.route ("/students")
@login_required 
def students():
    if current_user.id != 1:
        return abort(403)  
    
    students = User.query.order_by(asc(User.studentID)).all()

    maxUni = Grades.query.order_by(desc(Grades.units)).first().units
    maxAss = Grades.query.order_by(desc(Grades.assignments)).first().assignments
    maxAtt = Grades.query.order_by(desc(Grades.attend)).first().attend    


    lastChats = {}  ##dictionary  name : last chat string version , color code number x3
    for student in students:
        name = student.username
        
        chat = ChatBox.query.filter_by(username=name).all()        
        number = len(chat)
        d = datetime.today() - timedelta(days=7)
        if number > 0:            
            lastChat = chat[number-1]
            if lastChat.date_posted > d:
                stringChat = str(lastChat).split(',')[1]
                lastChats[name]= [ stringChat, 0,0,0]  ##add to dictionary name : lastchat then add color values           
            else: 
                lastChats[name] = [0,0,0,0]
        else:      
            lastChats[name] = [0,0,0,0]
        
        fieldsGrade = Grades.query.filter_by(username=name).first() 
        #set up colors
        try:
            lastChats[name][1] = fieldsGrade.attend/maxAtt
        except:
            lastChats[name][1] = 0
        try:
            lastChats[name][2] = fieldsGrade.units/maxUni
        except:
            lastChats[name][2] = 0 
        try:
            lastChats[name][3] = fieldsGrade.assignments/maxAss
        except:
            lastChats[name][3] = 0     

    ## FormFill Task
    attDict = {}
    for student in students:        

        attendance = Attendance.query.filter_by(studentID=student.studentID).first()
                                
        if attendance == None:
            attDict[student.studentID] = ['true', 'true', 'Absent', 0, 0]
        elif attendance.attend == 'Late':
            attDict[student.studentID] = ['true', 'false', 'Late', attendance.unit, attendance.id]
        elif attendance.attend == '2nd Class':
            attDict[student.studentID] = ['true', 'false', '2nd Class', attendance.unit, attendance.id]
        elif attendance.attend == 'On time':         
            attDict[student.studentID] = ['false', 'false', 'On time', attendance.unit, attendance.id]        
        else:
            attDict[student.studentID] = ['false', 'false', 'On time', 0, attendance.id]
    
    
    timeDict = {
        0 : ['_6','_7'],
        1 : ['_8','_9'], 
        2 : ['_6','_7'],
        3 : ['_3','_4'],
        4 : ["document.getElementById('DDList", "_1').checked=true;"]
        }

    formFill = []
    for key in attDict:  
        if attDict[key][0] == 'true':  
            formFill.append(timeDict[4][0] + key + timeDict[int(COLOR_SCHEMA)][0] + timeDict[4][1])
        if attDict[key][1] == 'true':
            formFill.append(timeDict[4][0] + key + timeDict[int(COLOR_SCHEMA)][1] + timeDict[4][1] )
        
    
    return render_template('instructor/students.html', students=students, LOCATION=S3_LOCATION, 
    lastChats=lastChats, formFill=formFill, attDict=attDict, title='students')  


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
    website = 'https://' + websites[int(COLOR_SCHEMA)] + '-lms.herokuapp.com'
    messText = 'New message for ' + websites[int(COLOR_SCHEMA)] + ' English class'
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


# set up the attendence for the day
@app.route("/attend_int", methods = ['GET', 'POST'])
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
        flash('Attendance not started', 'secondary') 
        return redirect(request.referrer)  

    return render_template('user/attInst.html', form=form, status=openData.teamnumber, title='controls')  
