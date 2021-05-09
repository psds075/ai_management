# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 11:10:58 2020
@author: psds0
"""

import pymongo
import datetime

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")

# Back Up Database
# Data Initialization
# myclient.drop_database("DENTIQUB_BACKUP_TEST")

TODAY_STRING = datetime.datetime.now().strftime("%Y%m%d")
DENTIQUB = myclient["DENTIQUB"]
DENTIQUB_BACKUP = myclient["DENTIQUB_"+TODAY_STRING]

for collection in DENTIQUB.list_collection_names():
    dataset_original = DENTIQUB[collection]
    dataset_backup = DENTIQUB_BACKUP[collection]
    dataset_backup.insert_many(list(dataset_original.find()))


## DentiQub Dataset ##
'''
# Back Up
dataset_original = DENTIQUB["dataset"]
dataset_backup = DENTIQUB_BACKUP_TEST["dataset"]
dataset_backup.insert_many(list(dataset_original.find()))
'''
'''
# Create
dataset_backup = DENTIQUB_BACKUP_TEST["dataset"]
if(dataset_backup.find_one({'NAME':'TEST'})):
    print('중복입니다.')
else:
    dataset_backup.insert_one({'NAME':'TEST', 'STATUS' : 'INSERTED'})
'''

'''
# Read
dataset_backup = DENTIQUB_BACKUP_TEST["dataset"]
one = dataset_backup.find_one({'NAME':'TEST'})
print(one)
'''

'''
# Read All
DENTIQUB_BACKUP_TEST = myclient["DENTIQUB_20200712"]
dataset_backup = DENTIQUB_BACKUP_TEST["dataset"]
dataset_list = dataset_backup.find({})

for one in dataset_list:
    print(one)
'''

'''
# Update
dataset_backup = DENTIQUB_BACKUP_TEST["dataset"]
one = dataset_backup.update_one({'NAME':'TEST'},{ "$set": { "STATUS": "INSERTED" } })
print(one)
'''

'''
# Delete All
dataset_backup.delete_many({})
'''

'''
# Delete One
dataset_backup.delete_one({'NAME':'TEST'})
'''

'''
## DentiQub Image Data ##

# Quary Read
DENTIQUB = myclient["DENTIQUB"]
imagedata = DENTIQUB["imagedata"]
searched = imagedata.find({'CONFIRM_CHECK':'CONFIRM'})
print(searched.count())
'''



