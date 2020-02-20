import boto3
import json
import os

try:
    from aws import KEYS
    DEBUG = True
    SCHEMA = KEYS.SCHEMA
except: 
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 
    SCHEMA = os.environ['SCHEMA']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    SECRET_KEY = os.environ['SECRET_KEY']

    DEBUG = False

jList = ['None', 'reading-lms', 'workplace-lms', 'abc-lms', 'peng-lms', 'food-lms']
         

s3_resource = boto3.resource('s3',
        aws_access_key_id=KEYS.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= KEYS.AWS_SECRET_ACCESS_KEY)

s3_client = boto3.client('s3',
         aws_access_key_id=KEYS.AWS_ACCESS_KEY_ID,
         aws_secret_access_key= KEYS.AWS_SECRET_ACCESS_KEY)


def loadJson():
    content_object = s3_resource.Object(   jList[int(SCHEMA)],    'json_files/meta.json' )    
    file_content = content_object.get()['Body'].read().decode('utf-8')
    meta = json.loads(file_content)      
    return meta

class BaseConfig:
    META = loadJson()     

    s3_resource = s3_resource
    s3_client = s3_client

    SCHEMA = SCHEMA
    DESIGN = META['M']['DESIGN']
    S3_BUCKET_NAME =  META['M']['S3_BUCKET_NAME']
    S3_LOCATION = 'https://' + S3_BUCKET_NAME + '.s3.ap-northeast-1.amazonaws.com/'

    AWS_ACCESS_KEY_ID = KEYS.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = KEYS.AWS_SECRET_ACCESS_KEY
    SQLALCHEMY_DATABASE_URI = KEYS.SQLALCHEMY_DATABASE_URI  
    MAIL_PASSWORD = KEYS.MAIL_PASSWORD
    SECRET_KEY = KEYS.SECRET_KEY 

    IDLIST = META['C']

    DEBUG = DEBUG
        






