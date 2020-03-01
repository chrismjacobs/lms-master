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

from meta import BaseConfig 
s3_client = BaseConfig.s3_client  
s3_resource = BaseConfig.s3_resource  
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN

'''
list of stages of presentation

choose product
choose transitions
choose cue card points (take form writing app)
Title
Team
Status

project page
4 questions about content
record question
write question

4 questions using vocabulary
upload picture
record answer 
write answer

Exam
create dictionary of exams
randomly assign exams to each student

listen to question - submit answers
check listen to answers - do you want to edit your answer?

'''

def get_peng_projects():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    sDict = json.loads(file_content)  # json loads returns a dictionary       
    
    return sDict


@app.route ("/peng_list", methods=['GET','POST'])
@login_required
def peng_list(): 

    sDict = get_peng_projects() 
    source = sDict['1']['M2']   
    
        
    return render_template('peng/peng_list.html', legend='Presentation Projects', source=source)


from routesFOOD import get_all_values

@app.route('/updatePENG', methods=['POST'])
def updatePENG():  
    proj = request.form ['proj']
    ansOBJ = request.form ['ansOBJ']

    ansDict = json.loads(ansOBJ)
    
    if get_all_values(ansDict) == None:        
        grade = 3
    else:
        print ('GET_ALL', get_all_values(ansDict))
        grade = 0 
       

    print('GRADE', grade)     

    project_answers = U011U.query.filter_by(username=current_user.username).first() 
    project_answers.Ans01 = ansOBJ 
    project_answers.Grade = grade 
    db.session.commit()   
    
    return jsonify({'grade' : grade})

@app.route ("/peng/<string:proj>", methods=['GET','POST'])
@login_required
def peng_proj(proj):
    print(proj)
    sDict = get_peng_projects()
    source = sDict['1']['M2']
    print(source)
    source = None 
        
    if U011U.query.filter_by(username=current_user.username).first():
        pass
    else:
        startDict = {
            'Product' : None, 
            'Image' : None,
            'Intro' : {
                1 : None, 
                2 : None, 
                3 : None
                },            
            'Parts' : {                
                'Product' : {
                1 : None, 
                2 : None, 
                3 : None
                },
                'Features' : {
                1 : None, 
                2 : None, 
                3 : None
                },
                'Demo' : {
                1 : None, 
                2 : None, 
                3 : None
                },
                'Close' : {
                1 : None, 
                2 : None, 
                3 : None
                },
            },
            'Cues' : {                
                'Product' : {
                1 : None, 
                2 : None, 
                3 : None
                },
                'Features' : {
                1 : None, 
                2 : None, 
                3 : None
                },
                'Demo' : {
                1 : None, 
                2 : None, 
                3 : None
                },
                'Close' : {
                1 : None, 
                2 : None, 
                3 : None
                },
            },
        }
            
        start = U011U(username=current_user.username, Ans01=json.dumps(startDict), Grade=0)
        db.session.add(start)
        db.session.commit()

    project = U011U.query.filter_by(username=current_user.username).first() 
    ansDict = project.Ans01

    return render_template('peng/peng_proj.html', legend='Presentation Project', 
    source=source,  
    ansString=ansDict,
    )






