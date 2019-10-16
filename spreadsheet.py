import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
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


sheetsList = ['blank', 'FRDExam', 'WPEExam', 'ICCExam'] 
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

json_dict = {
  "type": "service_account",
  "project_id": "testrec",
  "private_key_id": GS_KEY_ID,
  "private_key": "-----BEGIN PRIVATE KEY-----\n" + CODE_STRING + "==\n-----END PRIVATE KEY-----\n", 
  "client_email": "lmsexams@testrec.iam.gserviceaccount.com",
  "client_id": "",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lmsexams%40testrec.iam.gserviceaccount.com"
}

creds = ServiceAccountCredentials.from_json_keyfile_dict(json_dict, scope)
client = gspread.authorize(creds)



class Sheets: 
    sheets = client.open(sheetsList[int(COLOR_SCHEMA)])
    print(sheets)






    
    

    

