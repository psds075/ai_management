import os
import pandas as pd
import pymongo
import json

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
DENTIQUB = myclient["DENTIQUB_20200805"]
imagedata = DENTIQUB["imagedata"]
dataset = DENTIQUB["dataset"]

COUNT = 0


for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
    if ('BBOX_LABEL' in image):
        if((image['BBOX_LABEL']) == ''):
            image['BBOX_LABEL'] = '[]'
        BBOX_LABEL = json.loads(image['BBOX_LABEL'])
        for LABEL in BBOX_LABEL:
            
            if(LABEL['label'] == '하악관침범'):
                print(BBOX_LABEL)
                LABEL['label'] = '하악관중첩'
                COUNT = COUNT + 1
                print(BBOX_LABEL)
            
        BBOX_LABEL = json.dumps(BBOX_LABEL)
        query = {'FILENAME':image['FILENAME']}
        newvalues = { "$set": { "BBOX_LABEL": BBOX_LABEL } }
        imagedata.update_one(query, newvalues)
        
print(COUNT)

