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

count = 0

for image in imagedata.find({'DATASET_NAME' : '20200914'}):
    filepath = BASE_DIR + '20200914' + '/' + image['FILENAME']
    if(os.path.isfile(filepath)):
        img = cv2.imread(filepath)
        height, width, channels = img.shape
        if(width/height < 1.88):
            count += 1
            print(width/height)
            print(image)

print('count', count)



