import boto3
import json
import os


try:
    from aws import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SCHEMA
    DEBUG = True
except: 
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'] 
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'] 
    SCHEMA = os.environ['SCHEMA'] 
    DEBUG = False

jList = ['None', 'reading-lms', 'workplace-lms', 'abc-lms', 'peng-lms', 'food-lms']
         

s3_resource = boto3.resource('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

s3_client = boto3.client('s3',
         aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)


def loadJson():
    content_object = s3_resource.Object(   jList[int(SCHEMA)],    'json_files/meta.json' )    
    file_content = content_object.get()['Body'].read().decode('utf-8')
    meta = json.loads(file_content)      
    return meta

class BaseConfig:
    META = loadJson()     

    s3_resource = s3_resource
    s3_client = s3_client

    SCHEMA = int(META['M']['SCHEMA'])
    DESIGN = META['M']['DESIGN']

    IDLIST = META['C']

    SECRET_KEY = META['S']['SECRET_KEY']
    S3_LOCATION = META['S']['S3_LOCATION']
    S3_BUCKET_NAME =  META['S']['S3_BUCKET_NAME']
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    SQLALCHEMY_DATABASE_URI = META['S']['SQLALCHEMY_DATABASE_URI']    
    MAIL_USERNAME = META['S']['MAIL_USERNAME']
    MAIL_PASSWORD = META['S']['MAIL_PASSWORD']

    DEBUG = DEBUG
        






