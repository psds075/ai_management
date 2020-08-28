﻿# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, session
import os
import json
import pandas as pd
import requests
import collections
import cv2
import base64
import numpy as np
import pymongo
from shapely import geometry
from multiprocessing.pool import ThreadPool
from datetime import datetime
pool = ThreadPool(processes=2)

app = Flask(__name__)
app.secret_key = b'123'
DEBUG_MODE = True

# 일반 로그인 관련
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    hospitaldata = DENTIQUB["hospitaldata"]

    if request.method == 'POST':
        print('test')
        if(request.form['id']=='ai' and request.form['password'] == 'aiqub'):
            session['NAME'] = 'MANAGER'
            print('test1')
            return redirect(url_for('viewer'))
        elif(request.form['id']=='demo' and request.form['password'] == 'aiqub'):
            session['NAME'] = 'DEMO'
            return redirect(url_for('demo'))
        elif(hospitaldata.find_one({'ID':request.form['id'], 'PASSWORD':request.form['password']})):
            session['NAME'] = hospitaldata.find_one({'ID':request.form['id']})['NAME']
            return redirect(url_for('service'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session['NAME'] = False
    return redirect(url_for('login'))

with open('env.json') as json_file:
    data = json.load(json_file)

BASE_DIR = data['BASE_DIR']
DB_NAME = ''
DB_DIR = BASE_DIR + DB_NAME + '/'
TABLE_LIST = ['GUIDED_FILENAME','SEX','AGE','STATUS','TMJ_LEFT','TMJ_RIGHT','OSTEOPOROSIS','COMMENT_TEXT','REVIEW_CHECK','BBOX_LABEL', 'CONFIRM_CHECK','PREDICTION_CHECK','TIMESTAMP']

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('login.html')

@app.route("/viewer", defaults={'DATASET_NAME' : 'NONE'},methods=['GET', 'POST'])
@app.route("/viewer/<string:DATASET_NAME>", methods=['GET', 'POST'])
def viewer(DATASET_NAME):
    
    print('test2')
    if not session['NAME'] == 'MANAGER':
        return redirect(url_for('login'))

    print('test3')
    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]
    
    print('test4')

    with open('label_dict.json',encoding = 'utf-8') as json_file:
        data = json.load(json_file)
        LABEL_DICT = data['LABEL_DICT']

    response = requests.post('http://dentiqub.iptime.org:5001/api')
    training_status = json.loads(response.text)['STATUS']

    if(len(training_status.split(' '))==4):
        training_percent = training_status.split(' ')[2]
    else:
        training_percent = 0
    datasetlist = []
    archivelist = []

    for data in dataset.find({'STATUS':'ARCHIVE'}).sort("NAME",pymongo.DESCENDING):
        archivelist.append({'DATASET_NAME':data['NAME']})

    for data in dataset.find({'STATUS':'INSERTED'}).sort("NAME",pymongo.DESCENDING):
        datasetlist.append({'DATASET_NAME':data['NAME']})
                
    if DATASET_NAME == 'NONE':
        datalist = []
        archive_check = 'NONE'

    else:
        archive_check = dataset.find_one({'NAME':DATASET_NAME})['STATUS']
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
        
    return render_template('viewer.html', datalist = datalist, datasetlist = datasetlist, archivelist=archivelist, current_dataset = DATASET_NAME, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent, archive_check=archive_check)


@app.route("/comment",methods=['GET', 'POST'])
def comment():
    
    if not session['NAME'] == 'MANAGER':
        return redirect(url_for('login'))

    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]
    
    with open('label_dict.json',encoding = 'utf-8') as json_file:
        data = json.load(json_file)
        LABEL_DICT = data['LABEL_DICT']

    response = requests.post('http://dentiqub.iptime.org:5001/api')
    training_status = json.loads(response.text)['STATUS']

    if(len(training_status.split(' '))==4):
        training_percent = training_status.split(' ')[2]
    else:
        training_percent = 0
    datasetlist = []
    archivelist = []

    for data in dataset.find({'STATUS':'ARCHIVE'}).sort("NAME",pymongo.DESCENDING):
        archivelist.append({'DATASET_NAME':data['NAME']})

    for data in dataset.find({'STATUS':'INSERTED'}).sort("NAME",pymongo.DESCENDING):
        datasetlist.append({'DATASET_NAME':data['NAME']})

    datalist = []
    for image in imagedata.find({'DIALOG':{'$exists':True}}):
        if not 'REVIEW_CHECK' in image:
            image['REVIEW_CHECK'] = 'UNREAD'
        if not 'CONFIRM_CHECK' in image:
            image['CONFIRM_CHECK'] = 'UNCONFIRM'
        if not 'HOSPITAL' in image:
            image['HOSPITAL'] = ''
        if not 'NOTI' in image:
            image['COMMENT'] = 'UNCOMMENT'
            image['NOTI'] = ''
        if not 'NAME' in image:
            image['NAME'] = 'UNCOMMENT'
        if not 'COMMENT' in image:
            image['COMMENT'] = 'UNCOMMENT'
        elif image['NOTI'] == 'MANAGER':
            image['COMMENT'] = 'COMMENT'
        else:
            image['COMMENT'] = 'UNCOMMENT'
        data = {
                'FILENAME' : image['FILENAME'],
                'DATASET_NAME' : image['DATASET_NAME'],
                'REVIEW_CHECK': image['REVIEW_CHECK'],
                'CONFIRM_CHECK': image['CONFIRM_CHECK'],
                'COMMENT' : image['COMMENT'],
                'HOSPITAL' : image['HOSPITAL'],
                'NAME' : image['NAME']
                }
        datalist.append(data)
        
    return render_template('comment.html', datalist = datalist, datasetlist = datasetlist, archivelist=archivelist, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent)


@app.route("/demo", defaults={'DATASET_NAME' : 'NONE'},methods=['GET', 'POST'])
@app.route("/demo/<string:DATASET_NAME>", methods=['GET', 'POST'])
def demo(DATASET_NAME):
    
    if not session['NAME'] == 'DEMO':
        return redirect(url_for('login'))

    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]
    
    with open('label_dict.json',encoding = 'utf-8') as json_file:
        data = json.load(json_file)
        LABEL_DICT = data['LABEL_DICT']

    response = requests.post('http://dentiqub.iptime.org:5001/api')
    training_status = json.loads(response.text)['STATUS']
    if(len(training_status.split(' '))==4):
        training_percent = training_status.split(' ')[2]
    else:
        training_percent = 0
    datasetlist = []
    archivelist = []

    for data in dataset.find({'STATUS':'ARCHIVE'}).sort("NAME",pymongo.DESCENDING):
        archivelist.append({'DATASET_NAME':data['NAME']})

    for data in dataset.find({'STATUS':'INSERTED'}).sort("NAME",pymongo.DESCENDING):
        datasetlist.append({'DATASET_NAME':data['NAME']})

    if DATASET_NAME == 'NONE':
        datalist = []
        archive_check = 'NONE'

    else:
        archive_check = dataset.find_one({'NAME':DATASET_NAME})['STATUS']
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
        
    return render_template('demo.html', datalist = datalist, datasetlist = datasetlist, archivelist=archivelist, current_dataset = DATASET_NAME, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent, archive_check=archive_check)


@app.route("/service", defaults={'DATASET_NAME' : 'NONE'},methods=['GET', 'POST'])
@app.route("/service/<string:DATASET_NAME>", methods=['GET', 'POST'])
def service(DATASET_NAME):
    
    if not session.get('NAME'):
        return redirect(url_for('login'))

    hospital = session['NAME']
    
    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]
    
    with open('label_dict.json',encoding = 'utf-8') as json_file:
        data = json.load(json_file)
        LABEL_DICT = data['LABEL_DICT']

    response = requests.post('http://dentiqub.iptime.org:5001/api')
    training_status = json.loads(response.text)['STATUS']
    if(len(training_status.split(' '))==4):
        training_percent = training_status.split(' ')[2]
    else:
        training_percent = 0
    datasetlist = []

    for data in dataset.find({hospital:'INSERTED'}).sort("NAME",pymongo.DESCENDING):
        datasetlist.append({'DATASET_NAME':data['NAME']})

    if DATASET_NAME == 'NONE':
        datalist = []
        archive_check = 'NONE'

    else:
        archive_check = dataset.find_one({'NAME':DATASET_NAME})['STATUS']
        if(len(os.listdir(BASE_DIR+DATASET_NAME)) != imagedata.find({'DATASET_NAME' : DATASET_NAME}).count()):
            for filename in os.listdir(BASE_DIR+DATASET_NAME):
                if not imagedata.find_one({'FILENAME':filename}):
                    imagedata.insert_one({'FILENAME':filename,'DATASET_NAME':DATASET_NAME, 'REVIEW_CHECK': 'UNREAD','CONFIRM_CHECK':'UNCONFIRM'})
        datalist = []
        for image in imagedata.find({'DATASET_NAME' : DATASET_NAME, 'HOSPITAL':hospital}):
            if not 'REVIEW_CHECK' in image:
                image['REVIEW_CHECK'] = 'UNREAD'
            if not 'CONFIRM_CHECK' in image:
                image['CONFIRM_CHECK'] = 'UNCONFIRM'
            if not 'DIALOG' in image:
                DIALOG = 'NOCOMMENT'
            else:
                DIALOG = 'COMMENT'
            if not 'NOTI' in image:
                image['NOTI'] = 'NONE'
            data = {
                    'FILENAME' : image['FILENAME'],
                    'REVIEW_CHECK': image['REVIEW_CHECK'],
                    'CONFIRM_CHECK': image['CONFIRM_CHECK'],
                    'DIALOG' : DIALOG,
                    'NOTI' : image['NOTI']
                    }
            datalist.append(data)
        
    return render_template('service.html', datalist = datalist, datasetlist = datasetlist, current_dataset = DATASET_NAME, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent, archive_check=archive_check, hospital = hospital)


@app.route("/_JSON", methods=['GET', 'POST'])
def sending_data():

    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]

    if(request.json['ORDER'] == 'REFLASH'):
        target = imagedata.find_one({'FILENAME':request.json['FILENAME']})
        if('DIALOG' in target):
            data = {'DIALOG' : target['DIALOG']}
        else:
            data = {'DIALOG' : []}
        if(not 'NOTI' in target):
            target['NOTI'] = 'NONE'
        if((str(request.json['ID']) == 'MANAGER') & (target['NOTI'] == 'MANAGER')):
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": { "NOTI": 'NONE' }})
        elif((str(request.json['ID']) != 'MANAGER') & (target['NOTI'] != 'MANAGER')):
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": { "NOTI": 'NONE' }})
        return json.dumps(json.dumps(data))

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
                print(EACH_LABEL)
            for EACH_LABEL in BBOX_LABEL:
                EACH_LABEL['left'] = int(EACH_LABEL['left'] / request.json['RATIO'])
                EACH_LABEL['top'] = int(EACH_LABEL['top'] / request.json['RATIO'])
                EACH_LABEL['width'] = int(EACH_LABEL['width'] / request.json['RATIO'])
                EACH_LABEL['height'] = int(EACH_LABEL['height'] / request.json['RATIO'])
            for EACH_LABEL in BBOX_LABEL:
                print(EACH_LABEL)
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {request.json['PARAMETER']:json.dumps(BBOX_LABEL)}})
        else:
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {request.json['PARAMETER']:str(request.json['SETVALUE'])}})

        # Dialog 데이터의 경우 Push로 데이터를 입력함
        if(request.json['PARAMETER'] == 'DIALOG'):
            now = datetime.now()
            dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$push": {request.json['PARAMETER']:[str(request.json['ID']), str(request.json['SETVALUE']),dt_string]}})
            if(str(request.json['ID']) == 'MANAGER'):
                imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": { "NOTI": 'HOSPITAL' }})
            else:
                imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": { "NOTI": 'MANAGER' }})

        if(request.json['PARAMETER'] == 'CONFIRM_CHECK'):
            # Confirm 관련 데이터셋의 경우 시간까지 기록함
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {'TIMESTAMP':str(pd.Timestamp('now'))}})
            # 전체 데이터셋이 Confirm인 경우 Dataset의 Status 바꿈
            if(not imagedata.find_one({'DATASET_NAME':request.json['DATASET'],'CONFIRM_CHECK':'UNCONFIRM'})):
                dataset.update_one({'NAME':request.json['DATASET']},{ "$set": { "STATUS": "ARCHIVE" } })

        return json.dumps('Success')

    if(request.json['ORDER'] == 'PREDICTION'):

        myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
        DENTIQUB = myclient["DENTIQUB"]
        imagedata = DENTIQUB["imagedata"]
        dataset = DENTIQUB["dataset"]

        target_image = os.path.join(BASE_DIR+request.json['DATASET'],request.json['FILENAME'])
        img = hanimread(target_image) #img = cv2.imread(target_image) 대체함. 한글경로 버그 수정
        data = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        mydata = {'img_name' : request.json['FILENAME'], 'data' : data}

        #병렬 코드
        boxes1 = pool.apply_async(request_prediction, (5101, mydata)) 
        boxes2 = pool.apply_async(request_prediction, (5102, mydata))
        #osteoporosis = pool.apply_async(request_prediction, (5201, mydata))
        boxes = boxes1.get()['BOXES'] + boxes2.get()['BOXES']
        boxes = bbox_duplicate_check(boxes)
        VERSION = boxes1.get()['VERSION']
        ARCHITECTURE = boxes1.get()['ARCHITECTURE']
        TRAINING_DATE = boxes1.get()['TRAINING_DATE']

        if(DEBUG_MODE == True):
            pass #print(boxes)

        #query = {'boxes':boxes, osteoporosis:'osteoporosis'}
        imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {'BBOX_PREDICTION':json.dumps(boxes),'BBOX_VERSION':VERSION, 'BBOX_ARCHITECTURE':ARCHITECTURE,'TRAINING_DATE':TRAINING_DATE}})

        return json.dumps(boxes)

    if(request.json['ORDER'] == 'START_TRAINING'):
        response = requests.post('http://dentiqub.iptime.org:5001/start')
        if(DEBUG_MODE == True):
            print(json.loads(response.text)['STATUS'])
        return json.dumps(json.loads(response.text)['STATUS'])

    if(request.json['ORDER'] == 'TRAINING_STATUS'):
        response = requests.post('http://dentiqub.iptime.org:5001/api')
        if(DEBUG_MODE == True):
            print(json.loads(response.text)['STATUS'])
        return json.dumps(json.loads(response.text)['STATUS'])

    if(request.json['ORDER'] == 'STATISTICS'):
        LABEL_RANK = label_statistics()
        PRECISION_DATA = prediction_statistics()
        return json.dumps({'LABEL_RANK':LABEL_RANK, 'PRECISION_DATA':PRECISION_DATA})

    if(request.json['ORDER'] == 'STATISTICS_DEMO'):
        LABEL_RANK = label_statistics_demo()
        PRECISION_DATA = prediction_statistics_demo()
        print('Sending Complete.')
        return json.dumps({'LABEL_RANK':LABEL_RANK, 'PRECISION_DATA':PRECISION_DATA})

@app.route('/database/<path:path>')
def database(path):
    return send_from_directory(BASE_DIR, path) 

@app.route('/thumb/<path:path>')
def thumb_database(path):
    return send_from_directory(BASE_DIR, path)

def label_statistics():
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]

    LABEL_LIST = []

    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        if ('BBOX_LABEL' in image):
            if((image['BBOX_LABEL']) == ''):
                image['BBOX_LABEL'] = '[]'
            BBOX_LABEL = json.loads(image['BBOX_LABEL'])
            for j in range(len(BBOX_LABEL)):
                class_name = str(BBOX_LABEL[j]['label'])
                LABEL_LIST.append(class_name)

    LABEL_COUNTER = collections.Counter(LABEL_LIST)
    LABEL_RANK = []

    for key, value in sorted(LABEL_COUNTER.items(), key=lambda item: item[1], reverse = True):
        LABEL_RANK.append((key, value))

    return LABEL_RANK

def label_statistics_demo():
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB_20200712"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]

    LABEL_LIST = []

    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        if ('BBOX_LABEL' in image):
            if((image['BBOX_LABEL']) == ''):
                image['BBOX_LABEL'] = '[]'
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

    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]

    CONFIRM_COUNT = 0
    PREDICT_COUNT = 0
    NO_PREDICT_COUNT = 0
    NOT_CHECKED = 0

    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        CONFIRM_COUNT+=1
        if 'PREDICTION_CHECK' in image:
            if (image['PREDICTION_CHECK'] == 'PREDICT'):
                PREDICT_COUNT+=1
            if (image['PREDICTION_CHECK'] == 'NO_PREDICT'):
                NO_PREDICT_COUNT+=1
            if (image['PREDICTION_CHECK'] == ''):
                NOT_CHECKED+=1
        

    CURRENT_PRECISION = int((PREDICT_COUNT+NO_PREDICT_COUNT)/(PREDICT_COUNT+NO_PREDICT_COUNT+NOT_CHECKED+0.1)*100)
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

def prediction_statistics_demo():

    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB_20200712"]
    imagedata = DENTIQUB["imagedata"]
    dataset = DENTIQUB["dataset"]

    CONFIRM_COUNT = 0
    PREDICT_COUNT = 0
    NO_PREDICT_COUNT = 0
    NOT_CHECKED = 0

    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        CONFIRM_COUNT+=1
        if 'PREDICTION_CHECK' in image:
            if (image['PREDICTION_CHECK'] == 'PREDICT'):
                PREDICT_COUNT+=1
            if (image['PREDICTION_CHECK'] == 'NO_PREDICT'):
                NO_PREDICT_COUNT+=1
            if (image['PREDICTION_CHECK'] == ''):
                NOT_CHECKED+=1
        

    CURRENT_PRECISION = int((PREDICT_COUNT+NO_PREDICT_COUNT)/(PREDICT_COUNT+NO_PREDICT_COUNT+NOT_CHECKED+0.1)*100)
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

def bbox2rect(bbox):
    top = bbox['top']
    down = bbox['top'] + bbox['height']
    left = bbox['left']
    right = bbox['left'] + bbox['width']
    return [[left, top], [left, down], [right, down], [right, top]] 

def calculate_cross(box_1, box_2):
    poly_1 = geometry.Polygon(box_1)
    poly_2 = geometry.Polygon(box_2)
    cross_a = poly_1.intersection(poly_2).area / poly_1.area
    cross_b = poly_1.intersection(poly_2).area / poly_2.area
    cross = cross_a if cross_a > cross_b else cross_b
    return cross

def combine_bbox(bbox_1, bbox_2):
    top_1 = bbox_1['top']
    down_1 = bbox_1['top'] + bbox_1['height']
    left_1 = bbox_1['left']
    right_1 = bbox_1['left'] + bbox_1['width']
    
    top_2 = bbox_2['top']
    down_2 = bbox_2['top'] + bbox_2['height']
    left_2 = bbox_2['left']
    right_2 = bbox_2['left'] + bbox_2['width']
    
    top = top_1 if top_1 < top_2 else top_2
    left = left_1 if left_1 < left_2 else left_2
    down = down_1 if top_1 > top_2 else down_2
    right = right_1 if right_1 > right_2 else right_2
    
    bbox = {'left' : left, 'top' : top, 'width':right-left, 'height':down - top, 'label' : bbox_1['label']}
    
    return bbox
    
def bbox_duplicate_check(boxes):
    while(1):
        if(len(boxes) > 1):
            check = False
            for i in range(len(boxes)):
                if(check):
                    break
                for j in range(i+1, len(boxes)):
                    if(boxes[i]['label'] == boxes[j]['label']):
                        if(calculate_cross(bbox2rect(boxes[i]), bbox2rect(boxes[j])) > 0.3):
                            print(calculate_cross(bbox2rect(boxes[i]), bbox2rect(boxes[j])))
                            boxes.append(combine_bbox(boxes[i], boxes[j]))
                            del boxes[j], boxes[i] 
                            check = True
                            break
        else:
            break
        if(check == False):
            break
    return boxes

def request_prediction(port, mydata):
    response = requests.post('http://dentiqub.iptime.org:'+str(port)+'/api', json=mydata)
    boxes = json.loads(response.text)['message']
    VERSION = json.loads(response.text)['VERSION']
    ARCHITECTURE = json.loads(response.text)['ARCHITECTURE']
    TRAINING_DATE = json.loads(response.text)['TRAINING_DATE']
    return {'BOXES':boxes, 'VERSION':VERSION, 'ARCHITECTURE':ARCHITECTURE, 'TRAINING_DATE':TRAINING_DATE}

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host = '0.0.0.0', port = 80)


