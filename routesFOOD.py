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


def get_food_projects():
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')    
    sDict = json.loads(file_content)  # json loads returns a dictionary       
    ##print(sDict)
    return sDict


@app.route ("/food_list", methods=['GET','POST'])
@login_required
def food_list(): 

    sDict = get_food_projects() 
    source = sDict['1']['M2']     
        
    return render_template('food/food_list.html', legend='Food Projects', source=source)


def get_all_values(nested_dictionary):
    detected = 0
    for key, value in nested_dictionary.items():        
        if type(value) is dict:
            #print ('DICT FOUND', value)
            if get_all_values(value) != None:
                detected += get_all_values(value)
        else:
            if value == None:
                #print(key, value)
                detected += 1
                
    return detected 

@app.route('/updateFood', methods=['POST'])
def updateFood():  
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
    if proj == 'ND':
        project_answers.Ans01 = ansOBJ 
    if proj == 'CV':
        project_answers.Ans02 = ansOBJ 
       
    project_answers.Grade = grade 
    db.session.commit()   
    
    return jsonify({'grade' : grade})

@app.route('/createPPT', methods=['POST'])
def createPPT():  
    proj = request.form ['proj']
    ansOBJ = request.form ['ansOBJ']

    ansDict = json.loads(ansOBJ)

    if proj == 'ND':
        head = 'National Dish'
    if proj == 'CV':
        head = 'Cooking Video'
    
    if get_all_values(ansDict) != None: 
        return jsonify({'error' : None})    

    from pptx import Presentation

    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Hello, World!"
    subtitle.text = "python-pptx was here!"



    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = head + ': ' + ansDict['Dish']
    
    tf = body_shape.text_frame
    tf.text = 'Reasons'
    for r in ansDict['Reasons']:
        p = tf.add_paragraph()
        p.text = ansDict['Reasons'][r]
        p.level = 1

    count = 1
    for p in ansDict['Parts']:
        bullet_slide_layout = prs.slide_layouts[count + 1]
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        title_shape.text = 'Reason ' + count
        
        tf = body_shape.text_frame
        tf.text = ansDict['Reaons'][p]
        for r in ansDict['Parts'][p]:
            p = tf.add_paragraph()
            p.text = ansDict['Parts'][p][r]
            p.level = 1
        
        count +=1
    

    bullet_slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = 'Final Comment'

    filename = current_user.username + proj + '.pptx'
    aws_filename = 'MT/' + filename
    pptLink = S3_LOCATION + aws_filename
    
    prs.save(filename)   
      
    
    
    return jsonify({'pptLink' : pptLink})


@app.route ("/food/<string:proj>", methods=['GET','POST'])
@login_required
def food_proj(proj):
    print(proj)
    sDict = get_food_projects()
    if proj == 'ND':
        title = 'National Dish'
        source = sDict['1']['M3']  
    elif proj == 'CV':
        source = sDict['1']['M4']
        title = 'Cooking Video'  

    
    if U011U.query.filter_by(username=current_user.username).first():
        pass
    else:
        startDict = {
            'Dish' : None,             
            'Link' : 'Video Link',             
            'Image' : 'Image Link',
            'Final' : None,             
            'Intro' : None,             
            'Writer' : None, 
            'Reasons' : {
                1 : None, 
                2 : None, 
                3 : None
            },
            'Parts' : { 
                1 : {
                    'kw' : {
                        1 : None,
                        2 : None,
                        3 : None,
                    },
                    'dt' : {
                        1 : None,
                        2 : None,
                        3 : None,
                    },
                },
                2 : {
                    'kw' : {
                        1 : None,
                        2 : None,
                        3 : None,
                    },
                    'dt' : {
                        1 : None,
                        2 : None,
                        3 : None,
                    },
                },
                3 : {
                    'kw' : {
                        1 : None,
                        2 : None,
                        3 : None,
                    },
                    'dt' : {
                        1 : None,
                        2 : None,
                        3 : None,
                    },
                },
            }
        }
        start = U011U(username=current_user.username, Ans01=json.dumps(startDict), Ans02=json.dumps(startDict), Grade=0)
        db.session.add(start)
        db.session.commit()

    project = U011U.query.filter_by(username=current_user.username).first() 
    if proj == 'ND':
        ansDict = project.Ans01
    if proj == 'CV':
        ansDict = project.Ans02
    
    
    return render_template('food/food_proj.html', legend='Food Project', 
    source=source,     
    title=title,         
    ansString=ansDict,
    )



@app.route ("/food_MT", methods=['GET','POST'])
@login_required
def food_MT(): 

    users = User.query.all()

    mtDict = {}
    for user in users:
        mtDict[user.username] = {
            'Dish' : None,
            'Project' : None,
            'Grade' : None,
        }
    
    project_answers = U011U.query.all()

    for answer in project_answers:
        ndDict = json.loads(answer.Ans01)
        cvDict = json.loads(answer.Ans02)
        print(get_all_values(ndDict))
        print(get_all_values(cvDict))        
        
        if get_all_values(ndDict) < get_all_values(cvDict):
            project_result = 'National Dish'
            dish = ndDict['Dish']
        elif get_all_values(ndDict) > get_all_values(cvDict):
            project_result = 'Cooking Video'
            dish = cvDict['Dish']
        else: 
            project_result = 'Unknown'
            dish = 'Unknown'


        mtDict[answer.username]['Dish'] = dish
        mtDict[answer.username]['Project'] = project_result
        mtDict[answer.username]['Grade'] = answer.Grade
    
    pprint(mtDict)   
        
    return 'Done'





