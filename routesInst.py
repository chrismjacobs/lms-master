import json, time
from sqlalchemy import asc, desc
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db, bcrypt, mail
from flask_login import current_user, login_required
from forms import *
from models import *
from pprint import pprint
from meta import *
from routesGet import getUsers, get_MTFN
s3_resource = BaseConfig.s3_resource


def putData():
    SCHEMA = getSchema()
    userList = User.query.filter_by(schema=SCHEMA).all()

    students = {}

    for user in userList:
        students[user.username] = user.studentID

    with open('student.json', 'r') as json_file:
        sDict = json.load(json_file)

    sDict.update(students)

    print(len(sDict))

    with open('student.json', 'w') as json_file:
        json.dump(sDict, json_file)



def get_schedule():
    SCHEMA = getSchema()
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']
    print('S3', S3_BUCKET_NAME)
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    SOURCES = json.loads(file_content)  # json loads returns a dictionary
    #print(SOURCES)
    return (SOURCES)


@app.route ("/about")
@login_required
def about():
    SCHEMA = getSchema()
    ## src explaining this course
    srcs = get_schedule()
    intro = srcs['1']['M1']
    video = srcs['1']['M2']

    videoSet = False

    if video:
        videoSet = True

    return render_template('instructor/about.html', intro=intro, SCHEMA=SCHEMA, video=video, videoSet=videoSet)


@app.route("/course", methods = ['GET', 'POST'])
@login_required
def course():
    # json dumps returns a string
    course = json.dumps(get_schedule())
    SCHEMA = getSchema()
    DESIGN = schemaList[SCHEMA]['DESIGN']
    color = json.dumps(DESIGN)

    return render_template('instructor/course.html', title='Course', course=course, color=color)


@app.route ("/att_log", methods = ['GET', 'POST'])
@login_required
def att_log():
    if current_user.id != 1:
        return abort(403)
    SCHEMA = getSchema()
    courseCode = schemaList[SCHEMA]['courseCode']

    with open("static/ids.json", "r") as f:
        idDict = json.load(f)

    # idDict  = idList2

    IDLIST = idDict[courseCode]

    if current_user.id != 1:
        return abort(403)



    ## create a list of all course dates
    course_dates = get_schedule()
    print(course_dates)
    dateList = []
    for c in course_dates:
        print(c)
        print(course_dates[c]['Date'])
        date_string = course_dates[c]['Date']
        dateList.append(date_string)

    print('dateList:', dateList)


    ### create a dictionary of all att_logs
    userLogsDict = {}

    # set up user dict for vue table
    for number in IDLIST:
        # make a new dateDict for each number
        dateDict = {}
        for date in dateList:
            dateDict[date] = 0

        userLogsDict[number] = {
            'user' : None,
            'dates' : dateDict,
            'grade' : 0
        }

    # add data to user dict
    logs = getModels()['AttendLog_'].query.all()
    for log in logs:

        date = log.date_posted
        print(date)
        check = date.strftime("%Y-%m-%d")
        print(check)
        if check in dateList:
            if log.studentID in userLogsDict:
                print(log.username, log.studentID, userLogsDict[log.studentID]['dates'])
                userLogsDict[log.studentID]['user'] = log.username
                userLogsDict[log.studentID]['grade'] += log.attScore
                userLogsDict[log.studentID]['dates'][check] = 1
                print(log.username, log.studentID, userLogsDict[log.studentID]['dates'])
            else:
                print('ID check fail', log.username)
        else:
            print('Date not found')

    #print(userLogsDict)
    return render_template('instructor/att_log.html', title='att_log', logString=json.dumps(userLogsDict), dateString=json.dumps(dateList))



@app.route("/commentSet", methods = ['POST'])
def commentSet():

    newComment = request.form['comment']
    unit = request.form['unit']
    name = request.form['user']
    mods = getInfo()['aModsDict']
    studentAns = mods[unit].query.filter_by(username=name).first()

    studentAns.Comment = newComment
    db.session.commit()

    return jsonify({'comment' : newComment})



@app.route ("/dashboard")
@login_required
def dashboard():
    SCHEMA = getSchema()

    userList = getUsers(SCHEMA)



    if current_user.id != 1:
        return abort(403)

    ## intro edit
    if SCHEMA == 6 or SCHEMA == 3:
        period = ['01', '02', '03', '04', '05','06', '07', '08', '09', '10']
    else:
        period = ['01', '02', '03', '04', '05','06', '07', '08']



    totalDict = {}
    allStudents = userList
    for user in allStudents:
        example = {
                'idNum' : None,
                'A1' :None,
                'A2' :None,
                'L1' :None,
                'L2' :None,
                'L2' :None,
                'Notes' :None,
                'T1' :None,
                'T2' :None,
                'G' :None,
                'C' :None
                }
        totalDict[user.username] = {
            period[0] : example,
            period[1] : example,
            period[2] : example,
            period[3] : example,
        }

    print(totalDict)

    for unit in period:
        model = getInfo()['aModsDict'][unit]
        answers = model.query.order_by(desc(model.Grade)).all()
        for item in answers:
            totalDict[item.username][unit] = {
                'date' : str(item.date_posted),
                'user' : item.username,
                'idNum' : item.id,
                'A1' : item.AudioDataOne,
                'A2' : item.AudioDataTwo,
                'L1' : item.LengthOne,
                'L2' : item.LengthTwo,
                'L2' : item.LengthTwo,
                'Notes' : item.Notes,
                'T1' : item.TextOne,
                'T2' : item.TextTwo,
                'G' : item.Grade,
                'C' : item.Comment,
                }

    pprint(totalDict)


    att = getModels()['Attendance_'].query.filter_by(username="Chris").first().teamnumber


    return render_template('instructor/dashboard.html', ansString=json.dumps(totalDict), title='dashboard', SCHEMA=SCHEMA, att=att, MTFN=get_MTFN('grades'))

@app.route ("/dashboardTest")
def dashboardTest():
    SCHEMA = getSchema()


    fileName = 'ICC_assignments'

    if SCHEMA == 1:
        fileName = 'FRD_assignments'
    if SCHEMA == 2:
        fileName = 'WPE_assignments'

    static = "static\\example_data\\"


    with open(static + fileName + '.json', 'r') as json_file:
        totalDict = json.load(json_file)


        return render_template('instructor/dashboardTest.html', ansString=json.dumps(totalDict), title='dashboard')


@app.route("/refreshAttend", methods = ['POST'])
def get_attend_list():

    if current_user.id != 1:
        return abort(403)

    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    courseCode = schemaList[SCHEMA]['courseCode']

    with open("static/ids.json", "r") as f:
        idDict = json.load(f)



    # idDict  = idList2


    IDLIST = idDict[courseCode]
    print(IDLIST, SCHEMA, courseCode)


    sDict = {}

    for s in IDLIST:
        sDict[s] = {
                'nme' : None,
                'img' : None,
                'eml' : None,
                'att' : 'Unregistered',
                'count' : None
            }

    ignore = ['Chris', 'Test', 'Duo']
    count = 1

    students = getUsers(SCHEMA)

    for student in students:
        if student.studentID not in IDLIST:
            print (student.studentID)
            print(student.username)
            sDict[student.studentID] = {
                'nme' : None,
                'img' : None,
                'eml' : None,
                'att' : 'Unregistered',
            }
        sDict[student.studentID]['nme'] = student.username
        sDict[student.studentID]['img'] = S3_LOCATION + student.image_file
        sDict[student.studentID]['eml'] = student.email
        sDict[student.studentID]['att'] = 'Absent'
        if student.username not in ignore:
            sDict[student.studentID]['count'] = count
            count += 1

    print('sDict', json.dumps(sDict))

    #### attend todays attendance
    attendance = getModels()['Attendance_'].query.all()
    for att in attendance:
        if sDict[att.studentID]:
            sDict[att.studentID]['att'] = att.attend

    if request.method == 'POST':
        return jsonify({'attString' : json.dumps(sDict) })
    else:
        return json.dumps(sDict)


@app.route("/refreshTeams", methods = ['POST'])
def get_team_list():

    print('teamcount', getModels()['Attendance_'])

    instructor = getModels()['Attendance_'].query.filter_by(username='Chris').first()

    if instructor.teamcount:
        teamcount = instructor.teamcount
    else:
        teamcount = 0

    if teamcount > 0:
        attDict = {}  #  teamnumber = fields, 1,2,3,4 names
        for i in range(1, teamcount+1):
            teamCall = getModels()['Attendance_'].query.filter_by(teamnumber=i).all()
            print(teamCall)
            teamCall_students = []
            for s in teamCall:
                teamCall_students.append(s.username)
            attDict[i] = teamCall_students
            print (teamCall_students)

        teamString = json.dumps(attDict)
    else:
        teamString = json.dumps({ 1 : []})

    if request.method == 'POST':
        return jsonify({'teamString' : teamString })
    else:
        return teamString


@app.route("/updateCourse", methods = ['POST'])
def updateCourse():

    userData = request.form['userData']
    course = request.form['course']

    print('userData', userData, course)

    u = User.query.filter_by(studentID=userData).first()


    if course == 'frd':
        if u.frd == 0:
            u.frd = 1
        elif u.frd == 1:
            u.frd = 2
        elif u.frd == 2:
            u.frd = 0

    if course == 'wpe':
        if u.wpe == 0:
            u.wpe = 1
        elif u.wpe == 1:
            u.wpe = 2
        elif u.wpe == 2:
            u.wpe = 0

    if course == 'icc':
        if u.icc == 0:
            u.icc = 1
        else:
            u.icc = 0

    if course == 'lnc':
        if u.lnc == 0:
            u.lnc = 1
        else:
            u.lnc = 0

    if course == 'vtm' :
        if u.vtm == 0:
            u.vtm = 1
        else:
            u.vtm  = 0

    if course == 'png' :
        if u.png == 0:
            u.png = 1
        else:
            u.png  = 0

    db.session.commit()

    uDict = {}
    uDict['frd'] = u.frd
    uDict['wpe'] = u.wpe
    uDict['icc'] = u.icc
    uDict['lnc'] = u.lnc
    uDict['vtm'] = u.vtm
    uDict['png'] = u.png


    return jsonify({'userData' : userData, 'uDict' : json.dumps(uDict), 'course' : course})




@app.route ("/master_controls")
#@login_required
def master_controls():
    if current_user.id != 1:
        return abort(403)


    with open("static/ids.json", "r") as f:
        idDict = json.load(f)

    # idDict  = idList2

    idList = {}

    for c in idDict:
        for s in idDict[c]:
            idList[s]=0

    # master = User.query.get(1)
    # master.device = json.dumps(idList)
    # db.session.commit()

    userData = User.query.all()

    sDict = {
    }

    uDict = {
    }



    for u in userData:
        uDict['id'] = u.id
        uDict['username'] = u.username
        uDict['studentID'] = u.studentID
        uDict['frd'] = u.frd
        uDict['lnc'] = u.lnc
        uDict['wpe'] = u.wpe
        uDict['icc'] = u.icc
        uDict['vtm'] = u.vtm
        uDict['extra'] = u.extra
        uDict['new'] = 0

        if u.studentID not in idList:
            uDict['new'] = 1

        sDict[u.studentID] = uDict.copy()




    setString = json.dumps(sDict)
    idString = json.dumps(idDict)


    return render_template('instructor/master_controls.html', setString=setString, idString=idString, title='Master')

@app.route ("/controls")
@login_required
def controls():
    if current_user.id != 1:
        return abort(403)



    SCHEMA = getSchema()

    attend_list = get_attend_list()
    # print('ATTEND_LIST1', attend_list)
    team_list = get_team_list()
    openData = getModels()['Attendance_'].query.filter_by(username='Chris').first()




    setDict = {
        'Notice' : openData.attend,
        'Set_mode' : openData.teamnumber,
        'Unit' : openData.unit,
        'Size' : openData.teamsize,
        'Count' : openData.teamcount,
    }

    setString = json.dumps(setDict)

    return render_template('instructor/controls.html', SCHEMA=SCHEMA, setString=setString, attend_list=attend_list, team_list=team_list, title='Controls')

@app.route("/updateSet", methods = ['POST'])
@login_required
def updateSet():

    setOBJ = request.form['setOBJ']

    setDict = json.loads(setOBJ)

    print('setDict', setDict)

    notice = setDict['notice']
    unit = setDict['unit']
    teamcount = setDict['teamcount']
    teamsize = setDict['teamsize']
    set_mode = setDict['set_mode']

    openData = getModels()['Attendance_'].query.filter_by(username='Chris').first()

    if int(set_mode) == 100:
        db.session.query(getModels()['Attendance_']).delete()
        db.session.commit()
        attendance = getModels()['Attendance_'](username = 'Chris',
        attend='Notice', teamnumber=97,  teamsize=4, teamcount=10, studentID='100000000')
        db.session.add(attendance)
        db.session.commit()
    else:
        openData.teamcount = int(teamcount)
        openData.teamsize = int(teamsize)
        openData.unit = unit
        # notice and set mode are diff columns
        openData.attend = notice
        openData.teamnumber = int(set_mode)

        db.session.commit()


    setDict = {
        'Notice' : openData.attend,
        'Set_mode' : openData.teamnumber,
        'Unit' : openData.unit,
        'Size' : openData.teamsize,
        'Count' : openData.teamcount,
    }

    setString = json.dumps(setDict)


    return jsonify({'set_mode' : set_mode, 'setString' : setString})



@app.route ("/inchat/<string:user_name>", methods = ['GET', 'POST'])
@login_required
def inchat(user_name):

    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']


    from flask_mail import Message
    if current_user.id != 1:
        return abort(403)
    form = Chat()
    email = User.query.filter_by(username=user_name).first().email
    print (email)
    dialogues = getModels()['ChatBox_'].query.filter_by(username=user_name).all()
    websites = ['blank', 'READING', 'WORKPLACE', 'ABC', 'PENG', 'FOOD', 'ICC', 'NME', 'FSE', 'blank', 'vietnam' ]
    website = 'https://' + websites[int(SCHEMA)] + '-lms.herokuapp.com'
    messText = 'New message for ' + websites[int(SCHEMA)] + ' English class'
    if form.validate_on_submit():
        chat = getModels()['ChatBox_'](username = user_name, response=form.response.data, chat=form.chat.data)
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


######## Attendance //////////////////////////////////////////////
@app.route("/att_team", methods = ['GET', 'POST'])
@login_required
def att_team():

    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']

    legend = 'Attendance: ' + time.strftime('%A %b, %d %Y %H:%M')

    # check if attendance is open
    openData = getModels()['Attendance_'].query.filter_by(username='Chris').first()
    if openData:
        openCheck = openData.teamnumber
        if openCheck == 98 or openCheck == 50:  # 98 open in normal state, 50 open in midterm state - all units can be done
            form = Attend()
        elif openCheck == 99 or openCheck == 51:  # switch to late form
            form = AttendLate()
        elif openCheck == 100:   # delete all rows
            db.session.query(getModels()['Attendance_']).delete()
            db.session.commit()
            attendance = getModels()['Attendance_'](username = 'Chris',
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
    count = getModels()['Attendance_'].query.filter_by(username=current_user.username).count()
    fields = getModels()['Attendance_'].query.filter_by(username=current_user.username).first()

    # set teamnumber to be zero by default (or not Zero in the case of solo classes)
    if teamsize == 0:
        teamNumSet = current_user.id + 100
    else:
        teamNumSet = 0

    # set up team info
    users = {}
    if count == 1:
        teammates = getModels()['Attendance_'].query.filter_by(teamnumber=fields.teamnumber).all()
        for teammate in teammates:
            image = User.query.filter_by(username=teammate.username).first().image_file
            users[teammate.username] = [teammate.username, S3_LOCATION + image]
    else:
        users = None

    # prepare initial form
    if count == 0:
        if form.validate_on_submit():
            # check last id for AttendLog
            lastID = getModels()['AttendLog_'].query.order_by(desc(getModels()['AttendLog_'].id)).first().id
            # team maker
            attendance = getModels()['Attendance_'](username = form.name.data,
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
            attendLog = getModels()['AttendLog_'](
                username = form.name.data,
                attend=form.attend.data,teamnumber=form.teamnumber.data,
                studentID=form.studentID.data, attScore=attScore,
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
            count = getModels()['Attendance_'].query.filter_by(teamnumber=i).count()
            if count:
                teamDict[i] = count
            else:
                teamDict[i] = 0
        print (teamDict)

        # check the last team is full eg team 12 == 4 students
        if teamDict[teamcount] == teamsize:
            countField = getModels()['Attendance_'].query.filter_by(username='Chris').first()
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
                    tn = key+1
                    fields.teamnumber = tn
                    try:
                        print('TRY ATTLOG')
                        logs = getModels()['AttendLog_'].query.filter_by(username=current_user.username).all()
                        logID = []
                        for log in logs:
                            logID.append(log.id)
                        update = getModels()['AttendLog_'].query.filter_by(id=max(logID)).first()
                        update.teamnumber = tn
                    except:
                        print("ATTLOG FAIL")


                    db.session.commit()
                    flash('Your attendance has been recorded', 'info')
                    return redirect(url_for('att_team'))
                else:
                    pass

    return render_template('instructor/att_team.html', legend=legend, count=count, fields=fields,
    teamcount=teamcount, form=form, notice=notice, users=users)


@app.route('/studentAdd', methods=['POST'])
def studentAdd():
    if current_user.id != 1:
        return abort(403)



    SCHEMA = getSchema()

    courseCode = schemaList[SCHEMA]['courseCode']

    with open("static/ids.json", "r") as f:
        idDict = json.load(f)

    # idDict  = idList2

    IDLIST = idDict[courseCode]

    actionID = request.form ['id']
    print(actionID)

    if actionID == '100000000':
        print('cannot change instructor marker')
        return abort(403)


    marks = {}

    parent = User.query.filter_by(username='Chris').first()

    if parent.device == '"{}"':
        for idNum in IDLIST:
            marks[idNum] = 0
            # marks['100000000'] = 0
    else:
        marks = json.loads(parent.device)

    print(marks)

    if actionID not in marks:
        marks[actionID] = 0

    if marks[actionID] == 0:
        marks[actionID] = 1

    elif marks[actionID] == 1:
        marks[actionID] = 2

    elif marks[actionID] == 2:
        marks[actionID] = 0

    try:
        print('UPDATE STUDENT ACTION', User.query.filter_by(studentID=actionID).first())
        if User.query.filter_by(studentID=actionID).first():
            User.query.filter_by(studentID=actionID).first().extra = marks[actionID]
            db.session.commit()
    except:
        print('UPDATE STUDENT EXTRA FAILED')


    parent.device = json.dumps(marks)
    db.session.commit()

    return jsonify({'marks' : json.dumps(marks)})
