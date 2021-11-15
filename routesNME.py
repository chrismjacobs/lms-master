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
from random import shuffle

from meta import BaseConfig
s3_resource = BaseConfig.s3_resource
s3_client = BaseConfig.s3_client
S3_LOCATION = BaseConfig.S3_LOCATION
S3_BUCKET_NAME = BaseConfig.S3_BUCKET_NAME
SCHEMA = BaseConfig.SCHEMA
DESIGN = BaseConfig.DESIGN
DEBUG = BaseConfig.DEBUG


'''
NOTES for next time - make movie teams at the beginning and keep it the same number and team names

'''

projectDict = {
        '01' : U012U,
        '02' : U022U,
        '03' : U032U
    }


def create_folder(unit, teamnumber, nameRange):
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


'''Instructor dashboard'''
@app.route ("/nme_dash", methods=['GET','POST'])
@login_required
def nme_dash():
    taList = ['Chris']

    if current_user.username not in taList:
        return redirect('home')

    #srcDict = get_projects()
    #pprint(srcDict)
    nmeDict = {}

    for proj in projectDict:
        data = projectDict[proj].query.all()
        print('DATA', data)
        nmeDict[proj] = {}
        for entry in data:
            print(entry)

            nmeDict[proj][entry.username] = {
                'novel' : json.loads(entry.Ans01),
                'sums' : json.loads(entry.Ans02),
                'recs' : json.loads(entry.Ans03),
                'c' : entry.Comment
                }

    ## pprint (nmeDict)

    return render_template('nme/nme_dash.html', legend='NME Dash', nmeString = json.dumps(nmeDict))


'''### movies '''

movieDict = {
        1: U013U, # lionking
    }

movieCache = {
        1: U013U, # lionking
        2: U014U, # gifted
        3: U023U, # jobs
        4: U024U, # intern
        5: U033U, # Ginny Amanda
        6: U034U, # Elisha, Tina, Jessica
        7: U043U, # Bobby Leo William
        8: U044U, # Tracy Judy Tiffany
        9: U053U, # Fiona Abby Winnie
        12: U054U, # Jimmy Robin
        11: U063U, # Alex Wayne Daniel
    }

mDict = {
        1 : 'The Lion King'
    }

mDictCache = {
        1 : 'The Lion King',
        2 : 'Gifted',
        3 : 'Jobs',
        4 : 'Intern',
        5 : 'Finding Nemo',
        6 : 'Wonder',
        7: 'Thor',
        8: 'Moana',
        9: 'Devil Wears Prada',
        12: 'White Chicks',
        11: 'Key and Peele'
    }


@app.route ("/nme_dubdash", methods=['GET','POST'])
@login_required
def nme_dubdash():
    taList = ['Chris']

    if current_user.username not in taList:
        return redirect('home')

    nmeDict = {}

    payloadDict = {}

    for mov in movieDict:
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

    return render_template('nme/nme_dubdash.html', legend='NME Dash', nmeString = json.dumps(nmeDict), payString = json.dumps(payloadDict) )

@app.route ("/nme_dubs_sample", methods=['GET','POST'])
def nme_dubs_sample():

    # with open('0NME_dict' + '.json', 'w') as json_file:
    #     json.dump(nmeDict, json_file)

    # with open('0NME_payload' + '.json', 'w') as json_file:
    #     json.dump(nmeDict, json_file)

    with open('0NME_dict'  + '.json', 'r') as json_file:
        nmeDict = json.load(json_file)

    with open('0NME_payload'  + '.json', 'r') as json_file:
        payloadDict = json.load(json_file)


    return render_template('nme/nme_dubs.html', legend='NME Dubs', nmeString = json.dumps(nmeDict), payString = json.dumps(payloadDict) )


@app.route ("/nme_dubs", methods=['GET','POST'])
@login_required
def nme_dubs():

    nmeDict = {}

    payloadDict = {}

    for mov in movieDict:
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

    with open('0NME_payload' + '.json', 'w') as json_file:
         json.dump(payloadDict, json_file)

    return render_template('nme/nme_dubs.html', legend='NME Dubs', nmeString = json.dumps(nmeDict), payString = json.dumps(payloadDict) )


def getStudentDict():
    studentDict = {}

    for movie in mDict:
        studentDict[movie] = -1
        entries = movieDict[int(movie)].query.all()
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


@app.route ("/nme_movies", methods=['GET','POST'])
@login_required
def nme_movies():

    users = User.query.all()

    mString = json.dumps(mDict)
    sString = json.dumps(getStudentDict())

    check = Units.query.all()

    movies = {}

    for u in check:
        movies[u.unit] = u.u1

    movies=json.dumps(movies)

    return render_template('nme/nme_movies.html', mString=mString, sString=sString, legend='NME Movies', movies=movies)

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


@app.route("/nme_mov/<string:movie>/<string:part>", methods = ['GET', 'POST'])
@login_required
def nme_mov(movie, part):
    check = Units.query.filter_by(unit=movie).first()

    # if current_user.username != 'Chris':
    #     flash('Not open yet', 'danger')
    #     return (redirect (url_for('nme_movies')))

    sDict = getStudentDict()
    print('sDict', sDict)
    print('sDict',  sDict[int(movie)])

    print('CHECK', check.u1)

    team = int(current_user.extra)
    movieList = [1,2,3,4,5,6,7,8,9,12,11]

    if team not in movieList:
        movieList.append(team)

    if current_user.username == 'Chris':
        pass
    elif check and int(check.u1) == 0:
        flash('Not open yet', 'danger')
        return (redirect (url_for('nme_movies')))
    elif int(movie) not in movieList:
        flash('Not in movie list yet', 'danger')
        return (redirect (url_for('nme_movies')))
    elif int(part) > sDict[int(movie)] + 1:
        flash('First finish earlier parts', 'danger')
        return (redirect (url_for('nme_movies')))


    movieData = movieDict[int(movie)].query.filter_by(username='payload').first()
    mString = movieData.Ans01

    print(movie)
    entries = movieDict[int(movie)].query.all()

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


    return render_template('nme/nme_mov' + part + '.html', uString=uString, mString=mString, mData=movieData, team=team)


@app.route("/nme_project/", methods = ['GET', 'POST'])
@login_required
def nme_project():

    team = current_user.extra

    project = movieDict[int(team)].query.filter_by(username='payload').first()
    print(project)

    if not project:
        print('not')
        dictionary = getMovieDict(team)
        newProject = movieDict[int(team)](username='payload', Ans01=dictionary)
        db.session.add(newProject)
        db.session.commit()
    else:
        dictionary = project.Ans01

    return render_template('nme/nme_project.html', mData=dictionary, team=team)



@app.route('/dubUpload', methods=['POST', 'GET'])
def dubUpload(audio_string, team, movie, device):


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

    model = movieDict[int(team)]
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

    model = movieDict[int(movie)]
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


'''### novels '''

def getTeam():
    user = User.query.filter_by(username=current_user.username).first()
    team = user.extra
    if not team:
        team = 100
    return team

@app.route ("/nme_novels", methods=['GET','POST'])
@login_required
def nme_novels():
    print('TEAM', getTeam())

    novels = ['01', '02', '03']
    names = []

    for u in User.query.filter_by(extra=getTeam()).all():
        print(u.username)
        names.append(u.username)

    completed = 0
    nCount = 0
    nDict = {}
    for n in novels:
        project = projectDict[n].query.filter_by(Grade=getTeam(), username=current_user.username).first()
        if project:
            nCount +=1
            nDict[n] = {}
            nDict[n]['novel'] = json.loads(project.Ans01)
            nDict[n]['sums'] = 0
            nDict[n]['status'] = project.Comment

            for c in json.loads(project.Ans02):
                nDict[n]['sums'] += 1

            if project.Comment == '2':
                completed += 1

            nDict[n]['recs'] = 0
            recs = json.loads(project.Ans03)
            print(recs)

            ## check if any null in each recording
            for rec in recs:
                noneChecker = True
                if len(recs[rec]) == 0:
                    noneChecker = False
                else:
                    for key in recs[rec]:
                        if key == 'words':
                            if None in recs[rec][key]:
                                noneChecker = False
                        else:
                            print(recs[rec][key])
                            if recs[rec][key] == None:
                                noneChecker = False
                if noneChecker:
                    nDict[n]['recs'] += 1

    nString = json.dumps(nDict)

    print(json.dumps(names))

    return render_template('nme/nme_novels.html', completed=completed, nCount=nCount, nString=nString, names=json.dumps(names), legend='NME Projects')


@app.route ("/nme_exams", methods=['GET','POST'])
@login_required
def nme_exams():
    names = ['Chris', 'William ']

    if current_user.username in names:
        pass
    else:
        pass
        # flash('Not open yet', 'danger')
        # return (redirect (url_for('home')))


    user = Exams.query.filter_by(username=current_user.username).first()

    if user:
        pass
    else:
        print('set user')
        examDict = {
            'vocab': 0,
            'listening': 0,
            'reading': 0,
            'summary': 0
        }
        userSet = Exams(username=current_user.username, j1=json.dumps(examDict))
        db.session.add(userSet)
        db.session.commit()
        user = Exams.query.filter_by(username=current_user.username).first()


    eString = user.j1

    return render_template('nme/nme_exams.html', eString=eString, legend='NME Reading Exams')


@app.route ("/nme_reading_score", methods=['GET','POST'])
@login_required
def nme_reading_score():
    test = request.form ['test']
    grade = request.form ['grade']

    user = Exams.query.filter_by(username=current_user.username).first()

    examDict = json.loads(user.j1)

    examDict[test] = grade

    user.j1 = json.dumps(examDict)
    db.session.commit()

    return jsonify({ 'result': 'good'})


@app.route ("/nme_vocab", methods=['GET','POST'])
@login_required
def nme_vocab():

    novels = ['01', '02', '03']

    vCount = 1
    vDict = {}
    vIndex = []
    for n in novels:
        project = projectDict[n].query.filter_by(username=current_user.username).first()
        if project:
            work = json.loads(project.Ans02)
            for c in work:
                print(work[c])
                for w in work[c]['newWords']:
                    vDict[vCount] = work[c]['newWords'][w]
                    vIndex.append(vCount)
                    vCount +=1

    print(len(vDict))

    finalDict = {}

    count = 1
    random.shuffle(vIndex)

    for w in vIndex:
        if count <= 20:
            finalDict[count] = vDict[w]
            count += 1


    vString = json.dumps(finalDict)


    return render_template('nme/nme_vocab.html', vString=vString, legend='NME Vocab Test')


@app.route ("/nme_reading", methods=['GET','POST'])
@login_required
def nme_reading():

    texts = U061U.query.filter_by(username='test1').first()
    textss = U061U.query.filter_by(username='Chris').first()

    textDict = {
        1: texts.Ans01,
        2: texts.Ans02,
        3: texts.Ans03,
        4: texts.Ans04,
        5: texts.Ans05,
        6: texts.Ans06,
        7: texts.Ans07,
        8: texts.Ans08,
        9: textss.Ans01,
        10: textss.Ans02,
        11: textss.Ans03,
        12: textss.Ans04,
        13: textss.Ans05,
        14: textss.Ans06,
        15: textss.Ans07,
        16: textss.Ans08,
    }

    rearrDict = {}
    count = 1

    arrangeCount = []

    for tex in textDict:
        print('TEXT')

        splitsO = textDict[tex].split('.')



        splitsR = textDict[tex].split('.')
        random.shuffle(splitsR)

        for line in splitsO:
                # print(line)
                if len(line) < 3:
                    splitsO.pop(splitsO.index(line))
                    splitsR.pop(splitsR.index(line))

        blanks = []
        for e in splitsO:
            blanks.append(None)

        splitsLen = len(splitsO)

        rearrDict[tex] = {
            'first': splitsO[0],
            'last': splitsO[splitsLen-1],
            'order': splitsO,
            'reorder': splitsR,
            'blanks': blanks
        }

    items = list(rearrDict.items())
    print(items)

    random.shuffle(items)

    newDict = {}
    count = 1
    for i in items:
        newDict[count] = i[1]
        count += 1


    rString = json.dumps(newDict)

    ## pprint(newDict)
    return render_template('nme/nme_reading.html', rString=rString, legend='NME Rearrange Test')


@app.route ("/nme_listening", methods=['GET','POST'])
@login_required
def nme_listening():

    texts = U041U.query.all()

    listDict = {}
    count = 1

    listCount = []

    for tex in texts:
        print('TRY')
        print(tex, texts)
        te = json.loads(tex.Ans01)
        for entry in te:
            print(te)
            t = te[entry]
            print(t, type(t))
            print(count)
            listDict[count] = {}
            listDict[count]['passOriginal'] = t['passage']
            random.shuffle(t['words'])
            listDict[count]['words'] = t['words']
            newPassage = t['passage']
            tCount = 1

            wordDict = {}

            for word in t['words']:
                word_index = newPassage.find(word)
                wordDict[word_index] = word

            sort = sorted(wordDict)  ### makes a list of indexs

            print(wordDict, sort)
            wordList = []
            for idx in sort:
                print(idx, tCount, wordDict[idx])
                wordList.append(wordDict[idx])
                newPassage = newPassage.replace(wordDict[idx], '___' + str(tCount) + '___')
                #print(newPassage)
                tCount += 1

            listDict[count]['passGaps'] = newPassage
            listDict[count]['wordList'] = wordList
            listDict[count]['wordsNull'] = [None, None, None, None]


            ansPassage = t['passage'].split('.')
            splitPassage = t['passage'].split('.')

            for line in splitPassage:
                print(line)
                if len(line) < 3:
                    splitPassage.pop(splitPassage.index(line))
                    ansPassage.pop(ansPassage.index(line))



            random.shuffle(splitPassage)
            listDict[count]['passSplit'] = splitPassage

            sentences = []
            for p in range(len(splitPassage)):
                sentences.append(None)

            listDict[count]['sentences'] = sentences
            listDict[count]['passAns'] = ansPassage
            listDict[count]['audio'] = t['audio']

            listCount.append(count)
            count += 1


    random.shuffle(listCount)
    finalCount = 1
    pairCount = 1

    finalDict = {
        1: {},
        2: {},
        3: {},
        4: {},
        5: {},
        6: {}
    }

    for entry in listCount:
        if finalCount == 7: ## change to 6
            break

        finalDict[finalCount][pairCount] = listDict[entry]

        if pairCount == 1:
            pairCount = 2
        else:
            pairCount = 1
            finalCount += 1




    lString = json.dumps(finalDict)

    return render_template('nme/nme_listening.html', lString=lString, legend='NME Listening Test')

@app.route ("/nme_summary", methods=['GET','POST'])
@login_required
def nme_summary():

    texts = U051U.query.all()

    sumDict = {}

    for tex in texts:

        sums = { 1: tex.Ans01, 2: tex.Ans02, 3: tex.Ans03, 4: tex.Ans04 }

        nums = [1,2,3,4]
        blanks = [None, None, None, None]

        random.shuffle(nums)

        sumDict[tex.username] = {
            'sums': sums,
            'nums': nums,
            'blanks': blanks
        }


    keys = list(sumDict.keys())
    random.shuffle(keys)

    newDict = {}

    for key in keys:
        newDict[key] = sumDict[key]


    sString = json.dumps(newDict)

    return render_template('nme/nme_summary.html', sString=sString, legend='NME Summary Test')


@app.route ("/addNovel", methods=['GET','POST'])
@login_required
def addNovel():
    print('ADD_NOVEL')
    novel = request.form ['novel']
    number = json.loads(novel)['number']

    print('NOVEL', novel)
    print('NUMBER', number)


    for novels in projectDict:
        if int(number) == int(novels):
            PROJECT = projectDict[novels]

    sums = {}
    recs = {1:{}, 2:{}, 3:{}}
    feeds = {}

    check = PROJECT.query.filter_by(Grade=getTeam(), username=current_user.username).first()

    if check:
        print('CHECK')
        check.Ans01 = novel
        db.session.commit()
    else:
        print('ENTRY')
        entry = PROJECT(username=current_user.username, Grade=getTeam(), Ans01=novel, Ans02=json.dumps(sums), Ans03=json.dumps(recs), Ans04=json.dumps(feeds))
        db.session.add(entry)
        db.session.commit()

    return jsonify({'nValue' : novel, 'nKey':number })


'''### summaries '''

@app.route ("/sum/<string:index>", methods=['GET','POST'])
@login_required
def nme_sum(index):


    project = projectDict[index].query.filter_by(username=current_user.username).first()
    novel = json.loads(project.Ans01)
    sums = json.loads(project.Ans02)

    html = 'nme/nme_sums.html'

    return render_template(html, legend='Chapter Summaries', nString=project.Ans01, sString=project.Ans02)


@app.route ("/addSum", methods=['GET','POST'])
@login_required
def addSum():
    print('ADD_SUM')
    nString = request.form ['novel']
    cString = request.form ['chapter']

    novel = json.loads(nString)
    chapter = json.loads(cString)
    novel_number = novel['number']
    chap_number = chapter['number']

    for novels in projectDict:
        if int(novel_number) == int(novels):
            project = projectDict[novels].query.filter_by(username=current_user.username).first()

    print(project, project.Ans02, novel, chapter, novel_number, chap_number)

    current_sum = json.loads(project.Ans02)
    current_sum[chap_number] = chapter
    project.Ans02 = json.dumps(current_sum)
    db.session.commit()

    return jsonify({'cObj' : json.dumps(current_sum)})

@app.route ("/updateSum", methods=['GET','POST'])
@login_required
def updateSum():
    print('UPDATE_SUM')
    number = request.form ['number']
    name = request.form ['name']
    summary = request.form ['summary']
    novel = request.form ['novel']

    ## get student data
    entry = projectDict[novel].query.filter_by(username=name).first()
    sums = json.loads(entry.Ans02)
    print(summary, sums)
    sums[str(number)]['summary'] = summary
    entry.Ans02 = json.dumps(sums)
    entry.Ans03 = '{"1": {}, "2": {}}'
    db.session.commit()

    return jsonify({'success' : True})

@app.route ("/updateComment", methods=['GET','POST'])
@login_required
def updateComment():
    print('UPDATE_COMM')
    name = request.form ['name']
    novel = request.form ['novel']

    ## get student data
    entry = projectDict[novel].query.filter_by(username=name).first()
    entry.Comment = '2'
    db.session.commit()

    return jsonify({'success' : True})

'''### feedback '''

@app.route ("/rec/<string:index>", methods=['GET','POST'])
@login_required
def nme_recording(index):

    rCount = 0
    rDict = {}

    project = projectDict[index].query.filter_by(username=current_user.username).first()
    if project:
        rDict = json.loads(project.Ans03)
        rCount +=1

    html = 'nme/nme_recs.html'

    return render_template(html, legend='Add Recordings', index=index, rString=json.dumps(rDict), rCount=rCount)


@app.route ("/addRec", methods=['GET','POST'])
@login_required
def addRec():
    print('ADD_REC_DETAILS')
    novel = request.form ['novel']
    rec = request.form ['rec']
    details = request.form ['details']
    print(details)

    project = projectDict[novel].query.filter_by(username=current_user.username).first()

    rDict = json.loads(project.Ans03)
    rDict[rec] = json.loads(details)
    project.Ans03 = json.dumps(rDict)
    db.session.commit()

    return jsonify({'details' : details})



''' ## performance '''

@app.route ("/effort_dash", methods=['GET','POST'])
@login_required
def nme_effort_dash():

    eList = U001U.query.all()

    eDict = {}

    for e in eList:
        eDict[e.username] = json.loads(e.Ans01)

    html = 'nme/nme_effort_dash.html'

    return render_template(html, legend='Course Performance', eString=json.dumps(eDict))


@app.route ("/effort", methods=['GET','POST'])
@login_required
def nme_effort():

    survey = U012U.query.filter_by(username=current_user.username).first()

    if not survey:
        obj = json.dumps({})
        entry = U012U(username=current_user.username, Ans01=obj, Ans02=obj, Ans03=obj, Ans04=obj, Ans05=obj, Ans06=obj, Ans07=obj, Ans08=obj)
        db.session.add(entry)
        db.session.commit()

    survey = U012U.query.filter_by(username=current_user.username).first()

    html = 'nme/nme_performance.html'

    return render_template(html, legend='Course Performance', eString=json.dumps(survey.Ans01))

@app.route ("/addSurvey", methods=['GET','POST'])
@login_required
def addSurvey():
    print('ADD_SURVEY')
    eString = request.form ['reflection']
    reflection = json.loads(eString)

    survey = U012U.query.filter_by(username=current_user.username).first()

    if survey:
        records = json.loads(survey.Ans01)
    else:
        start = U012U(username=current_user.username, Ans01=json.dumps({}))
        db.session.add(start)
        db.session.commit()
        survey = U012U.query.filter_by(username=current_user.username).first()
        records = json.loads(survey.Ans01)

    records[reflection['date']] = reflection

    survey.Ans01 = json.dumps(records)
    db.session.commit()

    return jsonify({'msg' : 'Reflection added'})


@app.route('/nme_storeB64', methods=['POST'])
def storeB64():

    b64data = request.form ['b64data']
    fileType = request.form ['fileType']
    novel = request.form ['novel']
    rec = request.form ['rec']

    project = projectDict[novel].query.filter_by(username=current_user.username).first()
    rDict = json.loads(project.Ans03)
    print(type(rec), rec)
    print(rDict)
    try:
        file_key = rDict[int(rec)]['audio']
        print('file_key_found ', file_key)
        file_key_split = file_key.split('com/')[1]
        s3_resource.Object(S3_BUCKET_NAME, file_key_split).delete()
    except:
        print('no file_key found')

    now = datetime.now()
    time = now.strftime("_%M%S")
    print("time:", time)

    print('PROCESSING AUDIO')
    audio = base64.b64decode(b64data)

    filename = current_user.username + '/' + novel + '/' + rec + time + '.mp3'
    audioLink = S3_LOCATION + filename
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=audio)

    rDict[rec]['audio'] = audioLink
    project.Ans03 = json.dumps(rDict)
    db.session.commit()

    return jsonify({'audioLink' : audioLink})



