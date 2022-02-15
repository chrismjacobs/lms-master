import json
from datetime import datetime
from app import app, db
from models import *
from pprint import pprint

def get_participation_jData():

    blankDict = {}

    for assignment in Info.ass_mods_dict:
        for entry in Info.ass_mods_dict[assignment].query.all():
            #print(assignment, type(assignment))
            if entry.username not in blankDict:
                blankDict[entry.username] = {}

            blankDict[entry.username][assignment] = {
                            "date": entry.date_posted.strftime("%Y-%m-%d %H:%M:%S"),
                            "user": entry.username,
                            "idNum": entry.id,
                            "A1": entry.AudioDataOne,
                            "A2": entry.AudioDataTwo,
                            "L1": entry.LengthOne,
                            "L2": entry.LengthTwo,
                            "Notes": entry.Notes,
                            "T1": entry.TextOne,
                            "T2": entry.TextTwo,
                            "G": entry.Grade,
                            "C": entry.Comment
                            }

    #pprint(blankDict)
    with open('0FRD_part1.json', 'w') as json_file:
        json.dump(blankDict, json_file)

def get_assignment_jData():

    blankDict = {}

    for assignment in Info.ass_mods_dict:
        for entry in Info.ass_mods_dict[assignment].query.all():
            #print(assignment, type(assignment))
            if entry.username not in blankDict:
                blankDict[entry.username] = {}

            blankDict[entry.username][assignment] = {
                            "date": entry.date_posted.strftime("%Y-%m-%d %H:%M:%S"),
                            "user": entry.username,
                            "idNum": entry.id,
                            "A1": entry.AudioDataOne,
                            "A2": entry.AudioDataTwo,
                            "L1": entry.LengthOne,
                            "L2": entry.LengthTwo,
                            "Notes": entry.Notes,
                            "T1": entry.TextOne,
                            "T2": entry.TextTwo,
                            "G": entry.Grade,
                            "C": entry.Comment
                            }

    #pprint(blankDict)
    with open('0FRD_assignment1.json', 'w') as json_file:
        json.dump(blankDict, json_file)

def get_peng_jData():

    blankDict = {}

    for p in U021U.query.all():
        blankDict[p.username] = json.loads(p.Ans01)


    #pprint(blankDict)
    with open('0PENG_project2.json', 'w') as json_file:
        json.dump(blankDict, json_file)


get_peng_jData()

