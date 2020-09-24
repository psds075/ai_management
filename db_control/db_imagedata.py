# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
import json
from datetime import datetime

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





