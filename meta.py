import boto3
import json
import os

try:
    from aws import KEYS
    AWS_ACCESS_KEY_ID = KEYS.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = KEYS.AWS_SECRET_ACCESS_KEY
    SQLALCHEMY_DATABASE_URI = KEYS.SQLALCHEMY_DATABASE_URI
    MAIL_PASSWORD = KEYS.MAIL_PASSWORD
    SECRET_KEY = KEYS.SECRET_KEY
    # REDIS_PASSWORD = KEYS.REDIS_PASSWORD
    DEBUG = True


except:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_ALT']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = False
    # try:
    #     REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
    # except:
    #     REDIS_PASSWORD = None



s3_resource = boto3.resource('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

s3_client = boto3.client('s3',
         aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)


jList = ['None',
        'reading-lms',
        'workplace-lms',
        'icc-lms',
        'peng-lms',
        'culture-lms',
        'vietnam-lms',
        'nme-lms',
        'food-lms'
        ]

schemaList = {
    0 : {
        "Course": "Applied English",
        "S3_BUCKET_NAME" : "tester-lms",
        "S3_LOCATION" : "https://tester-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN" : {
            "titleColor": "grey",
            "bodyColor": "lightgrey",
            "headTitle": "Just Applied English",
            "headLogo": "https://reading-lms.s3.ap-northeast-1.amazonaws.com/logo.PNG"
        }
    },
    1 : {
        "Course": "Reading and Vocab",
        "courseCode" : "frd",
        "S3_BUCKET_NAME": "reading-lms",
        "S3_LOCATION" : "https://reading-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "MEDIUMSEAGREEN",
            "bodyColor": "MINTCREAM",
            "titleColor2": "LightSeaGreen",
            "bodyColor2": "Azure",
            "headTitle": "Freshman Reading",
            "headLogo": "https://reading-lms.s3-ap-northeast-1.amazonaws.com/profiles/favicon.png"
        }
    },
    2 : {
        "Course": "WorkPlace English",
        "courseCode" : "wpe",
        "S3_BUCKET_NAME": "workplace-lms",
        "S3_LOCATION" : "https://workplace-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "CORAL",
            "bodyColor": "FLORALWHITE",
            "headTitle": "Workplace English",
            "headLogo": "https://writing-lms.s3-ap-northeast-1.amazonaws.com/profiles/icon.png"
        }
    },

    3 : {
        "Course": "Intercultural Communication",
        "courseCode" : "icc",
        "S3_BUCKET_NAME": "icc-lms",
        "S3_LOCATION" : "https://icc-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "dodgerblue",
            "bodyColor": "powder",
            "headTitle": "ICC course",
            "headLogo": "https://icc-lms.s3-ap-northeast-1.amazonaws.com/profiles/logo.png"
        }
    },

    5 : {
        "Course": "Language and Culture",
        "S3_BUCKET_NAME": "culture-lms",
        "courseCode" : "lnc",
        "S3_LOCATION" : "https://culture-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "RebeccaPurple",
            "bodyColor": "whitesmoke",
            "headTitle": "LNC course",
            "headLogo": "https://culture-lms.s3-ap-northeast-1.amazonaws.com/profiles/logo.png"
        }
    },

    6 : {
        "Course": "Intercultural Communication",
        "S3_BUCKET_NAME": "vietnam-lms",
        "courseCode" : "icc",
        "S3_LOCATION" : "https://vietnam-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "darkslateblue",
            "bodyColor": "powder",
            "headTitle": "ICC course",
            "headLogo": "https://icc-lms.s3-ap-northeast-1.amazonaws.com/profiles/logo.png"
        }
    },

}


def loadJson(SCHEMA):
    content_object = s3_resource.Object(   jList[SCHEMA],    'json_files/meta.json' )
    file_content = content_object.get()['Body'].read().decode('utf-8')
    meta = json.loads(file_content)
    # print('META')
    return meta

class BaseConfig:

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    MAIL_PASSWORD = MAIL_PASSWORD
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG

    s3_resource = s3_resource
    s3_client = s3_client

    jList = jList


    # IDLIST = META['C']
    # SCHEMA = SCHEMA
    # DESIGN = META['M']['DESIGN']
    # S3_BUCKET_NAME =  META['M']['S3_BUCKET_NAME']
    # S3_LOCATION = 'https://' + S3_BUCKET_NAME + '.s3.ap-northeast-1.amazonaws.com/'
    # AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    # AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    # REDIS_PASSWORD = REDIS_PASSWORD









