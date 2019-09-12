import sys, boto3, random, base64, os, secrets, time, datetime
from sqlalchemy import asc, desc, func
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
except:
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME'] 
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 

@app.route ("/units", methods=['GET','POST'])
@login_required
def unit_list():
    
    unitList = Sources.query.order_by(asc(Sources.unit)).order_by(asc(Sources.part)).all()  # also remember .limit(3).all()     
    href = url_for('class_part')    
    
    
    #temporarily close old units
    # check today's unit
    unitCheck = Attendance.query.filter_by(username='Chris').first()
    
    if unitCheck:
        print ('unitcheck', unitCheck.unit)
        for unit in unitList:
            print('a', unit.unit , 'b', unitCheck.unit)
            if unit.unit == unitCheck.unit:
                
                if unit.openSet != 1:                  
                    unit.openSet = 1
                    db.session.commit()
            else:
                if unit.openSet == 0:
                    pass
                elif unit.openSet == 1:
                    # temporarily close old units during teamwork time
                    unit.openSet = 2
                    db.session.commit()
    else:
        # reset old open status when attendance has been closed
        for unit in unitList:            
            if unit.openSet == 2:
                unit.openSet = 1
                db.session.commit()
    

    # models update
    #list of models, used later to create a points dictionary
    modList = Info.modListUnits
    
    

    #create a dictionary of scores and comments
    modCount = 0
    scoreDict = {} # [001 : grade , comment]        
    for model in modList:
        rows = model.query.all()  
        unitCode = (str(model).split("U"))[1] #.split remove the item "" __U001U__  -->  __  001  ___  
        scoreDict[unitCode] = [0, ""]
        print(unitCode)
        for row in rows:
            if current_user.username in row.username:                           
                scoreDict[unitCode] = [row.Grade , row.Comment] 
        modCount += 1
        if modCount == len(unitList): # going to break the for loop once all sources have been checked 
            break
    
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
    unitList=unitList, href=href, scoreDict=scoreDict, 
    pointCounter=pointCounter, total=maxUni, color=color)


@app.route ("/unit")
def class_part():
    #this will redirect to the root url    
    return url_for('class_part')

def team_details ():
    # check user has a team number
    try:
        teamnumber = Attendance.query.filter_by(username=current_user.username).first().teamnumber
        if teamnumber == 0:
            namesRange = current_user.username 
        else:
        # confirm names of team
            names = Attendance.query.filter_by(teamnumber=teamnumber).all()   
            nameRange = []
        for student in names:
            nameRange.append(student.username)    
        print ('NAMES', nameRange)
    except: 
        # create a unique teamnumber for solo users
        teamnumber = current_user.id + 100
        nameRange = current_user.username 
        print ('Teamnumber: ', teamnumber)
    return [teamnumber, nameRange]


@app.route ("/unit/<string:unit_num>/<string:part_num>/<string:fm>/<string:qs>", methods=['GET','POST'])
@login_required
def unit(unit_num,part_num,fm,qs):
        
    teamdeets = team_details ()
    teamnumber = teamdeets[0]
    nameRange = teamdeets[1]    

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
        UnitFS()
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
    fieldsCheck = model.query.filter_by(teamnumber=teamnumber).first()  
    if fieldsCheck == None:
        response = model(username=nameRange, teamnumber=teamnumber, 
        Ans01="", 
        Ans02="", 
        Ans03="",
        Ans04="", 
        Ans05="",
        Ans06="",
        Ans07="",
        Ans08="",
        Grade=0,
        Comment=""  
        )
        db.session.add(response)
        db.session.commit()        
        return redirect(request.url)
    else: 
        fields = model.query.filter_by(teamnumber=teamnumber).first() 
      
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
    print(ansDict) 

    fieldsList = [
        None,
        fields.Ans01, fields.Ans02, 
        fields.Ans03, fields.Ans04,
        fields.Ans05, fields.Ans06, 
        fields.Ans07, fields.Ans08
        ]  
        
    #set the grade for the assignment
    zeroCounter = []         
    for j in range(1,questionNum):        
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
        'formList' : [None, form.Ans01, form.Ans02, form.Ans03, form.Ans04, form.Ans05, form.Ans06, form.Ans07, form.Ans08],   
        'qNumber' : questionNum, 
        'source' : source, 
        'ansSum' : ansSum
    }

    return render_template('units/unit_layout.html', **context)


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
    
    teamdeets = team_details()
    teamnumber = teamdeets[0]
    nameRange = teamdeets[1]
    
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

    
    