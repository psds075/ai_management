# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
import json
import datetime

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
db = myclient["DENTIQUB"]
imagedata = db["imagedata"]


# DB에서 새로운 Image 추가하기
#query = {'HOSPITAL':'수원 예치과'}
#if not imagedata.find(query):
#    imagedata.insert_one(query)


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

'''
# DATASET DB UPDATE
query = {"DATASET_NAME": "20200921_OKC"}
newvalues = { "$set": {"CONFIRM_CHECK":"UNCONFIRM"}}
imagedata.update_many(query, newvalues)
'''

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


#전체 DB에서 가로 세로 비율이 1.9 이하인 이미지를 찾아서 CONFIRM 수정하기
'''
# -*- coding: utf-8 -*-
import os
import json
import cv2
import pymongo


with open('env.json') as json_file:
    data = json.load(json_file)

BASE_DIR = data['BASE_DIR']

myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
DENTIQUB = myclient["DENTIQUB_BACKUP"]
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




# 정확도 통계 확인
'''
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



#전체 DB에서 이미지 가로세로 범위 벗어난거 있는지 확인
# -*- coding: utf-8 -*-

#'''

#import os
#import json
#import cv2
#import pymongo
#import numpy as np
#
#with open('env.json') as json_file:
#    data = json.load(json_file)
#
#BASE_DIR = data['BASE_DIR']
#myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
#DENTIQUB_20201106 = myclient["DENTIQUB_20201106"]
#imagedata_20201106 = DENTIQUB_20201106["imagedata"]
#DENTIQUB = myclient["DENTIQUB"]
#imagedata = DENTIQUB["imagedata"]
#
#def imread_han(filePath):
#    stream = open( filePath.encode("utf-8") , "rb")
#    bytes = bytearray(stream.read())
#    numpyArray = np.asarray(bytes, dtype=np.uint8)
#    return cv2.imdecode(numpyArray , cv2.IMREAD_UNCHANGED)
#
#for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
#    filepath = BASE_DIR + image['DATASET_NAME'] + '/' + image['FILENAME']
#    
#    
#    #print(filepath, "is here.")
#    #img = imread_han(filepath)
#    #height = img.shape[0]
#    #width = img.shape[1]
#    if(image["BBOX_LABEL"] == ''):
#        image["BBOX_LABEL"] = '[]'
#    
#    labels = json.loads(image["BBOX_LABEL"])
#       
#    
#    '''
#    # 가로세로 마이너스 체크
#    for label in labels:
#        if(label['width'] <= 0):
#            print('width error.')
#            
#        if(label['height'] <= 0):
#            print('height error.')
#    
#    # 가로세로 길이 체크
#    for label in labels:
#        if(height - 2 < label['top']+label['height'] ):
#            print("Incorrect label exist on image ", image["FILENAME"], label)
#            label['height'] = height - label['top'] - 2
#            print("Revised", image["FILENAME"], label)
#            
#            
#            BBOX_LABEL = json.dumps(labels)
#            query = {'FILENAME': image['FILENAME']}
#            newvalues = { "$set": { "BBOX_LABEL": BBOX_LABEL}}
#            imagedata.update_one(query, newvalues)
#            
#            
#        if(width - 2 < label['left']+label['width'] ):
#            print("Incorrect label exist on image ", image["FILENAME"], label)
#            label['width'] = width - label['left'] - 2
#            print("Revised", image["FILENAME"], label)
#
#            
#            BBOX_LABEL = json.dumps(labels)
#            query = {'FILENAME': image['FILENAME']}
#            newvalues = { "$set": { "BBOX_LABEL": BBOX_LABEL}}
#            imagedata.update_one(query, newvalues)
#            
#            
#    # Left, Top 이 0인 경우 수정
#    for label in labels:
#        if(label['top'] <= 0):
#            print("Incorrect label exist on image ", image["FILENAME"], label)
#            label['top'] = 1
#            print("Revised", image["FILENAME"], label)
#            
#            
#            BBOX_LABEL = json.dumps(labels)
#            query = {'FILENAME': image['FILENAME']}
#            newvalues = { "$set": { "BBOX_LABEL": BBOX_LABEL}}
#            imagedata.update_one(query, newvalues)
#            
#            
#        if(label['left'] <= 0):
#            print("Incorrect label exist on image ", image["FILENAME"], label)
#            label['left'] = 1
#            print("Revised", image["FILENAME"], label)
#
#            
#            BBOX_LABEL = json.dumps(labels)
#            query = {'FILENAME': image['FILENAME']}
#            newvalues = { "$set": { "BBOX_LABEL": BBOX_LABEL}}
#            imagedata.update_one(query, newvalues)
#    '''
#    
#    ERROR_CHECK = False
#    
#    # 가로세로 Small Object Check
#    for label in labels:
#        if(label['width'] <= 50):
#            print(label['width'], 'width error.')
#            ERROR_CHECK = True
#            
#        if(label['height'] <= 50):
#            print(label['height'], 'height error.')
#            ERROR_CHECK = True
#    
#    if(ERROR_CHECK):
#        print('Revised')
#        query = {'FILENAME': image['FILENAME']}
#        newvalues = { "$set": { "CONFIRM_CHECK": 'UNCONFIRM'}}
#        imagedata.update_one(query, newvalues)
#        
#    

#'''


'''
#전체 DB에서 이미지 Dimention 일치 여부 확인
# -*- coding: utf-8 -*-


import os
import json
import cv2
import pymongo
import numpy as np


with open('env.json') as json_file:
    data = json.load(json_file)

BASE_DIR = data['BASE_DIR']

myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
DENTIQUB = myclient["DENTIQUB"]
hospitaldata = DENTIQUB["hospitaldata"]
imagedata = DENTIQUB["imagedata"]
dataset = db["dataset"]

def imread_han(filePath):
    stream = open( filePath.encode("utf-8") , "rb")
    bytes = bytearray(stream.read())
    numpyArray = np.asarray(bytes, dtype=np.uint8)
    return cv2.imdecode(numpyArray , cv2.IMREAD_UNCHANGED)

for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'})[:]:
    filepath = BASE_DIR + image['DATASET_NAME'] + '/' + image['FILENAME']
    if(os.path.isfile(filepath)):
        img = imread_han(filepath)
        height = img.shape[0]
        width = img.shape[1]
        if(len(img.shape) == 3):
            print(image['FILENAME'])
                
    else:
        print('No image error.')
'''


'''
def up_val(filename, variable):
    filename = list(filename)
    filename[-4] = '.'
    filename = ''.join(filename)
    query = {'FILENAME':filename}
    target = imagedata.find_one(query)
    if(variable in target):
        newvalues = { "$set": {variable:target["USER_READ"]+1}}
        imagedata.update_one(query, newvalues)
    else:
        newvalues = { "$set": {variable:1}}
        imagedata.update_one(query, newvalues)

def reset_val(filename, variable):
    filename = list(filename)
    filename[-4] = '.'
    filename = ''.join(filename)
    query = {'FILENAME':filename}
    newvalues = { "$set": {variable:0}}
    imagedata.update_one(query, newvalues)

filename = '20210503141042_315_jpg'
variable = "USER_READ"
'''

'''
# IMAGE DB Read One
query = {'FILENAME':'20210518101955'}
image = imagedata.find_one(query)
print(json.loads(image['BBOX_LABEL']))
'''

'''
images = imagedata.find({'BOT_UNREAD' : {"$exists" : True}}).sort("FILENAME",pymongo.DESCENDING)
for image in images:
    print(image['FILENAME'])

image_count = imagedata.count_documents({'BOT_UNREAD' : {"$exists" : True}})
print(image_count)
'''

'''
# Unset Field
query = {'HOSPITAL': '사과꽃치과'}
newvalues = { "$unset": {"USER_UNREAD":1, "BOT_UNREAD":1} }
imagedata.update_many(query, newvalues)
'''

