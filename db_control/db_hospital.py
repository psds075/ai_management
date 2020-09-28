# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
from datetime import datetime, date, timedelta

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
db = myclient["DENTIQUB"]
imagedata = db["imagedata"]
hospitaldata = db["hospitaldata"]

'''
# DB에서 새로운 Hospital 추가하기
for image in imagedata.find():
    if('HOSPITAL' in image):
        if(not hospitaldata.find_one({'NAME':NAME})):
            NAME = image['HOSPITAL']
            ID = image['HOSPITAL']
            PASSWORD = '1'
            query = {'NAME' : NAME, 'ID': ID, 'PASSWORD' : PASSWORD}
            hospitaldata.insert_one(query)
'''            

'''
# HOSPITAL DB Create
NAME = '도봉 예치과'
ID = '도봉 예치과'
PASSWORD = '1'
query = {'NAME' : NAME, 'ID': ID, 'PASSWORD' : PASSWORD}
if(not hospitaldata.find_one({'NAME':NAME})):
    hospitaldata.insert_one(query)
'''

# HOSPITAL DB Read
for hospital in hospitaldata.find():
    print(hospital)

'''
# HOSPITAL DB Delete
hospitaldata.delete_many({})
'''

'''
# UPDATE
# 최근접속일 업데이트
now = datetime.now()
NOW_STRING = now.strftime("%Y-%m-%d")
myquery = { "NAME": "UNKNOWN" }
newvalues = { "$set": { "최근접속일": NOW_STRING } }
hospitaldata.update_one(myquery, newvalues)

# 최근전송일 업데이트
now = datetime.now()
NOW_STRING = now.strftime("%Y-%m-%d")
myquery = { "NAME": "UNKNOWN" }
newvalues = { "$set": { "최근전송일": NOW_STRING } }
hospitaldata.update_one(myquery, newvalues)
'''

'''
today = date.today()
yesterday = today - timedelta(days=1)
print(yesterday)
'''


