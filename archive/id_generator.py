# -*- coding: utf-8 -*-

import pymongo

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")


# DB 내용 확인
db = myclient["DENTIQUB"]
imagedata = db["imagedata"]
hospitaldata = db["hospitaldata"]


for image in imagedata.find():
    if('HOSPITAL' in image):
        NAME = image['HOSPITAL']
        ID = image['HOSPITAL']
        PASSWORD = '1'
        query = {'NAME' : NAME, 'ID': ID, 'PASSWORD' : PASSWORD}
        if(not hospitaldata.find_one({'NAME':NAME})):
            hospitaldata.insert_one(query)

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


