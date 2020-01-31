import sys, boto3, random, os, json, ast
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
SOURCES = BaseConfig.SOURCES
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN


def loadAWS():
    jList = [
        [None, None],
        ['reading-lms', "profiles/GradesFRD.json"],
        ['workplace-lms', "profiles/GradesWPE.json"],
        ['icc-lms', "profiles/GradesICC.json"]
    ]   
    content_object = s3_resource.Object(
        jList[int(SCHEMA)][0],
        jList[int(SCHEMA)][1]
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
    
   

    return render_template('instructor/exams.html', title='exams', reviewList=reviewList, bonusList=bonusList, displayDict=displayDict, SCHEMA=SCHEMA)


def loadExam():
    gradesList = [
    [None, None],
    ['reading-lms', "profiles/GradesFRD.json"],
    ['workplace-lms', "profiles/GradesWPE.json"],
    ['icc-lms', "profiles/GradesICC.json"]
    ]
    
    content_object = s3_resource.Object(
        gradesList[int(SCHEMA)][0],
        gradesList[int(SCHEMA)][1]
    )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    jload = json.loads(file_content)
    return jload

@app.route("/MTGrades", methods = ['GET', 'POST'])
@login_required
def MTGrades():
    finalGrades = loadExam()
     
    pprint(finalGrades)
    
    finalDict = {}

    scoringDict = {
        1 : [32, 8, 28 , 30], 
        2 : [32, 8, 39 , 35],
        3 : [34, 12, 30 , 25]
    }
    sc = scoringDict[int(SCHEMA)]
    
    
    for student in finalGrades:
        NAME = finalGrades[student]['NAME']
        MT = int(finalGrades[student]['MT'])/2
        partRaw = (   int(finalGrades[student]['PART'])    /sc[0]   )*15
        PART = round(partRaw,1)
        ASSN = (   int(finalGrades[student]['ASSN'])    /sc[1]   )*15 
        E1 = str(finalGrades[student]['E1']).split('/')[0] 
        E2 = str(finalGrades[student]['E2']).split('/')[0]       
        B = finalGrades[student]['B']
        TRIES = [len(finalGrades[student]['P1']),len(finalGrades[student]['P2'])]
        ATT = 0     
        EXAMdec = (int(E1) / sc[2])*10 + (int(E2) / sc[3])*10 
        EXAM = round(EXAMdec, 1)
        TOTAL = MT + PART + ASSN + EXAM + B*2

        finalDict[int(student)] = [TOTAL, NAME, MT, PART, ASSN, EXAM, E1, E2, TRIES, ATT, B]

    print (finalDict)
        
    return render_template('instructor/midGrades.html', title='MTGrades', midGrades=finalGrades, mtDict=finalDict)


