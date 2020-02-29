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
unitDict = {
        'ND' : U011U, 
        'CV' : U012U, 
        'RR' : U013U,         
    }  


def get_food_projects():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    sDict = json.loads(file_content)  # json loads returns a dictionary       
    print(sDict)
    return sDict


@app.route ("/food_list", methods=['GET','POST'])
@login_required
def food_list(): 

    sDict = get_food_projects() 
    source = sDict['1']['M2']     
        
    return render_template('food/food_list.html', legend='Food Projects', source=source)

@app.route ("/food/<string:proj>", methods=['GET','POST'])
@login_required
def food_proj(proj):
    
    project = unitDict[proj].query.filter_by(username=current_user.username).first()
    if project:
        pass
    else:
        start = project(username=current_user.username, Ans01=str({}), Grade=0)
        db.session.add(start)
        db.session.commit()
        project = unitDict[proj].query.filter_by(username=current_user.username).first()
    
    ansDict = json.loads(project.Ans01)

    
    ND_Dict = {
            'dish' : None, 
            'question' : None, 
            'answer' : None, 
            'writer' : None 
        }    
    
    
    return render_template('abc/abc_qna.html', legend='Questions & Answers', 
    meta=meta, 
    teamMembers=teamMembers,
    ansDict=ansDict,
    testDict=str(json.dumps(testDict))
    )






