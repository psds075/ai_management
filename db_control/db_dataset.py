# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
db = myclient["DENTIQUB"]
dataset = db["dataset"]
imagedata = db["imagedata"]

'''
# DB에서 새로운 DATASET 추가하기
query = {'NAME':'TEST DATASET'}
if not dataset.find_one(query):
    dataset.insert_one(query)
'''


# DATASET DB Read One
#data = dataset.find_one(query)
#print(data)


'''
# 병원 별 DB 읽기
query = {'수원 예치과' : {'$regex':''}}
for data in dataset.find(query):
    print(data)
'''

# DATASET DB UPDATE
#query = {'NAME':'TEST DATASET'}
#newvalues = { "$set": { "STATUS": "INSERTED" } }
#dataset.update_one(query, newvalues)


# IMAGEDATA DB Delete
#dataset.delete_one(query)

'''
# IMAGEDATA DB Delete ALL
imagedata.delete_many({})
'''


# 병원 imagedata를 통해서 Dataset 내에 병원 현황 업데이트하기
# IMAGE DB Read Query
for image in imagedata.find():
    if('HOSPITAL' in image):
        if not dataset.find_one({'NAME':image['DATASET_NAME'], image['HOSPITAL']:'INSERTED'}):
            query = {'NAME':image['DATASET_NAME']}
            newvalues = { "$set": {image['HOSPITAL']: "INSERTED" } }
            dataset.update_one(query, newvalues)


# 병원 별 DB 읽기
query = {'천안 예치과' : {'$regex':''}}
for data in dataset.find(query):
    print(data)







