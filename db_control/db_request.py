# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
import json
import datetime

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
db = myclient["DENTIQUB"]
REQUEST = db["REQUEST"]

# CREATE
query = {'NAME':'김동현', 'CONTACT':'010-7334-3551','HOSPITAL':'만남 치과','MESSAGE':'얼른 설치해주세요.'}
REQUEST.insert_one(query)

# READ
query = {}
for myrequest in REQUEST.find(query):
    print(myrequest)

'''
# DELETE ONE
query = {'NAME' : '김동현'}
REQUEST.delete_one(query)
'''

'''
# DELETE ALL
REQUEST.delete_many({})
'''





'''
# IMAGE DB Read One
query = {'HOSPITAL':'수원 예치과'}
image = imagedata.find_one(query)
print(json.loads(image['BBOX_LABEL']))
'''

'''
# IMAGE DB Read Query
query = {'DIALOG':{'$exists':True}}
for image in imagedata.find(query):
    print(image)
'''

# DATASET DB UPDATE
#newvalues = { "$set": { "STATUS": "INSERTED" } }
#imagedata.update_one(query, newvalues)

#data = imagedata.find_one(query)
#print(data)

'''
# Dialog 추가(PUSH)하기 
now = datetime.now()
dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
query = {'FILENAME': '20200828105255_95000390.jpg'}
newvalues = { "$push": { "DIALOG": ['수원 예치과', '안녕하세요. 문의드려도 될까요?',dt_string] } }
imagedata.update_one(query, newvalues)

data = imagedata.find_one(query)
print(data)
'''

'''
# Dialog 리셋하기 
query = {'FILENAME': '20200828105255_95000390.jpg'}
newvalues = { "$set": { "DIALOG": [] } }
imagedata.update_one(query, newvalues)

data = imagedata.find_one(query)
print(data)
'''

'''
# Feedback 수정하기 
query = {'FILENAME': '20200717110202.315518_283.jpg'}
newvalues = { "$set": { "FEEDBACK": ['진단이 이상합니다.'] } }
imagedata.update_one(query, newvalues)

query = {'FILENAME': '20200717110202.315518_283.jpg'}
data = imagedata.find_one(query)
print(data)


# IMAGE DB Delete
#query = {'FILENAME':'TESTFILE.jpg'}
#imagedata.delete_one(query)
'''

'''
# IMAGE DB Delete ALL
hospitaldata.delete_many({})
'''

'''
# IMAGE DB Read Query
query = {'BBOX_PREDICTION':{'$exists':True}}
for image in imagedata.find(query):
    print(image['FILENAME'], image['DATASET_NAME'])
'''

'''
#전체 DB에서 가로 세로 비율이 1.9 이하인 이미지를 찾아서 CONFIRM 수정하기

# -*- coding: utf-8 -*-
import os
import json
import cv2
import pymongo


with open('env.json') as json_file:
    data = json.load(json_file)

BASE_DIR = data['BASE_DIR']

myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
DENTIQUB = myclient["DENTIQUB"]
hospitaldata = DENTIQUB["hospitaldata"]
imagedata = DENTIQUB["imagedata"]
dataset = db["dataset"]

count = 0


#전체 데이터 읽기
for data in dataset.find({}):
    
    DATASET_NAME = data['NAME']
    for image in imagedata.find({'DATASET_NAME' : DATASET_NAME, 'CONFIRM_CHECK':'CONFIRM'}):
        filepath = BASE_DIR + DATASET_NAME + '/' + image['FILENAME']
        if(os.path.isfile(filepath)):
            img = cv2.imread(filepath)
            height, width, channels = img.shape
            if(width/height < 1.88):
                count += 1
                print(width/height)
                #query = {'FILENAME': image['FILENAME'], 'DATASET_NAME':DATASET_NAME}
                #newvalues = { "$set": { "CONFIRM_CHECK": 'UNCONFIRM' } }
                #imagedata.update_one(query, newvalues)

print('change', count)
'''



'''
# 정확도 통계 확인
TODAY_STRING = datetime.datetime.now().strftime("%Y%m%d")

DICT_TRUETOTAL = dict()
DICT_NEGATIVETOTAL = dict()
DICT_POSITIVETOTAL = dict()
DICT_TRUENEGATIVE = dict()
DICT_TRUEPOSITIVE = dict()

DICT_SENSITIVITY = dict()
DICT_SPECIFICITY = dict()
DICT_PRECISION = dict()

today = str(datetime.date.today())
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

for label in sorted(DICT_SENSITIVITY.items(), key=lambda x: x[1], reverse=True):
    label = label[0]
    print("%s Sensitivity : %s %% (%s/%s)" % (label, str(DICT_SENSITIVITY[label]), str(DICT_TRUEPOSITIVE[label]), str(DICT_TRUETOTAL[label])))

print()
print()

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
    print("%s Specificity : %s %% (%s/%s)" % (label, str(DICT_SPECIFICITY[label]), str(DICT_TRUENEGATIVE[label]), str(DICT_NEGATIVETOTAL[label])))

print()
print()


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
                DICT_POSITIVETOTAL[DISEASE] += 1
                if(DISEASE in GROUNDTRUTH_LABEL_SET):
                    DICT_TRUEPOSITIVE[DISEASE] += 1


for label in sorted(DICT_SENSITIVITY.items(), key=lambda x: x[1], reverse=True):
    label = label[0]
    DICT_PRECISION[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_POSITIVETOTAL[label] + 0.001))
    if(DICT_POSITIVETOTAL[label] == 0):
        print("%s Precision : %s %% (%s/%s)" % (label, 'N/A', str(DICT_TRUEPOSITIVE[label]), str(DICT_POSITIVETOTAL[label])))
    else:
        print("%s Precision : %s %% (%s/%s)" % (label, str(DICT_PRECISION[label]), str(DICT_TRUEPOSITIVE[label]), str(DICT_POSITIVETOTAL[label])))

print()
print()

print('총 입력 데이터 수 :', imagedata.count_documents({}))
print('CONFIRM 수 :', imagedata.count_documents({'CONFIRM_CHECK':"CONFIRM"}))
'''


