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


@app.route ("/food_list", methods=['GET','POST'])
@login_required
def food_list():    
    
    srcDict = get_sources()
    #print(srcDict)
      
    return render_template('units/food_list.html', legend='Units Dashboard')





