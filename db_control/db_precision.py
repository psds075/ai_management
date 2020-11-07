import os
import pandas as pd
import json
import pymongo
import datetime

TODAY_STRING = datetime.datetime.now().strftime("%Y%m%d")

LABEL_DICT = set()

'''
with open('label_set_new.json') as json_file:
    LABEL_NEW = json.load(json_file)
    for SET in LABEL_NEW:
        LABEL_DICT.add(SET[0])
'''

with open('label_set_old.json') as json_file:
    LABEL_OLD = json.load(json_file)
    for SET in LABEL_OLD:
        LABEL_DICT.add(SET[0])

#print(LABEL_DICT)

# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
DENTIQUB = myclient["DENTIQUB"]
imagedata = DENTIQUB["imagedata"]
dataset = DENTIQUB["dataset"]

DICT_TRUETOTAL = dict()
DICT_NEGATIVETOTAL = dict()
DICT_POSITIVETOTAL = dict()
DICT_TRUENEGATIVE = dict()
DICT_TRUEPOSITIVE = dict()

DICT_SENSITIVITY = dict()
DICT_SPECIFICITY = dict()
DICT_PRECISION = dict()

today = str(datetime.date.today())
FROM_DATE = '2020-07-01'
TO_DATE = today


#Sensitivity 평가
for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
    if 'BBOX_PREDICTION' in image:
        if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
            BBOX_LABEL_PREDICTION = json.loads(image['BBOX_PREDICTION'])
            PREDICTED_LABEL_SET = set()
            for LABEL in BBOX_LABEL_PREDICTION:
                PREDICTED_LABEL_SET.add(LABEL['label'])
            
            BBOX_LABEL = json.loads(image['BBOX_LABEL'])
            for LABEL in BBOX_LABEL:
                if(not LABEL['label'] in DICT_TRUETOTAL):
                    DICT_TRUETOTAL[LABEL['label']] = 0
                    DICT_TRUEPOSITIVE[LABEL['label']] = 0
                    DICT_NEGATIVETOTAL[LABEL['label']] = 0
                    DICT_TRUENEGATIVE[LABEL['label']] = 0
                    DICT_POSITIVETOTAL[LABEL['label']] = 0
                DICT_TRUETOTAL[LABEL['label']] += 1
                if(LABEL['label'] in PREDICTED_LABEL_SET):
                    DICT_TRUEPOSITIVE[LABEL['label']] += 1
        
for label in DICT_TRUETOTAL:
    DICT_SENSITIVITY[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_TRUETOTAL[label] + 0.001))
    print("%s Sensitivity : %s %% (%s/%s)" % (label, str(DICT_SENSITIVITY[label]), str(DICT_TRUEPOSITIVE[label]), str(DICT_TRUETOTAL[label])))

print()
print()

#Specificity 평가
for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
    if 'BBOX_PREDICTION' in image:
        if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
            
            BBOX_LABEL = json.loads(image['BBOX_LABEL'])
            BBOX_PREDICTION = json.loads(image['BBOX_PREDICTION'])
            GROUNDTRUTH_LABEL_SET = set()
            PREDICTION_LABEL_SET = set()
            for LABEL in BBOX_LABEL:
                GROUNDTRUTH_LABEL_SET.add(LABEL['label'])
            for LABEL in BBOX_PREDICTION:
                PREDICTION_LABEL_SET.add(LABEL['label'])
                
            for DISEASE in list(DICT_TRUEPOSITIVE.keys()):
                if(DISEASE not in GROUNDTRUTH_LABEL_SET):
                    DICT_NEGATIVETOTAL[DISEASE] += 1
                    if(DISEASE not in PREDICTION_LABEL_SET):
                        DICT_TRUENEGATIVE[DISEASE] += 1


for label in DICT_NEGATIVETOTAL:
    DICT_SPECIFICITY[label] = int((DICT_TRUENEGATIVE[label]*100) / (DICT_NEGATIVETOTAL[label] + 0.001))
    print("%s Specificity : %s %% (%s/%s)" % (label, str(DICT_SPECIFICITY[label]), str(DICT_TRUENEGATIVE[label]), str(DICT_NEGATIVETOTAL[label])))

print()
print()


#Precision 평가
for DISEASE in list(DICT_TRUEPOSITIVE.keys()):
    DICT_TRUEPOSITIVE[DISEASE] = 0

for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
    if 'BBOX_PREDICTION' in image:
        if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
            
            BBOX_LABEL = json.loads(image['BBOX_LABEL'])
            BBOX_PREDICTION = json.loads(image['BBOX_PREDICTION'])
            GROUNDTRUTH_LABEL_SET = set()
            PREDICTION_LABEL_SET = set()
            for LABEL in BBOX_LABEL:
                GROUNDTRUTH_LABEL_SET.add(LABEL['label'])
            for LABEL in BBOX_PREDICTION:
                PREDICTION_LABEL_SET.add(LABEL['label'])
                
            for DISEASE in PREDICTION_LABEL_SET:
                if(DISEASE in DICT_POSITIVETOTAL):
                    DICT_POSITIVETOTAL[DISEASE] += 1
                    if(DISEASE in GROUNDTRUTH_LABEL_SET):
                        DICT_TRUEPOSITIVE[DISEASE] += 1


for label in DICT_NEGATIVETOTAL:
    DICT_PRECISION[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_POSITIVETOTAL[label] + 0.001))
    if(DICT_POSITIVETOTAL[label] == 0):
        print("%s Precision : %s %% (%s/%s)" % (label, 'N/A', str(DICT_TRUEPOSITIVE[label]), str(DICT_POSITIVETOTAL[label])))
    else:
        print("%s Precision : %s %% (%s/%s)" % (label, str(DICT_PRECISION[label]), str(DICT_TRUEPOSITIVE[label]), str(DICT_POSITIVETOTAL[label])))







