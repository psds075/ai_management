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
'''
# HOSPITAL DB Read
for hospital in hospitaldata.find():
    print(hospital)
'''

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

'''
# 병원 별 접속 통계
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
'''

'''
# 금일 전송 데이터 수
today = str(date.today())
today_total = 0
for hospital in hospitaldata.find({}):
    if(today in hospital):
        today_total += hospital[today]

print(today_total)
print(hospitaldata.count_documents({}))
'''







