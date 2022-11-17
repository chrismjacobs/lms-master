import ast, json
from sqlalchemy import asc, desc
from flask_login import current_user
from pprint import pprint

from models import *

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource

def get_schedule():
    SCHEMA = getSchema()
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']
    print('S3', S3_BUCKET_NAME)
    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    SOURCES = json.loads(file_content)  # json loads returns a dictionary
    #print(SOURCES)
    return (SOURCES)


def getUsers(schema):

    if schema == 1:
        userList = User.query.filter_by(frd=2).order_by(asc(User.studentID)).all()
    if schema == 2:
        userList = User.query.filter_by(wpe=2).order_by(asc(User.studentID)).all()
    if schema == 3:
        userList = User.query.filter_by(icc=1).order_by(asc(User.studentID)).all()
    if schema == 4:
        userList = User.query.filter_by(peng=1).order_by(asc(User.studentID)).all()
    if schema == 5:
        userList = User.query.filter_by(lnc=1).order_by(asc(User.studentID)).all()
    if schema == 6 :
        userList = User.query.filter_by(vtm=1).order_by(asc(User.studentID)).all()

    print('getUsers', userList)

    return userList


def get_sources():
    SCHEMA = getSchema()
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

    content_object = s3_resource.Object( S3_BUCKET_NAME, 'json_files/sources.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    sDict = json.loads(file_content)  # json loads returns a dictionary
    unitDict = {}

    # lets put a condition to add unit 00 or not
    for week in sDict:
        print('week', week, sDict[week]['Unit'])
        try:
            if int(sDict[week]['Unit']) >= 0: ## this or condition will add unit 00 for the reading class practice
                unitNumber = sDict[week]['Unit']
                unitDict[unitNumber] = {}
                section = sDict[week]
                #unitDict[unitNumber] = sDict[week]

                unitDict[unitNumber]['Title'] = section['Title']
                unitDict[unitNumber]['Date'] = section['Date']
                unitDict[unitNumber]['Deadline'] = section['Deadline']
                unitDict[unitNumber]['Materials'] = {}
                unitDict[unitNumber]['Materials']['1'] = section['M1']
                unitDict[unitNumber]['Materials']['2'] = section['M2']
                unitDict[unitNumber]['Materials']['3'] = section['M3']
                unitDict[unitNumber]['Materials']['4'] = section['M4']
                unitDict[unitNumber]['Materials']['A'] = section['MA']

        except:
            print('get source exception', sDict[week]['Unit'])
            pass

    pprint(unitDict)

    return unitDict


def get_MTFN(t):

    SCHEMA = getSchema()
    ICC = [3,6]

    MTFN = 'MT'

    try:
        if t == 'layout':
            if getModels()['Units_'].query.filter_by(unit='02').first():
                MTFN = 'MT'
            elif getModels()['Units_'].query.filter_by(unit='06').first():
                MTFN = 'FN'
        elif t == 'grades':
            MTFN = 'MT'
            if SCHEMA in ICC:
                if getModels()['Units_'].query.filter_by(unit='06').first():
                    MTFN = 'FN'
            else:
                if getModels()['Units_'].query.filter_by(unit='05').first():
                    MTFN = 'FN'
    except:
        print('MTFN exception')
        MTFN = 'MT'


    return MTFN

# def get_mods():
#     uModsDict = getInfo()['uModsDict']
#     print('CHECK MODS', uModsDict)
#     aModsDict = getInfo()['aModsDict']
#     unit_mods_list = getInfo()['unit_mods_list']
#     ass_mods_list = getInfo()['ass_mods_list']

#     # first check is Units - won't be there until ogged in
#     if getModels()['Units_'] and getModels()['Units_'].query.filter_by(unit='00').first():
#         d1 = getInfo()['unit_mods_dict'].copy()
#         d2 = getInfo()['unit_zero_dict']
#         uModsDict = d2.update(d1)

#         d3 = getInfo()['ass_mods_dict'].copy()
#         d4 = getInfo()['ass_zero_dict']    #
#         uModsDict = d4.update(d3)

#         unit_mods_list = getInfo()['unit_zero_list']  + getInfo()['unit_mods_list']
#         ass_mods_list = getInfo()['ass_zero_list'] + getInfo()['ass_mods_list']


#     returnDict = {
#         'uModsDict' : uModsDict,
#         'aModsDict' : aModsDict,
#         'unit_mods_list' : unit_mods_list,
#         'ass_mods_list' : ass_mods_list
#     }

#     # for p in returnDict:
#     #     print("RETURN DICT", p, returnDict[p])

#     return returnDict

def get_grades(ass, unt):

    INFO = getInfo()
    SCHEMA = getSchema()


    ### set max grades
    total_units = 0
    maxU = 0
    maxA = 0
    units = getModels()['Units_'].query.all()
    for unit in units:
        total = unit.u1 + unit.u2 + unit.u3 + unit.u4
        maxU += total
        maxA += unit.uA
        total_units += 1
    maxU = maxU*2
    maxA = maxA*2

    MTFN = get_MTFN('grades')

    lessUnits = [1,2]
    moreUnits = [5,3,6]


    print('MTFN set = ', MTFN)
    # set number for counting through the lists of units and asses
    if MTFN == 'MT':
        unit_start = 0
        ass_start = 0
        unit_check = total_units*4
        ass_check = total_units
    elif MTFN == 'FN' and SCHEMA in lessUnits:
        unit_start = 16
        ass_start = 4
        unit_check = unit_start + total_units*4
        ass_check = ass_start + total_units
    elif MTFN == 'FN' and SCHEMA in moreUnits:
        unit_start = 20
        ass_start = 5
        unit_check = unit_start + total_units*4
        ass_check = ass_start + total_units
    else:
        unit_start = 0
        ass_start = 0
        unit_check = 0
        ass_check = 0


    unitGrade = 0
    unitGradRec = {}
    print ('check units: ', unt, 'maxUnits:', maxU)
    if unt == True:
        print('unit_list', INFO['unit_mods_list'])
        for model in INFO['unit_mods_list'][unit_start:unit_check]: # a list of all units (so MT will be the first 4x4=16 units)
            rows = model.query.all()
            unit = str(model).split('U')[1]
            unitGradRec[unit] = {
                'Grade' : 0,
                'Comment' : ''
            }

            for row in rows:
                names = ast.literal_eval(row.username)
                if current_user.username in names:
                    unitGrade += row.Grade
                    unitGradRec[unit] = {
                        'Grade' : row.Grade,
                        'Comment' : row.Comment
                        }
    assGrade = 0
    assGradRec = {}

    model_check = total_units
    print('model check ', model_check, ass, ass_start, ass_check)
    if ass == True:
        for model in INFO['ass_mods_list'][ass_start:ass_check]:
            unit = str(model).split('A')[1]
            rec = model.query.filter_by(username=current_user.username).first()
            if rec:
                assGrade += rec.Grade
                assGradRec[unit] = {
                    'Grade' : rec.Grade,
                    'Comment' : rec.Comment
                }
            else:
                assGradRec[unit] = {
                    'Grade' : 0,
                    'Comment' : 'Open to start...'
                }

    return {
        'unitGrade' : unitGrade,
        'assGrade' : assGrade,
        'assGradRec' :  assGradRec,
        'unitGradRec' :  unitGradRec,
        'maxU' : maxU,
        'maxA' : maxA
    }

