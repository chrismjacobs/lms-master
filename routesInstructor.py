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


@app.route ("/att_log")
@login_required
def att_log():  
    if current_user.id != 1:
        return abort(403)
    
    FRDID = [120454132,120512208, 120512220, 120512225, 120514112, 120554035, 120554038,120554051,120554054,120554062,120554102,120554125,120654029,120654033,120654042,120770904,120854002,120854003,120854004,120854005,120854006,120854007,120854008,120854009,120854010,120854011,120854012,120854013,120854015,120854016,120854017,120854018,120854019,120854020,120854021,120854022,120854023,120854025,120854026,120854028,120854029,120854030,120854031,120854032,120854033,120854034,120854037,120854040,120854041,120854044,120854045,120854047,120854048,120854049,120854050,120854051,120854052,320612314,320852201,320852202,320852203,320852204,320852205,320852206,320852207,320852208,320852209,320852210,320852212,320852214,320852215,320852216,320852217,320852218,320852219,320852220,320852221] 
    WPEID = [120454062,120454111,120454115,120454132,120454138,120454142,120454149,120514112,120554009,120554014,120554062,120554102,120554103,120554118,120554125,120654055,120714160,120735608,120754002,120754003,120754004,120754006,120754009,120754011,120754012,120754013,120754015,120754016,120754018,120754019,120754020,120754021,120754023,120754024,120754026,120754029,120754030,120754031,120754034,120754037,120754038,120754040,120754041,120754044,120754045,120754047,120754050,120754051,120754053,120754054,120754055,120754057,120754058,120754059,120754060,120754061,120754062,120754063,120754065,120754066,120754502,120754505,120754509,120754510,120754511,120754514,120754515,320612314] 
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

def examPractice(): 
    from spreadsheet import Sheets    

    grades = Grades.query.order_by(asc(Grades.studentID)).all()

    holder = {}
    practiceDict2 = {}
    for grade in grades:
        practiceDict2[grade.studentID] = { 1 : [],  2 : [] }
        holder[grade.studentID] = ast.literal_eval(grade.practice)
        
     
     
    count = 1
    for sheet in Sheets.sheets:         
        if count < 3:                   
            record_score = sheet.col_values(5)           
            record_id = sheet.col_values(4)
            listLen = len(record_score) 
            for i in range(1, listLen):                
                try: 
                    practiceDict2[str(record_id[i])][count].append(record_score[i])
                except:
                    print(record_id[i]) 
        else:
            pass                    
        count += 1 
        
    

    for key in practiceDict2:
        if str(practiceDict2[key]) != str(holder[key]):
            Grades.query.filter_by(studentID=key).first().practice = str(practiceDict2[key])
            db.session.commit()
            print (practiceDict2[key], '==', holder[key])
        else: 
            print ('PASS')

    return practiceDict2


def examResult():
    from spreadsheet import Sheets
    users = Grades.query.order_by(asc(Grades.studentID)).all()
    examDict = {}    

    for user in users:        
        #examDict[user.studentID] = [0, 0, 'None', 'None']
        listEval = eval(user.examList)        
        examDict[user.studentID] = listEval
             
    userList = {}
    count = 0
    for sheet in Sheets.sheets: 
        count += 1 
        if count == 3:             
            record_score = sheet.col_values(5) 
            print(record_score)
            record_id = sheet.col_values(4)
            listLen = len(record_score) 
            for i in range(1, listLen):  
                if examDict[record_id[i]][2] != record_score[i]:                            
                    examDict[record_id[i]][2] = record_score[i]
                    examDict[record_id[i]][0] = int(record_score[i].split('/')[0])
                    userList[record_id[i]] = examDict[record_id[i]]                   
        elif count == 4:             
            record_score = sheet.col_values(5)           
            record_id = sheet.col_values(4)
            listLen = len(record_score) 
            for i in range(1, listLen):
                if examDict[record_id[i]][3] != record_score[i]:                            
                    examDict[record_id[i]][3] = record_score[i]
                    examDict[record_id[i]][1] = int(record_score[i].split('/')[0])
                    userList[record_id[i]] = examDict[record_id[i]]
        elif count == 5:
            print (sheet.col_values(2))
            record_id = sheet.col_values(2)
            for record in record_id: 
                grade = Grades.query.filter_by(studentID=str(record)).first()                               
                if grade == None:
                    pass
                elif grade.bonus == None:
                    grade.bonus = 3 
                    db.session.commit()
                    print('commit', record, ' - bonus')     
        else:
            pass
    
    print (userList)
    dictionary = userList
    for key in dictionary:
        Grades.query.filter_by(studentID=key).first().examList = str(dictionary[key])
        db.session.commit()
        print('commit', key, ':', dictionary[key])
                   

    return examDict
            


@app.route("/exams", methods = ['GET', 'POST'])
@login_required
def exams():    
    course = Course.query.order_by(asc(Course.date)).all()    
    review = Course.query.filter_by(unit='E1').first()       
    reviewList = eval(str(review.linkTwo))
    bonusList = eval(str(review.embed))
    try:
        practiceDict = examPractice()
    except:
        pass

    grades = Grades.query.filter_by(username=current_user.username).first()
    displayDict = ast.literal_eval(grades.practice)
    print(len(displayDict[1]))

    displayDict = {
        1 : [reviewList[0], displayDict[1]], 
        2 : [reviewList[1], displayDict[2]]
    }

    return render_template('instructor/exams.html', title='exams', reviewList=reviewList, bonusList=bonusList, displayDict=displayDict)



@app.route("/MTGrades", methods = ['GET', 'POST'])
@login_required
def MTGrades():
    midGrades = Grades.query.order_by(asc(Grades.studentID)).all()
    
    examDict = examResult()
    practiceDict = examPractice()
    
    maxUniFactor = 30 / Grades.query.order_by(desc(Grades.units)).first().units  
    maxAssFactor = 30 / Grades.query.order_by(desc(Grades.assignments)).first().assignments
    
    mtDict = {}
    for item in midGrades:
         
        ass = round(item.assignments * maxAssFactor , 1 )
        part = round(item.units * maxUniFactor, 1 )
        examList = eval(item.examList)
        exam = round( ((examList[0] + examList[1])*0.8) , 1)
        if item.bonus !=None:
            bonus = item.bonus
        else:
            bonus = 0
        total = int ( ass + part + exam + bonus )


        
        mtDict[int(item.studentID)] = [ 
            total, 
            item.username, 
            part, 
            ass, 
            exam, 
            examList[2], 
            examList[3], 
            item.extraInt, 
            item.attend, 
            bonus                 
        ]

        
    return render_template('instructor/midGrades.html', title='MTGrades', midGrades=midGrades, mtDict=mtDict)


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
    if current_user.id != 1:
        return abort(403)
    form = Chat()     
    dialogues = ChatBox.query.filter_by(username=user_name).all()
     
    if form.validate_on_submit():
        chat = ChatBox(username = user_name, response=form.response.data, chat=form.chat.data)      
        db.session.add(chat)
        db.session.commit()  
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

    return render_template('user/attInst.html', form=form, status=openData.teamnumber, title='att')  
