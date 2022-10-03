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
            "bodyColor": "whitesmoke",
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
        "courseCode" : "vtm",
        "S3_LOCATION" : "https://vietnam-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "darkslateblue",
            "bodyColor": "whitesmoke",
            "headTitle": "VTM course",
            "headLogo": "https://icc-lms.s3-ap-northeast-1.amazonaws.com/profiles/logo.png"
        }
    },
    7 : {
        "Course": "Movie Dubbing",
        "S3_BUCKET_NAME": "nme-lms",
        "courseCode" : "nme",
        "S3_LOCATION" : "https://nme-lms.s3.ap-northeast-1.amazonaws.com/",
        "DESIGN": {
            "titleColor": "gold",
            "bodyColor": "whitesmoke",
            "headTitle": "NME course",
            "headLogo": "https://nme-lms.s3-ap-northeast-1.amazonaws.com/profiles/logo.png"
        }
    },

}

idList2 = {"frd": ["120854017", "120854029", "120854048", "120854058", "121154002", "121154003", "121154004", "121154005", "121154006", "121154007", "121154008", "121154009", "121154010", "121154011", "121154013", "121154014", "121154015", "121154017", "121154018", "121154019", "121154020", "121154021", "121154022", "121154023", "121154024", "121154025", "121154026", "321152040", "321152041", "321152042", "321152044"], "wpe": ["120815145", "120871014", "120953046", "121015001", "121015125", "121015242", "121054001", "121054002", "121054003", "121054005", "121054006", "121054007", "121054008", "121054010", "121054011", "121054012", "121054013", "121054016", "121054017", "121054018", "121054019", "121054022", "121054023", "121054024", "121054025", "121054026", "121054027", "121054028", "121054029", "121054031", "121054033", "121054038", "121054039", "121054041", "121054042", "121054043", "121054044", "131154002"], "icc": ["120754071", "120812309", "120854005", "120854013", "120854018", "120854019", "120854021", "120854031", "120854037", "120854040", "120854050", "121015001", "121015242", "121054001", "121054002", "121054003", "121054005", "121054006", "121054007", "121054008", "121054010", "121054011", "121054012", "121054013", "121054016", "121054017", "121054018", "121054019", "121054022", "121054023", "121054024", "121054025", "121054026", "121054027", "121054028", "121054029", "121054031", "121054033", "121054038", "121054039", "121054041", "121054042", "121054043", "121054044", "131054003", "320852204", "320852221"], "lnc": ["120736507", "120832011", "120836028", "120850920", "120850932", "120854058", "120955053", "121154002", "121154003", "121154004", "121154005", "121154006", "121154007", "121154008", "121154009", "121154010", "121154011", "121154013", "121154014", "121154015", "121154017", "121154018", "121154019", "121154020", "121154021", "121154022", "121154023", "121154024", "121154025", "121154026", "321152040", "321152041", "321152042", "321152044"], "vtm": ["120850903", "120850904", "120850905", "120850906", "120850907", "120850909", "120850910", "120850911", "120850913", "120850914", "120850915", "120850916", "120850917", "120850918", "120850921", "120850922", "120850923", "120850924", "120850925", "120850927", "120850928", "120850929", "120850930", "120850931", "120850933", "120850934", "120850935", "120850937", "120850938", "120850939", "120850940"]}

# def loadJson(SCHEMA):
#     content_object = s3_resource.Object(   jList[SCHEMA],    'json_files/meta.json' )
#     file_content = content_object.get()['Body'].read().decode('utf-8')
#     meta = json.loads(file_content)
#     # print('META')
#     return meta

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









