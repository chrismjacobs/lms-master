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


def putData():

    students = {}

    for user in User.query.all():
        students[user.username] = user.studentID

    with open('student.json', 'r') as json_file:
        sDict = json.load(json_file)

    sDict.update(students)

    print(len(sDict))

    with open('student.json', 'w') as json_file:
        json.dump(sDict, json_file)



def get_schedule():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    SOURCES = json.loads(file_content)  # json loads returns a dictionary
    #print(SOURCES)
    return (SOURCES)


@app.route ("/about")
def about():
    ## src explaining this course
    srcs = get_schedule()
    intro = srcs['1']['M1']
    return render_template('instructor/about.html', intro=intro, SCHEMA=SCHEMA)


@app.route("/course", methods = ['GET', 'POST'])
@login_required
def course():
    # json dumps returns a string
    course = json.dumps(get_schedule())
    color = json.dumps(DESIGN)

    return render_template('instructor/course.html', course=course, color=color)


@app.route ("/att_log", methods = ['GET', 'POST'])
@login_required
def att_log():
    if current_user.id != 1:
        return abort(403)

    IDLIST = BaseConfig.IDLIST

    ## create a list of all course dates
    course_dates = get_schedule()
    print(course_dates)
    dateList = []
    for c in course_dates:
        print(c)
        ### special set up for the Food calendar
        if SCHEMA == 10:
            date_string1 = course_dates[c]['Wed']
            dateList.append(date_string1)
            date_string2 = course_dates[c]['Thurs']
            dateList.append(date_string2)
        else:
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
    logs = AttendLog.query.all()
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
    mods = Info.ass_mods_dict
    studentAns = mods[unit].query.filter_by(username=name).first()

    studentAns.Comment = newComment
    db.session.commit()

    return jsonify({'comment' : newComment})


@app.route ("/dashboard")
@login_required
def dashboard():
    if current_user.id != 1:
        return abort(403)

    ## intro edit
    if SCHEMA == 6:
        midterm = ['01', '02', '03', '04', '05']
        final = ['06', '07', '08', '09', '10']
    else:
        midterm = ['01', '02', '03', '04']
        final = ['05', '06', '07', '08']

    # final = ['05', '06', '07', '08']

    period = midterm

    totalDict = {}
    allStudents = User.query.all()
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
        model = Info.ass_mods_dict[unit]
        answers = model.query.order_by(desc(model.Grade)).all()
        for item in answers:
            totalDict[item.username][unit] = {
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

    return render_template('instructor/dashboard.html', ansString=json.dumps(totalDict), title='dashboard')


@app.route("/refreshAttend", methods = ['POST'])
def get_attend_list():
    if current_user.id != 1:
        return abort(403)

    sDict = {}
    IDLIST = BaseConfig.IDLIST
    for s in IDLIST:
        sDict[s] = {
                'nme' : None,
                'img' : None,
                'eml' : None,
                'att' : 'Unregistered',
            }

    students = User.query.order_by(asc(User.studentID)).all()
    for student in students:
        if student.studentID not in IDLIST:
            print (student.studentID)
            sDict[student.studentID] = {
                'nme' : None,
                'img' : None,
                'eml' : None,
                'att' : 'Unregistered',
            }
        print(student.username)
        sDict[student.studentID]['nme'] = student.username
        print(sDict[student.studentID]['nme'])
        sDict[student.studentID]['img'] = S3_LOCATION + student.image_file
        sDict[student.studentID]['eml'] = student.email
        sDict[student.studentID]['att'] = 'Absent'

    #### attend todays attendance
    attendance = Attendance.query.all()
    for att in attendance:
        sDict[att.studentID]['att'] = att.attend

    if request.method == 'POST':
        return jsonify({'attString' : json.dumps(sDict) })
    else:
        return json.dumps(sDict)


@app.route("/refreshTeams", methods = ['POST'])
def get_team_list():
    instructor = Attendance.query.filter_by(username='Chris').first()

    if instructor.teamcount:
        teamcount = instructor.teamcount
    else:
        teamcount = 0

    if teamcount > 0:
        attDict = {}  #  teamnumber = fields, 1,2,3,4 names
        for i in range(1, teamcount+1):
            teamCall = Attendance.query.filter_by(teamnumber=i).all()
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



@app.route ("/controls")
@login_required
def controls():

    attend_list = get_attend_list()
    team_list = get_team_list()

    openData = Attendance.query.filter_by(username='Chris').first()

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

    openData = Attendance.query.filter_by(username='Chris').first()

    if int(set_mode) == 100:
        db.session.query(Attendance).delete()
        db.session.commit()
        attendance = Attendance(username = 'Chris',
        attend='Notice', teamnumber=97, studentID='100000000')
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
    from flask_mail import Message
    if current_user.id != 1:
        return abort(403)
    form = Chat()
    email = User.query.filter_by(username=user_name).first().email
    print (email)
    dialogues = ChatBox.query.filter_by(username=user_name).all()
    websites = ['blank', 'READING', 'WORKPLACE', 'ABC', 'PENG', 'FOOD', 'ICC', 'NME', 'FSE' ]
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