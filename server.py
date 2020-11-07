# -*- coding: utf-8 -*-
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
from datetime import datetime, date, timedelta
pool = ThreadPool(processes=2)

app = Flask(__name__)
app.secret_key = b'123'
DEBUG_MODE = True
__VERSION__ = '0.1.13'

with open('env.json') as json_file:
    data = json.load(json_file)

BASE_DIR = data['BASE_DIR']
THUMB_DIR = data['THUMB_DIR']
DB_NAME = ''
DB_DIR = BASE_DIR + DB_NAME + '/'
TABLE_LIST = ['GUIDED_FILENAME','SEX','AGE','STATUS','TMJ_LEFT','TMJ_RIGHT','OSTEOPOROSIS','COMMENT_TEXT','REVIEW_CHECK','BBOX_LABEL', 'CONFIRM_CHECK','PREDICTION_CHECK','TIMESTAMP']


@app.route("/", methods=['GET', 'POST'])
def index():
    if 'NAME' in session:
        if(session['NAME'] == 'MANAGER'):
            return redirect(url_for('train'))
        elif(session['NAME'] == 'DEMO'):
            return redirect(url_for('demo'))
        elif(session['NAME'] == False):
            return redirect(url_for('main'))
        else:
            return redirect(url_for('service'))
    else:
        return redirect(url_for('main'))


# 일반 로그인 관련
@app.route("/main", methods=['GET', 'POST'])
def main():
    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    hospitaldata = DENTIQUB["hospitaldata"]
    imagedata = DENTIQUB["imagedata"]
    REQUEST = DENTIQUB["REQUEST"]

    today = str(date.today())
    today_total = 0
    for hospital in hospitaldata.find({}):
        if(today in hospital):
            today_total += hospital[today]

    total_hospital = hospitaldata.count_documents({})
    total_confirm = imagedata.count_documents({"CONFIRM_CHECK":"CONFIRM"})
    STATISTICS = {'today_total':today_total, 'total_hospital':total_hospital, 'total_confirm':total_confirm}
    
    if request.method == 'POST':
        NAME = request.form['NAME']
        CONTACT = request.form['CONTACT']
        MESSAGE = request.form['MESSAGE']
        HOSPITAL = request.form['HOSPITAL']
        REQUEST.insert_one({'NAME':NAME, 'CONTACT':CONTACT, 'MESSAGE':MESSAGE, 'HOSPITAL':HOSPITAL})
        ALERT = True
    else:
        ALERT = False
  
    return render_template('main.html', STATISTICS = STATISTICS, ALERT = ALERT)


# 일반 로그인 관련
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    hospitaldata = DENTIQUB["hospitaldata"]

    if request.method == 'POST':
        if(request.form['id']=='ai' and request.form['password'] == 'aiqub'):
            session['NAME'] = 'MANAGER'
            return redirect(url_for('train'))
        elif(request.form['id']=='demo' and request.form['password'] == 'aiqub'):
            session['NAME'] = 'DEMO'
            return redirect(url_for('demo'))
        elif(hospitaldata.find_one({'ID':request.form['id'], 'PASSWORD':request.form['password']})):
            session['NAME'] = hospitaldata.find_one({'ID':request.form['id']})['NAME']
            return redirect(url_for('service'))

    session.permanent = True

    return render_template('login.html')

@app.route('/logout')
def logout():
    session['NAME'] = False
    return redirect(url_for('login'))

@app.route("/train", defaults={'DATASET_NAME' : 'NONE'},methods=['GET', 'POST'])
@app.route("/train/<string:DATASET_NAME>", methods=['GET', 'POST'])
def train(DATASET_NAME):

    if not session['NAME'] == 'MANAGER':
        return redirect(url_for('login'))

    ID = session['NAME']

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
        # 해당 날짜에 UNCONFIRM이 없으면 CONFIRM 시키기
        query = {'DATASET_NAME':DATASET_NAME, 'CONFIRM_CHECK':'UNCONFIRM'}
        if not imagedata.find_one(query):
            query = {'NAME':DATASET_NAME}
            newvalues = { "$set": { "STATUS": "ARCHIVE" } }
            dataset.update_one(query, newvalues)
        else:
            query = {'NAME':DATASET_NAME}
            newvalues = { "$set": { "STATUS": "INSERTED" } }
            dataset.update_one(query, newvalues)
        
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
            if not 'HOSPITAL' in image:
                image['HOSPITAL'] = 'UNKNOWN'
            if not 'NAME' in image:
                image['NAME'] = 'UNKNOWN'
            data = {
                    'FILENAME' : image['FILENAME'],
                    'REVIEW_CHECK': image['REVIEW_CHECK'],
                    'CONFIRM_CHECK': image['CONFIRM_CHECK'],
                    'HOSPITAL' : image['HOSPITAL'],
                    'NAME' : image['NAME']
                    }
            datalist.append(data)
        
    return render_template('train.html', datalist = datalist, datasetlist = datasetlist, archivelist=archivelist, current_dataset = DATASET_NAME, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent, archive_check=archive_check, ID = ID)


@app.route("/comment",methods=['GET', 'POST'])
def comment():
    
    if not session['NAME'] == 'MANAGER':
        return redirect(url_for('login'))

    ID = session['NAME']

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
        if not 'NAME' in image:
            image['NAME'] = 'UNKNOWN'
        if not 'NOTI' in image:
            image['COMMENT'] = 'UNCOMMENT'
            image['NOTI'] = ''
            print('check1')
        elif image['NOTI'] == 'MANAGER':
            image['COMMENT'] = 'COMMENT'
            print('check2')
        else:
            image['COMMENT'] = 'UNCOMMENT'
            print('check3')
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
        
    return render_template('comment.html', datalist = datalist, datasetlist = datasetlist, archivelist=archivelist, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent, ID = ID)

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
                    'HOSPITAL' : image['HOSPITAL'],
                    'NAME' : image['NAME'],
                    'DIALOG' : DIALOG,
                    'NOTI' : image['NOTI']
                    }
            datalist.append(data)
        
    return render_template('service.html', datalist = datalist, datasetlist = datasetlist, current_dataset = DATASET_NAME, LABEL_DICT = json.dumps(LABEL_DICT, ensure_ascii=False), training_status = training_status, training_percent = training_percent, archive_check=archive_check, hospital = hospital)

@app.route("/hospital", methods=['GET', 'POST'])
def hospital():
    if not session.get('NAME'):
        return redirect(url_for('login'))
    USER = session['NAME']

    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    hospitaldata = DENTIQUB["hospitaldata"]
    hospitals = []

    today = date.today()
    yesterday = today - timedelta(days=1)
    print(yesterday)

    for hospital in hospitaldata.find({}).sort("NAME",pymongo.ASCENDING):
        hospital['WEEKLYIMAGES'] = 0
        for i in range(7):
            searchday = str(today - timedelta(days=i))
            if(searchday in hospital) : hospital['WEEKLYIMAGES'] += hospital[searchday]
        hospital['DAILYIMAGES'] = 0 if not str(today) in hospital else hospital[str(today)]
        if not "최근접속일" in hospital:
            hospital['최근접속일'] = 'NONE'
        if not "최근전송일" in hospital:
            hospital['최근전송일'] = 'NONE'
        hospitals.append(hospital)

    return render_template('hospital.html', USER=USER, Title = '병원 관리', hospitals = hospitals)


@app.route("/message", methods=['GET', 'POST'])
def message():
    if not session.get('NAME'):
        return redirect(url_for('login'))
    USER = session['NAME']

    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    REQUEST = DENTIQUB["REQUEST"]
    
    if('NAME' in request.args):
        NAME = request.args['NAME']
        REQUEST.delete_one({'NAME':NAME})
    
    MYREQUEST = REQUEST.find({})

    return render_template('message.html', USER=USER, Title = '설치 문의 관리', MYREQUEST = MYREQUEST)


@app.route("/model", methods=['GET', 'POST'])
def model():
    if not session.get('NAME'):
        return redirect(url_for('login'))
    USER = session['NAME']

    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]

    # 레이블 데이터 불러오기
    import collections
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
    LABEL_TABLE = []

    # 값으로 정렬
    for key, value in sorted(LABEL_COUNTER.items(), key=lambda item: item[0], reverse = False):
        LABEL_TABLE.append((key, value))

    # 정확도 통계 확인
    TODAY_STRING = datetime.now().strftime("%Y%m%d")

    DICT_TRUETOTAL = dict()
    DICT_NEGATIVETOTAL = dict()
    DICT_POSITIVETOTAL = dict()
    DICT_TRUENEGATIVE = dict()
    DICT_TRUEPOSITIVE = dict()

    DICT_SENSITIVITY = dict()
    DICT_SPECIFICITY = dict()
    DICT_PRECISION = dict()

    today = str(date.today())
    FROM_DATE = '2020-07-01'
    TO_DATE = today


    #Sensitivity 평가
    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        if 'BBOX_PREDICTION' in image:
            if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
                BBOX_LABEL_PREDICTION = json.loads(image['BBOX_PREDICTION'])
                PREDICTED_LABEL_SET = set()
                for LABEL in BBOX_LABEL_PREDICTION:
                    PREDICTED_LABEL_SET.add(LABEL['label'])
                
                BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                for LABEL in BBOX_LABEL:
                    if(not LABEL['label'] in DICT_TRUETOTAL):
                        DICT_TRUETOTAL[LABEL['label']] = 0
                        DICT_TRUEPOSITIVE[LABEL['label']] = 0
                        DICT_NEGATIVETOTAL[LABEL['label']] = 0
                        DICT_TRUENEGATIVE[LABEL['label']] = 0
                        DICT_POSITIVETOTAL[LABEL['label']] = 0
                    DICT_TRUETOTAL[LABEL['label']] += 1
                    if(LABEL['label'] in PREDICTED_LABEL_SET):
                        DICT_TRUEPOSITIVE[LABEL['label']] += 1

    for label in DICT_TRUETOTAL:
        DICT_SENSITIVITY[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_TRUETOTAL[label] + 0.001))

    #Specificity 평가
    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        if 'BBOX_PREDICTION' in image:
            if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
                
                BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                BBOX_PREDICTION = json.loads(image['BBOX_PREDICTION'])
                GROUNDTRUTH_LABEL_SET = set()
                PREDICTION_LABEL_SET = set()
                for LABEL in BBOX_LABEL:
                    GROUNDTRUTH_LABEL_SET.add(LABEL['label'])
                for LABEL in BBOX_PREDICTION:
                    PREDICTION_LABEL_SET.add(LABEL['label'])
                    
                DISEASE_DICT = dict(filter(lambda elem:elem[1]>=1, DICT_TRUEPOSITIVE.items()))
                    
                for DISEASE in list(DISEASE_DICT.keys()):
                    if(DISEASE not in GROUNDTRUTH_LABEL_SET):
                        DICT_NEGATIVETOTAL[DISEASE] += 1
                        if(DISEASE not in PREDICTION_LABEL_SET):
                            DICT_TRUENEGATIVE[DISEASE] += 1

    for label in sorted(DICT_SENSITIVITY.items(), key=lambda x: x[1], reverse=True):
        label = label[0]
        DICT_SPECIFICITY[label] = int((DICT_TRUENEGATIVE[label]*100) / (DICT_NEGATIVETOTAL[label] + 0.001))

    #Precision 평가
    for DISEASE in list(DICT_TRUEPOSITIVE.keys()):
        DICT_TRUEPOSITIVE[DISEASE] = 0

    for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
        if 'BBOX_PREDICTION' in image:
            if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
                
                BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                BBOX_PREDICTION = json.loads(image['BBOX_PREDICTION'])
                GROUNDTRUTH_LABEL_SET = set()
                PREDICTION_LABEL_SET = set()
                for LABEL in BBOX_LABEL:
                    GROUNDTRUTH_LABEL_SET.add(LABEL['label'])
                for LABEL in BBOX_PREDICTION:
                    PREDICTION_LABEL_SET.add(LABEL['label'])
                    
                for DISEASE in PREDICTION_LABEL_SET:
                    if(DISEASE in DICT_POSITIVETOTAL):
                        DICT_POSITIVETOTAL[DISEASE] += 1
                        if(DISEASE in GROUNDTRUTH_LABEL_SET):
                            DICT_TRUEPOSITIVE[DISEASE] += 1


    for label in sorted(DICT_SENSITIVITY.items(), key=lambda x: x[1], reverse=True):
        label = label[0]
        DICT_PRECISION[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_POSITIVETOTAL[label] + 0.001))

    COMFIRM_NUMBER = imagedata.count_documents({'CONFIRM_CHECK':"CONFIRM"})
    TOTAL_NUMBER = imagedata.count_documents({})

    print(COMFIRM_NUMBER, TOTAL_NUMBER)

    response = requests.post('http://dentiqub.iptime.org:5001/api')
    training_status = json.loads(response.text)['STATUS']

    if(len(training_status.split(' '))==4):
        training_percent = training_status.split(' ')[2]
    else:
        training_percent = 0

    return render_template('model.html', USER=USER, Title = '학습 모델 관리', LABEL_TABLE=LABEL_TABLE, SENSITIVITY=DICT_SENSITIVITY, SPECIFICITY=DICT_SPECIFICITY, PRECISION=DICT_PRECISION, training_status=training_status, training_percent=training_percent, COMFIRM_NUMBER=COMFIRM_NUMBER, TOTAL_NUMBER=TOTAL_NUMBER)


@app.route("/_JSON", methods=['GET', 'POST'])
def sending_data():

    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    DENTIQUB = myclient["DENTIQUB"]
    imagedata = DENTIQUB["imagedata"]
    hospitaldata = DENTIQUB["hospitaldata"]
    REQUEST = DENTIQUB["REQUEST"]
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

    if(request.json['ORDER'] == 'MODAL'):
        print(request.json['PARAMETER'])
        target = REQUEST.find_one({'NAME':request.json['PARAMETER']})
        result = {'NAME':target['NAME'],'CONTACT':target['CONTACT'], 'HOSPITAL':target['HOSPITAL'], 'MESSAGE':target['MESSAGE']}
        return json.dumps(json.dumps(result))

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
        if(request.json['ID'] != 'MANAGER'): #버그픽스
            today = str(date.today())
            hospitaldata.update_one({'NAME':request.json['ID']}, { "$set": {"최근접속일": today} })
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

        # Dialog 데이터의 경우 Push로 데이터를 입력함
        elif(request.json['PARAMETER'] == 'DIALOG'):
            now = datetime.now()
            dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$push": {request.json['PARAMETER']:[str(request.json['ID']), str(request.json['SETVALUE']),dt_string]}})
            if(str(request.json['ID']) == 'MANAGER'):
                imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": { "NOTI": 'HOSPITAL' }})
            else:
                imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": { "NOTI": 'MANAGER' }})

        elif(request.json['PARAMETER'] == 'CONFIRM_CHECK'):
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {request.json['PARAMETER']:str(request.json['SETVALUE'])}})
            # Confirm 관련 데이터셋의 경우 시간까지 기록함
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {'TIMESTAMP':str(pd.Timestamp('now'))}})
            # 전체 데이터셋이 Confirm인 경우 Dataset의 Status 바꿈
            if(not imagedata.find_one({'DATASET_NAME':request.json['DATASET'],'CONFIRM_CHECK':'UNCONFIRM'})):
                dataset.update_one({'NAME':request.json['DATASET']},{ "$set": { "STATUS": "ARCHIVE" } })

        else:
            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {request.json['PARAMETER']:str(request.json['SETVALUE'])}})

        return json.dumps('Success')

    if(request.json['ORDER'] == 'PREDICTION'):

        myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
        DENTIQUB = myclient["DENTIQUB"]
        imagedata = DENTIQUB["imagedata"]
        dataset = DENTIQUB["dataset"]

        query = {'DATASET_NAME':request.json['DATASET'], 'FILENAME':request.json['FILENAME']}
        target_image = imagedata.find_one(query)

        if('BBOX_PREDICTION' not in target_image) or (request.json['PARAMETER'] == 'FORCE'):
            imagepath = os.path.join(BASE_DIR+request.json['DATASET'],request.json['FILENAME'])
            img = hanimread(imagepath) #img = cv2.imread(target_image) 대체함. 한글경로 버그 수정
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
                #print(type(boxes), boxes)
                pass 

            imagedata.update_one({'FILENAME':request.json['FILENAME']}, { "$set": {'BBOX_PREDICTION':json.dumps(boxes),'BBOX_VERSION':VERSION, 'BBOX_ARCHITECTURE':ARCHITECTURE,'TRAINING_DATE':TRAINING_DATE}})

        else:
            boxes = json.loads(target_image['BBOX_PREDICTION'])
            
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


@app.route('/database/<path:path>')
def database(path):
    return send_from_directory(BASE_DIR, path) 

@app.route('/thumb/<path:path>')
def thumb_database(path):
    return send_from_directory(BASE_DIR, path)

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


