# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@aiqub.iptime.org:27017/")


'''
# DentiQub User Account DB
# Define
class UserList(UserMixin, me.Document):
    Name = me.StringField()
    Id = me.StringField()
    Password = me.StringField()
    DateModified = me.DateTimeField(default=datetime.datetime.utcnow)

# Create
me.connect('DENTIQUB', host='mongodb://ai:1111@dentiqub.iptime.org:27017/?authSource=admin')
Name = 'AIQUB'
Id = 'aiqub'
Password = 'aiqub!'
if UserList.objects(Id=Id):
    print("중복입니다.")
else:
    user = UserList(Name=Name, Id=Id, Password=Password)
    user.save()
me.disconnect()

# Read
me.connect('DENTIQUB', host='mongodb://ai:1111@dentiqub.iptime.org:27017/?authSource=admin')
for item in UserList.objects():
    print(item.Id)
me.disconnect()

# Delete All
me.connect('DENTIQUB', host='mongodb://ai:1111@dentiqub.iptime.org:27017/?authSource=admin')
item = UserList.objects()
item.delete()
me.disconnect()
'''



'''
# 디렉토리 불러오기
with open('env.json') as json_file:
    data = json.load(json_file)
    BASE_DIR = data['BASE_DIR']

# 폴더명 확인
folderlist = []
for DB_NAME in os.listdir(BASE_DIR):
    if(os.path.isdir(BASE_DIR+DB_NAME)):
        if os.path.isfile(BASE_DIR+DB_NAME+'.xls'):
            folderlist.append(DB_NAME)

for DATASET_NAME in folderlist[0:1]:
    df = pd.read_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1')
    df = df.fillna('')
    df['DATASET_NAME'] = DATASET_NAME
    del df['GUIDED_FILENAME'], df['SEX'], df['AGE'], df['STATUS']
    db = myclient["DENTIQUB"]
    imagedata = db["imagedata"]
    imagedata.delete_many({})
    imagedata.create_index([('FILENAME', pymongo.ASCENDING)], unique=True)
    try:
        imagedata.insert_many(df.to_dict('records'))
    except:
        print('input error.')
'''

# DB 내용 확인
db = myclient["DENTIQUB"]
imagedata = db["imagedata"]

'''
for image in imagedata.find({'DATASET_NAME' : '20200123'}):
    print(image['FILENAME'])
'''

for image in imagedata.find():
    print(image['FILENAME'])

    
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



