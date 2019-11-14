import sys, boto3, random, base64, os, secrets, time, datetime, json
from sqlalchemy import asc, desc, func
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import * 
from models import * 
import ast 

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

@app.route ("/units", methods=['GET','POST'])
@login_required
def unit_list():
    
    sourceList = Sources.query.filter_by(openSet='1').order_by(asc(Sources.unit)).order_by(asc(Sources.part)).all()  # also remember .limit(3).all()     
    href = url_for('class_part') 

    unitsSet = set()
    for src in sourceList:
        unitsSet.add(int(src.unit))
    
    #temporarily close old units
    # check today's unit
    attendance = Attendance.query.filter_by(username='Chris').first()
    if attendance:
        todaysUnit = attendance.unit
        attStatus = attendance.teamnumber
        print (attStatus)
    else: 
        todaysUnit = 0
        attStatus = 0

    if attStatus > 97:     
        print ('todaysUnit', todaysUnit)
        for sourceLine in sourceList:
            print('a', sourceLine.unit , 'b', todaysUnit)
            if sourceLine.openSet == 1:
                try:
                    int(todaysUnit)
                except:
                    break                    
                if sourceLine.unit != todaysUnit:
                    sourceLine.openReset = 100
                    sourceLine.openSet = 2
                    db.session.commit() 
    elif attStatus == 50:
        pass 
    else:
        #return to normal state after attendence closed
        for sourceLine in sourceList:
            if sourceLine.openReset == 100:
                sourceLine.openReset = 0
                sourceLine.openSet = 1
                db.session.commit() 

    print('sourceList', sourceList) 
    # models update
    #list of models, used later to create a points dictionary
    modList = Info.modListUnits  

    #create a dictionary of scores and comments    
    scoreDict = {} # [001 : grade , comment]         
    for model in modList:          
        unitCode = (str(model).split("U"))[1] #.split remove the item "" __U001U__  -->  __  001  ___  
        if int(unitCode[:2]) not in unitsSet:           
            pass
        else: 
            rows = model.query.order_by(asc(model.id)).all()
            scoreDict[unitCode] = [0, ""]        
            for row in rows:
                # need to stop Chris being found when ChrisHsu is present in a string 
                if current_user.username + ',' in row.username or current_user.username + '"' in row.username or current_user.username + '}' in row.username or current_user.username == row.username:
                    # this code prevents scores being replaced by Zeros but Zeros will be replaced by scores                
                    if scoreDict[unitCode][0] == 2:
                        print ('pass2') 
                        pass 
                    elif scoreDict[unitCode][0] == 1:
                        if row.Grade == 2:
                            scoreDict[unitCode] = [row.Grade , row.Comment] 
                        else:                         
                            print ('pass1') 
                            pass 
                    else:                   
                        scoreDict[unitCode] = [row.Grade , row.Comment] 
        
    
    print('scoreDict: ', scoreDict)

    
    # count points based on grade for all models and update Grades    
    pointCounter = 0 
    for score in scoreDict:
        try:
            pointCounter = pointCounter + scoreDict[score][0]
        except:
            pass
    
    fieldsGrade = Grades.query.filter_by(username=current_user.username).first() 
    if fieldsGrade.units == pointCounter:
        pass
    else:
        fieldsGrade.units = pointCounter
        db.session.commit()
    
    # set total based max score
    maxUni = Grades.query.order_by(desc(Grades.units)).first().units
    try:
        color = pointCounter/(maxUni)
    except:
        color = 0   

    return render_template('units/unit_list.html', legend='Units Dashboard', 
    sourceList=sourceList, href=href, scoreDict=scoreDict, 
    pointCounter=pointCounter, total=maxUni, color=color, title='unit_list')


@app.route ("/unit")
def class_part():
    #this will redirect to the root url    
    return url_for('class_part')

def team_details ():
    # check user has a team number
    try:
        teamnumber = Attendance.query.filter_by(username=current_user.username).first().teamnumber
        if teamnumber == 0:
            namesRange = [current_user.username]
        else:
        # confirm names of team
            names = Attendance.query.filter_by(teamnumber=teamnumber).all()
            nameRange = [student.username for student in names]             
        #for student in names:
            #nameRange.append(student.username)    
        print ('NAMES', nameRange)
    except: 
        # create a unique teamnumber for solo users
        teamnumber = current_user.id + 100
        nameRange = [current_user.username] 
        print ('Teamnumber: ', teamnumber)
    nnDict = { 'teamnumber' : teamnumber, 
                    'nameRange' : nameRange}
    return nnDict


# check the score of teams during participation
@app.route('/partCheck', methods=['POST'])
def scoreCheck():  
    qNum = request.form ['qNum']
    part_num = request.form ['part_num']
    unit_num = request.form ['unit_num']

    print (type(qNum), part_num, unit_num)

    modDict = Info.modDictUnits
    model = modDict[unit_num][int(part_num)]            
    answers = model.query.order_by(asc(model.teamnumber)).all()  

    scoreDict = {}     
    for answer in answers: 
        print (answer)
        scoreList = [answer.Ans01, answer.Ans02, answer.Ans03, answer.Ans04, 
        answer.Ans05, answer.Ans06, answer.Ans07, answer.Ans08]
        if answer.teamnumber <21:
            scoreDict[answer.teamnumber] = []
            for item in scoreList[0:int(qNum)+1]:               
                if item != "" and item != None:
                    scoreDict[answer.teamnumber].append(1)    
    print (scoreDict)    
    
    maxScore = len(scoreDict) * int(qNum)
    actScore = 0
    for key in scoreDict:
        for item in scoreDict[key]:            
            actScore += item  
    print ('max', maxScore, 'act', actScore)
        
    percentFloat = (actScore / maxScore )*100
    percent = round (percentFloat, 1)     
    
    return jsonify({'percent' : percent, 'scoreDict' : scoreDict, 'qNum' : qNum })  


@app.route ("/answers/<string:unit_num>/<string:part_num>/<string:fm>/<string:qs>", methods=['GET','POST'])
@login_required
def unit_instructor(unit_num,part_num,fm,qs):  
    if current_user.id != 1:
        return abort(403)    

    # models update
    modDict = Info.modDictUnits
    model = modDict[unit_num][int(part_num)]        
    source = Sources.query.filter_by(unit=unit_num).filter_by(part=part_num).first()            
      
    answers = model.query.all()
    ansDict = {}    
    counter = 0 
    for answer in answers:        
        ansDict[counter] = [
        answer.teamnumber,
        answer.Ans01, 
        answer.Ans02, 
        answer.Ans03,
        answer.Ans04,
        answer.Ans05,
        answer.Ans06,
        answer.Ans07,
        answer.Ans08
        ]        
        counter = counter+1    

    dictCount = len(ansDict)

    
    if Attendance.query.filter_by(username='Chris').first().teamcount:
        teamcounter = Attendance.query.filter_by(username='Chris').first().teamcount
    else: 
        teamcounter = 10

    if int(fm) == 1:
        jdata = None
        html = 'units/unit_instructor.html'
    elif int(fm) == 2:
        jdata = None
        html = 'units/unit_instructor.html'
    elif int(fm) == 3: 
        jsonList = [ 'blank', "FRD.json", "WPE.json", "ICC.json"]
        string = jsonList[int(COLOR_SCHEMA)]   
        with open (string, "r") as f:
            jload = json.load(f)             
        jdata = jload[unit_num][part_num]        
        html = 'units/unit_instructor_json.html'
        questionNum = len(jdata)
     
    context = { 
        'ansDict' : ansDict, 
        'part_num' : part_num, 
        'unit_num' : unit_num,        
        'qNumber' : questionNum, 
        'source' : source,
        'dictCount' : dictCount,        
        'title' : 'unit_IM',
        'teamcounter' : teamcounter
    }

    

    return render_template(html, **context, jdata=jdata)



@app.route ("/unit/<string:unit_num>/<string:part_num>/<string:fm>/<string:qs>", methods=['GET','POST'])
@login_required
def unit(unit_num,part_num,fm,qs):
        
    nnDict = team_details ()
    teamnumber = nnDict['teamnumber']
    nameRange = nnDict['nameRange']     

    if int(fm) == 2:
        return redirect(url_for('unit_sl', unit_num=unit_num))
    else:
        pass
    
    # models update
    modDict = Info.modDictUnits
    
    #set form  / model / No.questions / source
    forms = [
        None,
        UnitF1(),
        UnitFS(),
        UnitF1()
        ]        
    form = forms[int(fm)]
    model = modDict[unit_num][int(part_num)] 
    questionNum = int(qs)+1 # +1 because count starts at zero        
    source = Sources.query.filter_by(unit=unit_num).filter_by(part=part_num).first()

    #check source to see if unit is open yet
    if source.openSet == 1:    
        pass
    else:
        flash('This unit is not open at the moment', 'danger')
        return redirect(url_for('unit_list'))    
        
    #start unit assignment    

    mods = model.query.all()
    fields = None
    for row in mods:
        if current_user.username + ',' in row.username or current_user.username + '"' in row.username or current_user.username + '}' in row.username or current_user.username == row.username:
            fields = row
        
    print(fields)
    if fields == None: 
        response = model(username=nameRange, teamnumber=teamnumber, 
            Ans01="", Ans02="", Ans03="",  Ans04="",  Ans05="",  Ans06="",
            Ans07="", Ans08="", Grade=0, Comment=""  
            )
        db.session.add(response)
        db.session.commit()        
        return redirect(request.url)
    
      
    answers = model.query.all()  
    ansDict = {}
    counter = 0 
    for answer in answers:        
        ansDict[counter] = [
        answer.teamnumber,
        answer.Ans01, 
        answer.Ans02, 
        answer.Ans03,
        answer.Ans04,
        answer.Ans05,
        answer.Ans06,
        answer.Ans07,
        answer.Ans08
        ]
        counter = counter+1 

    dictCount = len(ansDict)    


    fieldsCount = 1
    fieldsList = [
        None,
        fields.Ans01, fields.Ans02, 
        fields.Ans03, fields.Ans04,
        fields.Ans05, fields.Ans06, 
        fields.Ans07, fields.Ans08
        ]  

    print (fieldsList)
    #fields count will tell the front end which question we are on
    for i in range(1,8):
        if fieldsList[i] != "":
            fieldsCount +=1

    if int(fm) == 1:
        jdata = None
        html = 'units/unit_layout.html'
    elif int(fm) == 2:
        jdata = None
        html = 'units/unit_layout.html'
    elif int(fm) == 3:
        #jList = [ [], ['reading-lms', "images/FRD.json"], ['workplace-lms', "images/WPE.json"], ['icc-lms', "images/ICC.json"]]
        #content_object = s3_resource.Object(jsonList[int(COLOR_SCHEMA)][0], jsonList[int(COLOR_SCHEMA)][1])
        #file_content = content_object.get()['Body'].read().decode('utf-8')
        #jload = json.loads(file_content)
        
        jsonList = [ 'blank', "FRD.json", "WPE.json", "ICC.json"]
        string = jsonList[int(COLOR_SCHEMA)]   
        with open (string, "r") as f:
            jload = json.load(f)             
        jdata = jload[unit_num][part_num]
        questionNum = len(jdata)
        html = 'units/unit_layout_json.html'        
        
    #set the grade for the assignment
    zeroCounter = []         
    for j in range(1,questionNum+1):        
        if fieldsList[j] == "":            
            zeroCounter.append(0)
        else: 
            zeroCounter.append(1)
        
    if 0 in zeroCounter:
        pass
    elif fields.Grade == 0:
        if fields.date_posted > source.duedate:            
            fields.Grade = 1            
            fields.Comment = 'This is late, be careful of deadlines'
            db.session.commit()   
        else:
            comList = ['Nice work', 'Done', 'Complete', 'Great']                     
            fields.Grade = 2
            rand_com = random.choice(comList)            
            fields.Comment = rand_com
            db.session.commit()   
    ansSum = sum(zeroCounter)
    
    
    #deal with the form
    if form.validate_on_submit():          
        fields.username = nameRange
        fields.teamnumber = teamnumber 
        if fields.Ans01 == "":
            fields.Ans01 = form.Ans01.data
        if fields.Ans02 == "":
            fields.Ans02 = form.Ans02.data
        if fields.Ans03 == "":        
            fields.Ans03 = form.Ans03.data   
        if fields.Ans04 == "":
            fields.Ans04 = form.Ans04.data 
        if fields.Ans05 == "":
            fields.Ans05 = form.Ans05.data   
        if fields.Ans06 == "":
            fields.Ans06 = form.Ans06.data
        if fields.Ans07 == "": 
            fields.Ans07 = form.Ans07.data   
        if fields.Ans08 == "":
            fields.Ans08 = form.Ans08.data        
        #fields.Grade = score
        db.session.commit()
        flash('Your answer has been recorded', 'success') 
        return redirect(request.url)
    elif request.method == 'GET':   
        form.Ans01.data = fields.Ans01
        form.Ans02.data = fields.Ans02
        form.Ans03.data = fields.Ans03
        form.Ans04.data = fields.Ans04
        form.Ans05.data = fields.Ans05
        form.Ans06.data = fields.Ans06
        form.Ans07.data = fields.Ans07
        form.Ans08.data = fields.Ans08
        
    
    

    
    context = {
        'form' : form, 
        'fields' : fields, 
        'ansDict' : ansDict, 
        'dictCount' : dictCount, 
        'fieldsList' : fieldsList,
        'fieldsCount' : str(fieldsCount),
        'formList' : [None, form.Ans01, form.Ans02, form.Ans03, form.Ans04, form.Ans05, form.Ans06, form.Ans07, form.Ans08],   
        'qNumber' : questionNum, 
        'source' : source, 
        'ansSum' : ansSum
    }    

    return render_template(html, **context, jdata=jdata)




def unit_audio(audio, unit, team, rec):    
    _ , f_ext = os.path.splitext(audio.filename) # _  replaces f_name which we don't need #f_ext  file extension 
    s3_folder = 'unit_audio/'
    audio_filename =  s3_folder + unit + 'Team' + team + '_' + rec + f_ext 
    s3_filename =  S3_LOCATION + audio_filename     
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=audio_filename, Body=audio) 
      
    return s3_filename    


@app.route('/upload/<string:unit_num>/<string:team_num>/<string:nameRange>', methods=['POST', 'GET'])
@login_required
def unit_slup(unit_num, team_num, nameRange):
    form = UnitFS()
    source = Sources.query.filter_by(unit=unit_num).filter_by(part='4').first()
    
    if form.validate_on_submit():        
        record1 = unit_audio(form.Record1.data, unit_num, team_num, '1')        
        record2 = unit_audio(form.Record2.data, unit_num, team_num, '2')
        data = U555(username=nameRange, teamnumber=team_num, unit=unit_num,
        record1=record1, answers1=form.Answers1.data,
        record2=record2, answers2=form.Answers2.data)   
        db.session.add(data)        
        db.session.commit() 
        flash('Your speaking has been added, please complete the listening.', 'success')
        return redirect(url_for('unit_sl', unit_num=unit_num))
    

        
    return render_template('units/sl_record.html', form=form, source=source)


@app.route("/partsl/<string:unit_num>", methods=['GET','POST'])
@login_required
def unit_sl(unit_num):
    form = UnitF1()
    source = Sources.query.filter_by(unit=unit_num).filter_by(part='4').first()
    
    #models update    
    modList = Info.modListSL
    model=modList[int(unit_num)]
     
    #check source to see if unit is open yet
    if source.openSet == 1:    
        pass
    else:
        flash('This unit is not open at the moment', 'danger')
        return redirect(url_for('unit_list'))    
    
    nnDict = team_details ()
    teamnumber = nnDict['teamnumber']
    nameRange = nnDict['nameRange']  
    
    lisTasks = U555.query.filter_by(unit=unit_num).all()   
    #lisList = [] 
    greenLight = False     
    for row in lisTasks:
        if current_user.username in row.username:
            greenLight = True
        else:
            #lisList.append(row)
            pass
    
    if greenLight == False:
        flash('You must complete the speaking to participate in the listening. Make sure you have a partner to proceeed.' , 'danger')
        return redirect(url_for('unit_slup', unit_num=unit_num, team_num=teamnumber, nameRange=nameRange)) 
    else:
        pass
    
    SLcount = U555.query.filter_by(unit=unit_num).count()
    if SLcount > 1:    
        try:        
            while True:
                randField = U555.query.filter_by(unit=unit_num).order_by(func.random()).first()
                if randField.teamnumber != teamnumber:
                    break 
        except:            
            return render_template('units/unit_list.html', source=source, randField=None)
    else:
        flash('Your are the first team to finish! Please wait a moment for another team to finish' , 'secondary')
        return redirect(url_for('unit_list')) 
    
    print ('RandField', randField)
    modFields = model.query.all()

    fields = None
    for mod in modFields:
        if current_user.username in mod.username:
            fields = mod            
        else:
            pass

    if form.validate_on_submit():
        data = model(username=nameRange, teamnumber=teamnumber,
        Ans01=form.Ans01.data, Ans02=form.Ans02.data,
        Ans03=randField.record1, Ans04=randField.record2,
        Ans05=randField.answers1, Ans06=randField.answers2,
        Grade=2, Comment="")        
        db.session.add(data)
        db.session.commit() 
        flash('Your listening answers have been added,', 'success')
        return redirect(request.referrer)


    context = {
        'form' : form, 
        'source' : source, 
        'randField' : randField, 
        'fields' : fields       
    }

    return render_template('units/sl_layout.html', **context)

    
    