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

    DESIGN = {
            "titleColor": "grey",
            "bodyColor": "lightgrey",
            "headTitle": "Just Applied English",
            "headLogo": "https://reading-lms.s3.ap-northeast-1.amazonaws.com/logo.PNG"
        }

    # IDLIST = META['C']
    # SCHEMA = SCHEMA
    # DESIGN = META['M']['DESIGN']
    # S3_BUCKET_NAME =  META['M']['S3_BUCKET_NAME']
    # S3_LOCATION = 'https://' + S3_BUCKET_NAME + '.s3.ap-northeast-1.amazonaws.com/'
    # AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    # AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    # REDIS_PASSWORD = REDIS_PASSWORD









