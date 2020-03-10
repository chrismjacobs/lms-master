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


from routesFOOD import get_all_values

def get_peng_projects():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    sDict = json.loads(file_content)  # json loads returns a dictionary       
    source = sDict['1']['M2']
    return source


@app.route ("/peng_list", methods=['GET','POST'])
@login_required
def peng_list(): 

    source = get_peng_projects() 

    if U011U.query.filter_by(username=current_user.username).first():
        pass
    else:
        startDict = {
            'Product' : None, 
            'Brand' : None, 
            'Why' : None, 
            'Image' : None,
            'Presenter' : current_user.username,
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
            
        start = U011U(username=current_user.username, Ans01=json.dumps(startDict), Grade=0, Comment='0')
        db.session.add(start)
        db.session.commit()

    project = U011U.query.filter_by(username=current_user.username).first() 
    ansDict = project.Ans01
    grade = project.Grade
    stage = project.Comment

    return render_template('peng/peng_list.html', legend='Presentation Projects', source=source, stage=stage, grade=grade)



@app.route ("/peng/<string:MTFN>/<string:page_stage>", methods=['GET','POST'])
@login_required
def peng_proj(MTFN, page_stage):    
    source = get_peng_projects()
    # midterm or final
    if MTFN == 'MT':        
        project = U011U.query.filter_by(username=current_user.username).first() 
    else:
        pass

    ansDict = project.Ans01
    grade = project.Grade
    stage = project.Comment
    

    return render_template('peng/peng_demo' + page_stage + '.html', legend='Presentation Project', 
    source=source, ansString=ansDict )




@app.route('/updatePENG', methods=['POST'])
def updatePENG():  
    proj = request.form ['proj']
    ansOBJ = request.form ['ansOBJ']
    stage = request.form ['stage']
    image_b64 = request.form ['image_b64']

    print (proj, stage)

    ansDict = json.loads(ansOBJ)   

    if image_b64:
        print('PROCESSING IMAGE')            
        image = base64.b64decode(image_b64)    
        filename = proj + '/' + current_user.username + '.png'
        imageLink = S3_LOCATION + filename
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=image)
        ansDict['Image'] = imageLink

    project_answers = U011U.query.filter_by(username=current_user.username).first() 
    ansOBJ = json.dumps(ansDict)
    project_answers.Ans01 = str(ansOBJ)
    db.session.commit()  


    ### check stage 1 
    if int(stage) == 1: 
        stage1_checklist = [
            ansDict['Product'], 
            ansDict['Brand'],  
            ansDict['Image'],  
            ansDict['Why']
            ]            
        
        if project_answers.Ans02 == '3' or int(project_answers.Comment) > 1 :
            pass 
        elif None in stage1_checklist:
            project_answers.Ans02 = 0      ## stage one grade
            project_answers.Comment = 1  ## stage
            db.session.commit()   
        else:
            project_answers.Ans02 = 3  ## stage one grade
            project_answers.Comment = 2  ## stage
            db.session.commit()       
    
    if int(stage) == 2: 
        check = 0 
        for answer in ansDict:
            if ansDict.answer == None:
                check += 1
        
        if project_answers.Ans03 == '3' or int(project_answers.Comment) > 2 :
            pass 
        elif check > 0:
            pass
        else:
            project_answers.Ans03 = 3  ## stage one grade
            project_answers.Comment = 3  ## stage
            db.session.commit()       

    return jsonify({'ansString' : str(ansOBJ), 'stage' : project_answers.Comment})



