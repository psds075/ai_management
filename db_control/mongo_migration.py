# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
import json


# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@127.0.0.1:27017/")


# 디렉토리 불러오기
with open('env.json') as json_file:
    data = json.load(json_file)
    BASE_DIR = data['BASE_DIR']

# DB 초기화
DENTIQUB = myclient["DENTIQUB"]
imagedata = DENTIQUB["imagedata"]
imagedata.delete_many({})
imagedata.create_index('FILENAME', unique=True)

dataset = DENTIQUB["dataset"]
dataset.delete_many({})
dataset.create_index('NAME', unique=True)

# 폴더명 확인
folderlist = []
for DB_NAME in os.listdir(BASE_DIR):
    if(os.path.isdir(BASE_DIR+DB_NAME)):
        if os.path.isfile(BASE_DIR+DB_NAME+'.xls'):
            folderlist.append(DB_NAME)

# 데이터 입력
for DATASET_NAME in folderlist[:]:
    df = pd.read_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1')
    df = df.fillna('')
    df['DATASET_NAME'] = DATASET_NAME
    if('GUIDED_FILENAME' in df):
        del df['GUIDED_FILENAME']
    if('SEX' in df):
        del df['SEX']
    if('AGE' in df):
        del df['AGE']
    if('STATUS' in df):
        del df['STATUS']
    try:
        imagedata.insert_many(df.to_dict('records'))
    except:
        print('input error.')
    if not dataset.find_one({'NAME':DATASET_NAME}):
        dataset.insert_one({'NAME':DATASET_NAME,'STATUS':'INSERTED'})
    
    print(DATASET_NAME)


'''
# DB 내용 확인
db = myclient["DENTIQUB"]
imagedata = db["imagedata"]
'''


'''
for image in imagedata.find({'DATASET_NAME' : '20200123'}):
    print(image['FILENAME'])
'''

'''
for image in imagedata.find():
    print(image['FILENAME'])
'''

    
'''
# DB 리스트 확인
mydb = myclient["mydatabase"]
mycol = mydb["customers"]
print(myclient.list_database_names())
'''

'''
# Insert
mydb = myclient["mydatabase"]
mycol = mydb["customers"]
#mycol.create_index([('name', pymongo.ASCENDING)], unique=True)
mylist = [
  { "name": "Amy", "address": "Apple st 652"},
  { "name": "Hannah", "address": "Mountain 21"},
  { "name": "Michael", "address": "Valley 345"},
  { "name": "Sandy", "address": "Ocean blvd 2"},
  { "name": "Betty", "address": "Green Grass 1"},
  { "name": "Richard", "address": "Sky st 331"},
  { "name": "Susan", "address": "One way 98"},
  { "name": "Vicky", "address": "Yellow Garden 2"},
  { "name": "Ben", "address": "Park Lane 38"},
  { "name": "William", "address": "Central st 954"},
  { "name": "Chuck", "address": "Main Road 989"},
  { "name": "Viola", "address": "Sideway 1633"}
]

x = mycol.insert_many(mylist)
'''

'''
# DB 내용 확인
mydb = myclient["mydatabase"]
mycol = mydb["customers"]
for col in mycol.find({}):
    print(col)
'''

'''
# 프로파일
mydb = myclient["mydatabase"]
mycol = mydb["customers"]
result = mycol.profiles.create_index([('name', pymongo.ASCENDING)], unique=True)
sorted(list(mycol.profiles.index_information()))

mylist = [
  { "name": "Amy", "address": "Apple st 652"},
  { "name": "Hannah", "address": "Mountain 21"},
  { "name": "Michael", "address": "Valley 345"},
  { "name": "Sandy", "address": "Ocean blvd 2"},
  { "name": "Betty", "address": "Green Grass 1"},
  { "name": "Richard", "address": "Sky st 331"},
  { "name": "Susan", "address": "One way 98"},
  { "name": "Vicky", "address": "Yellow Garden 2"},
  { "name": "Ben", "address": "Park Lane 38"},
  { "name": "William", "address": "Central st 954"},
  { "name": "Chuck", "address": "Main Road 989"},
  { "name": "Viola", "address": "Sideway 1633"}
]


mydb = myclient["mydatabase"]
mycol = mydb["customers"]
try:
    mycol.profiles.insert_one({ "name": "Amy", "address": "Apple st 652"})
except:
    print('error occured')

print(sorted(list(mycol.index_information())))
'''



