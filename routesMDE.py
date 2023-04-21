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
from routesGet import getUsers
from random import shuffle

from meta import *
s3_resource = BaseConfig.s3_resource
s3_client = BaseConfig.s3_client

'''
NOTES for next time - make movie teams at the beginning and keep it the same number and team names

'''


def create_folder(unit, teamnumber, nameRange):

    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']

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

'''### movies '''

mDict = {
        1 : 'The Lion King',
        2 : 'Gifted',
        3 : 'Jobs',
        4 : 'Intern',
        5 : 'Finding Nemo',
        6 : 'undecided',
        7 : ' new project.....'
    }

## this is the old list numbered as such
mDict2 = {
        1 : 'The Lion King',
        2 : 'Gifted',
        3 : 'Jobs',
        4 : 'Intern',
        5 : 'Finding Nemo',
        6 : 'Wonder',
        7: 'Thor',
        8: 'Moana',
        9: 'Devil Wears Prada',
        21: 'The Intern (2/3)',
        22: 'Paw Patrol (3)',
        23: 'Toy Story (3)',
        24: 'Sponge Bob (3)',
        25: 'Zootopia (2)',
        26: 'Aladdin (2)',
        27: 'Zootopia  (2)',
        28: 'Frozen (2)',
        29: 'Wreck it Ralph (2)',
        30: 'Sponge Bob (2)',
        31: 'Brave (2)',
        32: 'Friends (2)',
        33: 'Despicable Me (2)'
    }


def getTable(movie):

    SCHEMA = getSchema()
    models = modDictUnits_VTM
    if SCHEMA == 6:
         models = modDictUnits_VTM

    ## list of tables for previous movies
    tableDict = {
        # 0 : models['00'][1],
        ### 0 is set for instructor
        1 : models['01'][1],
        2 : models['01'][2],
        3 : models['01'][3],
        4 : models['01'][4],
        5 : models['02'][1],
        6 : models['02'][2],
        ### first 6 movies are pre prepared
        ## following movies are made by teams

        7 : models['03'][1],
        8 : models['03'][2],
        9 : models['03'][3],
        10 : models['03'][4],
        11 : models['04'][1],
        12 : models['04'][2],
        13 : models['04'][3],
        14 : models['04'][4],
        15 : models['05'][1],
        16 : models['05'][2],
        17 : models['05'][3],
        18 : models['05'][4],
        19 : models['05'][1],
        20 : models['05'][2],
        21 : models['05'][3],
        22 : models['05'][4],
    }

    if not movie:
        return tableDict
    else:
        return tableDict[int(movie)]


def getStudentDict():
    studentDict = {}

    for movie in mDict:
        studentDict[movie] = -1
        entries = getTable(movie).query.all()
        for a in entries:
            if a.username == 'payload':
                print(a)
            else:
                movieData = json.loads(a.Ans01)
                for name in movieData['names']:
                    print(name)
                    if name == current_user.username:
                        try:
                            studentDict[movie] = movieData['status']
                        except:
                            studentDict[movie] = 4
    return studentDict


def getTeam():

    SCHEMA = getSchema()
    teamDict = {}

    if SCHEMA == 6 or SCHEMA == 7:
        teamDict = {
            0:["Chris", "Test", None],
            7:["Cyan Huang", "Iris", "Bris"],
            8:["Jelf", "Mioly", "Layla", "Helen"],
            9:["Jasper", "Fay", "Luna"],
            10:["Kaylin", "Leon", "June", "Evelyn"],
            11:["Jessy", "Sunny", "Gwen", "Xavia"],
            12:["Anita", "Bly", "T.Y"],
            13:["Clyde", "James", "Maris"],
            14:["Wendychen2001", "Frederick", "Holly", "Cris"],
            15:["Laura", "Mac", "Beatrix", "Yuri"],
            16:["Sean Chen", "Vivién"],
            17:["Ray Chen", "Terry", "Lisa"],
            18:["Tony", "Frank", "Star Yellow"],
            19:["Johnny", "Steven", "Jarry"],
            20:["Andyyy", "Chi", "Cindy"],
            21:["Sharon Xu", "Mandy Yao", "Stephanie"],
            22:["Veronica", "Coco", "Serena"],
            23:["Ken", "Jenny", "Yanling"]
        }

    names = []
    for user in getUsers(SCHEMA):
        names.append(user.username)
    print('names', names)

    for x in teamDict:
        # print(teamDict[x])
        # for name in teamDict[x]:
        #     if name not in names:
        #         print('NOT PRESENT', name)
        #     else:
        #         print('Present', name)
        if current_user.username in teamDict[x]:
            return [x, teamDict[x]]


'''get all dubbing recordings'''
def getDubs():
    all_objects = s3_client.list_objects(Bucket = 'nme-lms')
    print(type(all_objects['Contents']))

    for x in all_objects['Contents']:
        if x['Key'][0] == 'd':  ## in 'dubbing' folder
            print(x['Key'])


def getPayloads():

    static = "static\\example_data\\"
    static = "static/"

    with open(static + 'NME_payload'  + '.json', 'r', encoding='utf8', errors='ignore') as json_file:
        payloadDict = json.load(json_file)

    # print('PAYLOAD DICT', payloadDict)

    return payloadDict




@app.route ("/nme_dubdash/<int:project>", methods=['GET','POST'])
@login_required
def nme_dubdash(project):
    taList = ['Chris']

    if current_user.username not in taList:
        return redirect('home')

    nmeDict = {}

    payloadjson = get_movieDict() # get payload from json file

    payloadDict = {}


    #get all movies in models
    movies = []
    movieUnits = getModels()['Units_'].query.all()
    for m in movieUnits:
        movies.append(m.unit)

    movieDict = getTable(None)

    for mov in movieDict:
        if int(mov) <= 6:
            print(mov, type(mov))
            ## first 6 movies are from josn file; others are from saved student work
            payloadDict[mov] = payloadjson[str(mov)]
        if mov in movieDict: # str(mov) in movies (see above)
            data = movieDict[mov].query.all()
            print('DATA', data)
            nmeDict[mov] = {}
            for entry in data:
                if entry.username == 'payload':
                    payloadDict[mov] = json.loads(entry.Ans01)
                else:
                    movieData = json.loads(entry.Ans01)
                    nmeDict[mov][movieData['team']] = movieData

    pprint (nmeDict)

    return render_template('nme/nme_dubdash.html', legend='NME Dash', project = project, nmeString = json.dumps(nmeDict), payString = json.dumps(payloadDict), movies=json.dumps(movies) )



@app.route ("/nme_dubs_sample", methods=['GET','POST'])
def nme_dubs_sample():

    # getDubs()

    static = "static\\example_data\\"
    static = "static/"

    with open(static + 'NME_dict'  + '.json', 'r', encoding='utf8') as json_file:
        nmeDict = json.load(json_file)

    with open(static + 'NME_examples'  + '.json', 'r', encoding='utf8') as json_file:
        nmeExamples = json.load(json_file)

    payloadDict = getPayloads()


    return render_template('nme/nme_dubs.html', legend='NME Dubs', nmeString = json.dumps(nmeExamples), payString = json.dumps(payloadDict), schema=getSchema(), mode='examples')


def get_movieDict():
    movieDict = {}

    static = "static\\example_data\\"
    static = "static/"
    with open(static + 'NME_payload'  + '.json', 'r', encoding='utf8', errors='ignore') as json_file:
        movieDict = json.load(json_file)

    return movieDict


@app.route ("/nme_dubs", methods=['GET','POST'])
@login_required
def nme_dubs():

    nmeDict = {}

    payloadDict = {}

    movies = []
    movieUnits = getModels()['Units_'].query.all()
    for m in movieUnits:
        movies.append(str(m.unit))

    print(movies)

    movieDict = get_movieDict() # get payload from json file

    for mov in movieDict:
        print('Mov in MovieDict', mov)
        if str(mov) in movies:
            data = getTable(mov).query.all()
            print('DATA', data)
            nmeDict[mov] = {}
            payloadDict[mov] = movieDict[mov]
            for entry in data:
                # if entry.username == 'payload':
                #     payloadDict[mov] = json.loads(entry.Ans01)
                # else:
                movieData = json.loads(entry.Ans01)
                nmeDict[mov][movieData['team']] = movieData

    pprint (nmeDict)

    # with open('NME_payload' + '.json', 'w') as json_file:
    #      json.dump(payloadDict, json_file)

    return render_template('nme/nme_dubs.html', legend='NME Dubs', nmeString = json.dumps(nmeDict), payString = json.dumps(payloadDict), schema=getSchema(), mode='dubs')

@app.route ("/nme_movies", methods=['GET','POST'])
@login_required
def nme_movies():

    users = getUsers(getSchema())

    mString = json.dumps(mDict)
    sString = json.dumps(getStudentDict())

    check = getModels()['Units_'].query.all()

    movies = {}

    for u in check:
        movies[u.unit] = u.u1

    movies=json.dumps(movies)

    return render_template('nme/nme_movies.html', mString=mString, sString=sString, legend='NME Movies', movies=movies)



@app.route("/nme_mov/<string:movie>/<string:part>", methods = ['GET', 'POST'])
@login_required
def nme_mov(movie, part):
    ## part 1-4 (not sure what part 5 is necessary for)
    team = getTeam()

    check = getModels()['Units_'].query.filter_by(unit=movie).first()

    # if current_user.username != 'Chris':
    #     flash('Not open yet', 'danger')
    #     return (redirect (url_for('nme_movies')))

    sDict = getStudentDict()
    print('sDict', sDict)
    print('sDict',  sDict[int(movie)])

    print('CHECK', check.u1)

    # team = int(current_user.extra)
    # movieList = [1,2,3,4,5,6,7,8,9,12,11,25,21,22,25,26,27,29,31]


    if current_user.username == 'Chris':
        pass
    elif check and int(check.u1) == 0:
        flash('Not open yet', 'danger')
        return (redirect (url_for('nme_movies')))
    elif int(movie) not in mDict:
        flash('Not in movie list yet', 'danger')
        return (redirect (url_for('nme_movies')))
    elif int(part) > sDict[int(movie)] + 1:
        flash('First finish earlier parts', 'danger')
        return (redirect (url_for('nme_movies')))


    payloadString = getPayloads()[str(movie)]


    print(movie)
    entries = getTable(int(movie)).query.all()

    model = None
    for a in entries:
        if a.username == 'payload':
            print(a)
        else:
            movieData = json.loads(a.Ans01)
            for name in movieData['names']:
                print(name)
                if name == current_user.username:
                    model = a
    if model:
        movieData = model.Ans01
    else:
        movieData = json.dumps({})

    uString = json.dumps({})
    if int(part) == 0:
        users = User.query.all()
        uList = ['Chris']
        # uList = []
        for user in users:
            if user.username != 'Chris':
                uList.append(user.username)
        uString=json.dumps(uList)
        print(uString)


    return render_template('nme/nme_mov' + part + '.html', uString=uString, mString=json.dumps(payloadString), mData=movieData, team=team[0], members=json.dumps(team[1]))


@app.route("/nme_project/", methods = ['GET', 'POST'])
@login_required
def nme_project():

    team = getTeam()[0]

    project = getTable(int(team)).query.filter_by(username='payload').first()
    print(project)

    if not project:
        print('not')
        dictionary = getMovieDict(team)
        newProject = getTable(int(team))(username='payload', Ans01=dictionary)
        db.session.add(newProject)
        db.session.commit()
    else:
        dictionary = project.Ans01

    return render_template('nme/nme_project.html', mData=dictionary, team=team)


## API FUNCTIONS

def getMovieDict(team):
    selection = {
          'title': '',
          'trailer': 'https://nme-lms.s3-ap-northeast-1.amazonaws.com/dubbing/' + str(team) + '-0.mp4',
          'intro': '',
          'q01': '',
          'q02': '',
          'clip': 'https://nme-lms.s3-ap-northeast-1.amazonaws.com/dubbing/' + str(team) + '-1.mp4',
          'description': '',
          'q11':'',
          'q12':'',
          'q21':'',
          'q22':'',
          'q23':'',
          'subtitles': 'https://nme-lms.s3-ap-northeast-1.amazonaws.com/dubbing/' + str(team) + '-2.mp4',
          'script': {
                1: '',
                2: '',
                3: '',
                4: '',
                5: '',
                6: '',
                7: '',
                8: '',
                9: '',
                10: '',
                11: '',
                12: '',
                13: '',
                14: '',
                15: '',
                16: '',
                17: '',
                18: '',
                19: '',
                20: '',
                21: '',
                22: '',
          },
          'vocab': {
              1: { 'v':'',
                   'q' : ''
              },
              2: { 'v':'',
                   'q' : ''
              },
              3: { 'v':'',
                   'q' : ''
              },
          }
        }

    return json.dumps(selection)



@app.route('/dubUpload', methods=['POST', 'GET'])
def dubUpload(audio_string, team, movie, device):

    SCHEMA = getSchema()
    S3_LOCATION = schemaList[SCHEMA]['S3_LOCATION']
    S3_BUCKET_NAME = schemaList[SCHEMA]['S3_BUCKET_NAME']


    title = str(movie) + '-' + str(team)
    print('PROCESSING AUDIO')
    print(audio_string[0:10])
    seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
    audio = base64.b64decode(audio_string)
    filename = 'dubbing/' + movie + '/' + team + '_' + device + random.choice(seq) +  '.mp3'
    link = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)


    return link

@app.route('/addProject', methods=['POST', 'GET'])
def addProject():

    team = request.form ['team']
    data = request.form ['movieData']
    print(data)

    movieData = json.loads(data)

    model = getTable(int(team))
    payload = model.query.filter_by(username="payload").first()
    payload.Ans01 = data
    db.session.commit()



    return jsonify({'result' : True })


@app.route('/addMovie', methods=['POST', 'GET'])
def addMovie():

    audio_string = request.form ['base64']
    device = request.form ['device']
    part = request.form ['part']
    data = request.form ['movieData']
    movie = request.form ['movie']
    print(data)

    try:
        device = str(device)
    except:
        device = 'N'

    movieData = json.loads(data)
    team = movieData['team']
    names = movieData['names']
    link = 'None'

    model = getTable(int(movie))
    details = model.query.filter_by(username=json.dumps(names)).first()


    if details == None:
            addTeam = model(teamnumber=team, username=json.dumps(names), Ans01=data)
            db.session.add(addTeam)
            db.session.commit()
            details = model.query.filter_by(username=team).first()
            return jsonify({'result' : True})

    if part == '4':
        link = dubUpload(audio_string, team, movie, device)
        movieData['audio'] = link

    details.Ans01 = json.dumps(movieData)
    db.session.commit()

    return jsonify({'result' : True, 'link': link })



