import os
import boto3
import json
try:
    from aws import Settings    
    COLOR_SCHEMA = Settings.COLOR_SCHEMA
    s3_resource = Settings.s3_resource 
    CODE_STRING = Settings.CODE_STRING
    GS_KEY_ID = Settings.GS_KEY_ID
except:
    s3_resource = boto3.resource('s3') 
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 
    CODE_STRING = os.environ['CODE_STRING']
    GS_KEY_ID = os.environ['GS_KEY_ID']



s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=json_name, Body=json_content) 
print('JSON Updated')







    
    

    

