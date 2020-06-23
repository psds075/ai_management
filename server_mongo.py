# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
import os
import json
import pandas as pd
import requests
import collections
import cv2
import base64
import numpy as np
import pymongo

app = Flask(__name__)
DEBUG_MODE = False

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
DENTIQUB = myclient["DENTIQUB"]
imagedata = DENTIQUB["imagedata"]
dataset = DENTIQUB["dataset"]

with open('env.json') as json_file:
    data = json.load(json_file)

BASE_DIR = data['BASE_DIR']
DB_NAME = ''
DB_DIR = BASE_DIR + DB_NAME + '/'
TABLE_LIST = ['GUIDED_FILENAME','SEX','AGE','STATUS','TMJ_LEFT','TMJ_RIGHT','OSTEOPOROSIS','COMMENT_TEXT','REVIEW_CHECK','BBOX_LABEL', 'CONFIRM_CHECK','PREDICTION_CHECK','TIMESTAMP']

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/viewer", defaults={'DATASET_NAME' : 'NONE'},methods=['GET', 'POST'])
@app.route("/viewer/<string:DATASET_NAME>", methods=['GET', 'POST'])
def viewer(DATASET_NAME):
    with open('label_dict.json',encoding = 'utf-8') as json_file:
        data = json.load(json_file)
        LABEL_DICT = data['LABEL_DICT']

    response = requests.post('http://dentiqub.iptime.org:5002/api')
    training_status = json.loads(response.text)['STATUS']
    if(len(training_status.split(' '))==4):
        training_percent = training_status.split(' ')[2]
    else:
        training_percent = 0
    datasetlist = []
    archivelist = []
    for DIR in os.listdir(BASE_DIR):
        if(os.path.isdir(BASE_DIR+DIR)):
            if not dataset.find_one({'NAME':DIR}):
                dataset.insert_one({'NAME':DIR,'STATUS':'INSERTED'})
            try:
                dataset_num = len(os.listdir(BASE_DIR+DIR))
                if(imagedata.find({'DATASET_NAME':DIR,'CONFIRM_CHECK':'CONFIRM'}).count()+imagedata.find({'DATASET_NAME':DIR,'CONFIRM_CHECK':'DELETE'}).count() == dataset_num):
                    myquery = { "NAME":DIR }
                    newvalues = { "$set": { "STATUS": "ARCHIVE" } }
                    dataset.update_one(myquery, newvalues)
                    archivelist.append({'DATASET_NAME' : DIR})
                else:
                    myquery = { "NAME":DIR }
                    newvalues = { "$set": { "STATUS": "INSERTED" } }
                    dataset.update_one(myquery, newvalues)
                    datasetlist.append({'DATASET_NAME' : DIR})
            except:
                print('exception occured.')
                
    if DATASET_NAME == 'NONE':
        datalist = []

    else:
        if(len(os.listdir(BASE_DIR+DATASET_NAME)) != imagedata.find({'DATASET_NAME' : DATASET_NAME}).count()):
            for filename in os.listdir(BASE_DIR+DATASET_NAME):
                if not imagedata.find_one({'FILENAME':filename}):
                    imagedata.insert_one({'FILENAME':filename,'DATASET_NAME':DATASET_NAME, 'REVIEW_CHECK': 'UNREAD','CONFIRM_CHECK':'UNCONFIRM'})
        datalist = []
        for image in imagedata.find({'DATASET_NAME' : DATASET_NAME}):
            if not 'REVIEW_CHECK' in image:
                image['REVIEW_CHECK'] = 'UNREAD'
            if not 'CONFIRM_CHECK' in image:
                image['CONFIRM_CHECK'] = 'UNCONFIRM'
            data = {
                    'FILENAME' : image['FILENAME'],
                    'REVIEW_CHECK': image['REVIEW_CHECK'],
                    'CONFIRM_CHECK': image['CONFIRM_CHECK'],
                    }
            datalist.append(data)

    print('speed_test_end')
        
    return render_template('viewer.html', datalist = datalist, datasetlist = datasetlist, archivelist=archivelist, current_dataset = DATASET_NAME, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent)

@app.route("/_JSON", methods=['GET', 'POST'])
def sending_data():

    if(request.json['ORDER'] == 'TARGET'):
        target = imagedata.find_one({'FILENAME':request.json['FILENAME']})
        if not 'TMJ_LEFT' in target:
            target['TMJ_LEFT'] = ''
        if not 'TMJ_RIGHT' in target:
            target['TMJ_RIGHT'] = ''
        if not 'OSTEOPOROSIS' in target:
            target['OSTEOPOROSIS'] = ''
        if not 'COMMENT_TEXT' in target:
            target['COMMENT_TEXT'] = ''
        if not 'REVIEW_CHECK' in target:
            target['REVIEW_CHECK'] = 'UNREAD'
        if not 'BBOX_LABEL' in target:
            target['BBOX_LABEL'] = '[]'
        if not 'CONFIRM_CHECK' in target:
            target['CONFIRM_CHECK'] = 'UNCONFIRM'
        if not 'PREDICTION_CHECK' in target:
            target['PREDICTION_CHECK'] = 'NO_PREDICT'
        data = {'FILENAME' : target['FILENAME'], 
                'TMJ_LEFT':target['TMJ_LEFT'], 
                'TMJ_RIGHT':target['TMJ_RIGHT'],
                'OSTEOPOROSIS':target['OSTEOPOROSIS'], 
                'COMMENT_TEXT':target['COMMENT_TEXT'],
                'REVIEW_CHECK':target['REVIEW_CHECK'],
                'BBOX_LABEL':target['BBOX_LABEL'],
                'CONFIRM_CHECK':target['CONFIRM_CHECK'],
                'PREDICTION_CHECK':target['PREDICTION_CHECK']
                }
        
        target['REVIEW_CHECK'] = 'READ'
        imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": target })

        return json.dumps(json.dumps(data))

    if(request.json['ORDER'] == 'LABEL'):

        if(request.json['PARAMETER'] == 'BBOX_LABEL'):
            BBOX_LABEL = json.loads(request.json['SETVALUE'])
            for EACH_LABEL in BBOX_LABEL:
                EACH_LABEL['left'] = int(EACH_LABEL['left'] / request.json['RATIO'])
                EACH_LABEL['top'] = int(EACH_LABEL['top'] / request.json['RATIO'])
                EACH_LABEL['width'] = int(EACH_LABEL['width'] / request.json['RATIO'])
                EACH_LABEL['height'] = int(EACH_LABEL['height'] / request.json['RATIO'])
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {request.json['PARAMETER']:json.dumps(BBOX_LABEL)}})
        else:
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {request.json['PARAMETER']:str(request.json['SETVALUE'])}})
        
        if(request.json['PARAMETER'] == 'CONFIRM_CHECK'):
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {'TIMESTAMP':str(pd.Timestamp('now'))}})

        return json.dumps('Success')

    if(request.json['ORDER'] == 'PREDICTION'):
        target_image = os.path.join(BASE_DIR+request.json['DATASET'],request.json['FILENAME'])
        img = hanimread(target_image) #img = cv2.imread(target_image) 대체함. 한글경로 버그 수정
        data = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        mydata = {'img_name' : request.json['FILENAME'], 'data' : data}
        response = requests.post('http://dentiqub.iptime.org:5001/api', json=mydata)
        if(DEBUG_MODE == True):
            print(json.loads(response.text)['message'])
        return json.dumps(json.loads(response.text)['message'])

    if(request.json['ORDER'] == 'START_TRAINING'):
        response = requests.post('http://dentiqub.iptime.org:5002/start')
        if(DEBUG_MODE == True):
            print(json.loads(response.text)['STATUS'])
        return json.dumps(json.loads(response.text)['STATUS'])

    if(request.json['ORDER'] == 'TRAINING_STATUS'):
        response = requests.post('http://dentiqub.iptime.org:5002/api')
        if(DEBUG_MODE == True):
            print(json.loads(response.text)['STATUS'])
        return json.dumps(json.loads(response.text)['STATUS'])

    if(request.json['ORDER'] == 'STATISTICS'):
        LABEL_RANK = label_statistics()
        PRECISION_DATA = prediction_statistics()
        return json.dumps({'LABEL_RANK':LABEL_RANK, 'PRECISION_DATA':PRECISION_DATA})

@app.route('/database/<path:path>')
def database(path):
    return send_from_directory(BASE_DIR, path) 

@app.route('/thumb/<path:path>')
def thumb_database(path):
    return send_from_directory(BASE_DIR, path)

def label_statistics():

    LABEL_LIST = []
    
    for image in imagedata.find({}):
        print(image)
        if ('BBOX_LABEL' in image) and ('CONFIRM_CHECK' in image):
            if (image['CONFIRM_CHECK'] == 'CONFIRM'):
                BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                for j in range(len(BBOX_LABEL)):
                    class_name = str(BBOX_LABEL[j]['label'])
                    LABEL_LIST.append(class_name)

    LABEL_COUNTER = collections.Counter(LABEL_LIST)
    LABEL_RANK = []

    for key, value in sorted(LABEL_COUNTER.items(), key=lambda item: item[1], reverse = True):
        LABEL_RANK.append((key, value))

    return LABEL_RANK

def prediction_statistics():

    CONFIRM_COUNT = 0
    PREDICT_COUNT = 0
    NO_PREDICT_COUNT = 0
    NOT_CHECKED = 0

    for image in imagedata.find():
        if ('BBOX_LABEL' in image) and ('CONFIRM' in image):
            if (image['CONFIRM_CHECK'] == 'CONFIRM'):
                CONFIRM_COUNT+=1
                if (image['PREDICTION_CHECK'] == 'PREDICT'):
                    PREDICT_COUNT+=1
                if (image['PREDICTION_CHECK'] == 'NO_PREDICT'):
                    NO_PREDICT_COUNT+=1
                if (image['PREDICTION_CHECK'] == ''):
                    NOT_CHECKED+=1
    

    CURRENT_PRECISION = int((PREDICT_COUNT+NO_PREDICT_COUNT)/(CONFIRM_COUNT*100+0.1))
    CURRENT_DATA_AMOUNT = CONFIRM_COUNT
    CURRENT_DATE = 'NOW'

    # 디렉토리 불러오기
    with open('precision_record.json') as json_file:
        data = json.load(json_file)
        PRECISION_RECORD = data['PRECISION_RECORD']

    PRECISION_DATA = []
    for PRECISION in PRECISION_RECORD:
        PRECISION_DATA.append((PRECISION[0],PRECISION[1], PRECISION[2]))
    PRECISION_DATA.append((CURRENT_DATE, CURRENT_DATA_AMOUNT, str(CURRENT_PRECISION) + '%'))

    return PRECISION_DATA

def hanimread(filePath):
    stream = open( filePath.encode("utf-8") , "rb")
    bytes = bytearray(stream.read())
    numpyArray = np.asarray(bytes, dtype=np.uint8)
    return cv2.imdecode(numpyArray , cv2.IMREAD_UNCHANGED)

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host = '0.0.0.0', port = 80)


