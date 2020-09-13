import sys, boto3, random, base64, os, secrets, time, datetime, json
from sqlalchemy import asc, desc, func, or_
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *
from models import *
import ast
from pprint import pprint
from routesUser import get_grades, get_sources
from random import shuffle

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource
s3_client = BaseConfig.s3_client
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN
DEBUG = BaseConfig.DEBUG


projectDict = {
        '01' : U011U,
        '02' : U021U,
        '03' : U031U,
        '04' : U041U,
        '05' : U051U,
        '06' : U061U,
        '07' : U071U,
        '08' : U081U
    }

effortDict = {
        '01' : U012U,
        '02' : U022U,
        '03' : U032U,
        '04' : U042U,
        '05' : U052U,
        '06' : U062U,
        '07' : U072U,
        '08' : U082U
    }

def create_folder(unit, teamnumber, nameRange):
    keyName = (unit + '/' + teamnumber + '/')  #adding '/' makes a folder object
    print (keyName)
    try:
        # use s3_client instead of resource to use head_object or list_objects
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=keyName)
        print('Folder Located')
    except:
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=keyName)
        object = s3_resource.Object(S3_BUCKET_NAME, keyName + str(nameRange) + '.txt')
        object.put(Body='some_binary_data')
        print('Folder Created for', teamnumber, nameRange)
    else:
        print('Create_Folder_Pass')
        pass

    return keyName


'''### novels '''

@app.route ("/nme_novels", methods=['GET','POST'])
@login_required
def nme_novels():

    novels = ['01', '02', '03', '04', '05']

    completed = 0
    nCount = 0
    nDict = {}
    for n in novels:
        project = projectDict[n].query.filter_by(username=current_user.username).first()
        if project:
            nCount +=1
            nDict[n] = {}
            nDict[n]['novel'] = json.loads(project.Ans01)
            nDict[n]['sums'] = 0

            for c in json.loads(project.Ans02):
                nDict[n]['sums'] += 1
            if nDict[n]['sums'] >= int(nDict[n]['novel']['chapters']):
                completed += 1

            nDict[n]['recs'] = 0
            for c in json.loads(project.Ans03):
                nDict[n]['recs'] += 1



    nString = json.dumps(nDict)


    return render_template('nme/nme_novels.html', completed=completed, nCount=nCount, nString=nString, legend='NME Projects')

@app.route ("/addNovel", methods=['GET','POST'])
@login_required
def addNovel():
    print('ADD_NOVEL')
    novel = request.form ['novel']
    number = json.loads(novel)['number']

    PROJECT = projectDict[number]
    sums = {}
    recs = {1:{}, 2:{}, 3:{}}
    feeds = {}

    check = PROJECT.query.filter_by(username=current_user.username).first()

    if check:
        check.Ans01 = novel
        db.session.commit()
    else:
        entry = PROJECT(username=current_user.username, Ans01=novel, Ans02=json.dumps(sums), Ans03=json.dumps(recs), Ans04=json.dumps(feeds))
        db.session.add(entry)
        db.session.commit()

    return jsonify({'nValue' : novel, 'nKey':number })


'''### summaries '''

@app.route ("/sum/<string:index>", methods=['GET','POST'])
@login_required
def nme_sum(index):

    project = projectDict[index].query.filter_by(username=current_user.username).first()
    novel = json.loads(project.Ans01)
    sums = json.loads(project.Ans02)

    html = 'nme/nme_sums.html'

    return render_template(html, legend='Chapter Summaries', nString=project.Ans01, sString=project.Ans02)


@app.route ("/addSum", methods=['GET','POST'])
@login_required
def addSum():
    print('ADD_SUM')
    nString = request.form ['novel']
    cString = request.form ['chapter']

    novel = json.loads(nString)
    chapter = json.loads(cString)
    novel_number = novel['number']
    chap_number = chapter['number']

    project = projectDict[novel_number].query.filter_by(username=current_user.username).first()

    print(project, project.Ans02, novel, chapter, novel_number, chap_number)

    current_sum = json.loads(project.Ans02)
    current_sum[chap_number] = chapter
    project.Ans02 = json.dumps(current_sum)
    db.session.commit()

    return jsonify({'cObj' : json.dumps(current_sum)})

'''### feedback '''

@app.route ("/feedback/<string:student>", methods=['GET','POST'])
@login_required
def nme_feedback(student):
    if current_user.id == 1 or student == current_user.username:
        pass
    else:
        flash('Wrong Username', 'danger')
        return (redirect (url_for('home')))

    novels = ['01', '02', '03']

    completed = 0
    nCount = 0
    fDict = {}
    for n in novels:
        project = projectDict[n].query.filter_by(username=current_user.username).first()
        if project:
            nCount +=1
            fDict[n] = json.loads(project.Ans04)

    html = 'nme/nme_feedback.html'

    return render_template(html, legend='Writing Feedback', fString=json.dumps(fDict))


@app.route ("/addFeedback", methods=['GET','POST'])
@login_required
def addFeedback():
    print('ADD_FEEDBACK')
    nString = request.form ['novel']
    student = request.form ['student']

    novel = json.loads(nString)
    current_feedback = {}

    return jsonify({'fObj' : json.dumps(current_feedback)})


@app.route ("/rec/<string:index>", methods=['GET','POST'])
@login_required
def nme_recording(index):
    novels = ['01', '02', '03', '04', '05']

    rCount = 0
    rDict = {}
    for n in novels:
        project = projectDict[n].query.filter_by(username=current_user.username).first()
        if project:
            rDict = json.loads(project.Ans03)
            rCount +=1

    html = 'nme/nme_recs.html'

    return render_template(html, legend='Add Recordings', index=index, rString=json.dumps(rDict), rCount=rCount)


@app.route ("/addRec", methods=['GET','POST'])
@login_required
def addRec():
    print('ADD_REC_DETAILS')
    novel = request.form ['novel']
    rec = request.form ['rec']
    details = request.form ['details']

    project = projectDict[novel].query.filter_by(username=current_user.username).first()

    rDict = json.loads(project.Ans03)
    rDict[rec] = json.loads(details)
    project.Ans03 = json.dumps(rDict)
    db.session.commit()

    return jsonify({'details' : details})



''' ## performance '''

@app.route ("/effort", methods=['GET','POST'])
@login_required
def nme_effort():
    weeks =  ['01', '02', '03', '04', '05', '06', '07', '08']

    survey = U012U.query.filter_by(username=current_user.username).first()

    if not survey:
        obj = json.dumps({})
        entry = U012U(username=current_user.username, Ans01=obj, Ans02=obj, Ans03=obj, Ans04=obj, Ans05=obj, Ans06=obj, Ans07=obj, Ans08=obj)
        db.session.add(entry)
        db.session.commit()

    survey = U012U.query.filter_by(username=current_user.username).first()

    eDict = {}
    week = '01'
    effort1 = json.loads(survey.Ans01)
    eDict['01'] = effort1

    html = 'nme/nme_performance.html'

    return render_template(html, legend='Course Performance', week=week, eString=json.dumps(eDict))

@app.route ("/addSurvey", methods=['GET','POST'])
@login_required
def addSurvey():
    print('ADD_SURVEY')
    eString = request.form ['reflection']
    reflection = json.loads(eString)
    week = reflection['week']



    survey = U012U.query.filter_by(username=current_user.username).first()



    return jsonify({'msg' : True})


@app.route('/nme_storeB64', methods=['POST'])
def storeB64():

    b64data = request.form ['b64data']
    fileType = request.form ['fileType']
    novel = request.form ['novel']
    rec = request.form ['rec']

    project = projectDict[novel].query.filter_by(username=current_user.username).first()
    rDict = json.loads(project.Ans03)
    print(type(rec), rec)
    print(rDict)
    try:
        file_key = rDict[int(rec)]['audio']
        print('file_key_found ', file_key)
        file_key_split = file_key.split('com/')[1]
        s3_resource.Object(S3_BUCKET_NAME, file_key_split).delete()
    except:
        print('no file_key found')

    now = datetime.now()
    time = now.strftime("_%M%S")
    print("time:", time)

    print('PROCESSING AUDIO')
    audio = base64.b64decode(b64data)

    filename = current_user.username + '/' + novel + '/' + rec + time + '.mp3'
    audioLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)

    rDict[rec]['audio'] = audioLink
    project.Ans03 = json.dumps(rDict)
    db.session.commit()

    return jsonify({'audioLink' : audioLink})