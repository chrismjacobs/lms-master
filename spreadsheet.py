import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from flask import url_for
from flask_login import current_user
try:
    from aws import Settings
    COLOR_SCHEMA = Settings.COLOR_SCHEMA    
except:  
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 

    
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Exam.json', scope)
client = gspread.authorize(creds)

class Sheets: 

    sheets = client.open(sheetsList[int(COLOR_SCHEMA)])






    
    

    

