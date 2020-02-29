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



def create_food(proj): 
    keyName = (proj + '/' + current_user.username)  #adding '/' makes a folder object
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


def get_peng_projects():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    sDict = json.loads(file_content)  # json loads returns a dictionary       
    print(sDict)
    return sDict


@app.route ("/peng_list", methods=['GET','POST'])
@login_required
def peng_list(): 

    sDict = get_peng_projects() 
    source = sDict['00']['M2'] 
    
        
    return render_template('peng/peng_list.html', legend='Food Projects', source=source)







