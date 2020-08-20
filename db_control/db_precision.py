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

DICT_TOTAL = dict()
DICT_WRONG = dict()
DICT_RIGHT = dict()
DICT_PRECISION = dict()

FROM_DATE = '2020-08-01'
TO_DATE = '2020-08-20'

TOTAL = 0
RIGHT = 0
WRONG = 0

for image in imagedata.find({'CONFIRM_CHECK':'CONFIRM'}):
    
    if 'BBOX_PREDICTION' in image:
        if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
            BBOX_LABEL_PREDICTION = json.loads(image['BBOX_PREDICTION'])
            PREDICTED_LABEL_SET = set()
            for LABEL in BBOX_LABEL_PREDICTION:
                PREDICTED_LABEL_SET.add(LABEL['label'])
            
            BBOX_LABEL = json.loads(image['BBOX_LABEL'])
            for LABEL in BBOX_LABEL:
                if(not LABEL['label'] in DICT_TOTAL):
                    DICT_TOTAL[LABEL['label']] = 0
                    DICT_WRONG[LABEL['label']] = 0
                    DICT_RIGHT[LABEL['label']] = 0
                DICT_TOTAL[LABEL['label']] += 1
                if(LABEL['label'] in PREDICTED_LABEL_SET):
                    DICT_RIGHT[LABEL['label']] += 1
        
        
        
'''
        
    if 'TIMESTAMP' in image:
        
        #if(True):
        if((image['TIMESTAMP'] > FROM_DATE) & (image['TIMESTAMP'] < TO_DATE)):
            BBOX_LABEL = json.loads(image['BBOX_LABEL'])
            
            for LABEL in BBOX_LABEL:
                if(not LABEL['label'] in DICT_TOTAL):
                    DICT_TOTAL[LABEL['label']] = 0
                    DICT_WRONG[LABEL['label']] = 0
                    DICT_RIGHT[LABEL['label']] = 0
                DICT_TOTAL[LABEL['label']] += 1
                DICT_RIGHT[LABEL['label']] += 1
            
            
            # 전체 정확도
            TOTAL+=1
            if 'PREDICTION_CHECK' in image:
                if (image['PREDICTION_CHECK'] == 'PREDICT'):
                    RIGHT+=1
                    if ('BBOX_LABEL' in image):
                        if((image['BBOX_LABEL']) == ''):
                            image['BBOX_LABEL'] = '[]'
                        BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                        for LABEL in BBOX_LABEL:
                            if(not LABEL['label'] in DICT_TOTAL):
                                DICT_TOTAL[LABEL['label']] = 0
                                DICT_WRONG[LABEL['label']] = 0
                                DICT_RIGHT[LABEL['label']] = 0
                            DICT_TOTAL[LABEL['label']] += 1
                            DICT_RIGHT[LABEL['label']] += 1
                if (image['PREDICTION_CHECK'] == ''):
                    RIGHT+=1
                    if ('BBOX_LABEL' in image):
                        if((image['BBOX_LABEL']) == ''):
                            image['BBOX_LABEL'] = '[]'
                        BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                        for LABEL in BBOX_LABEL:
                            if(not LABEL['label'] in DICT_TOTAL):
                                DICT_TOTAL[LABEL['label']] = 0
                                DICT_WRONG[LABEL['label']] = 0
                                DICT_RIGHT[LABEL['label']] = 0
                            DICT_TOTAL[LABEL['label']] += 1
                            DICT_RIGHT[LABEL['label']] += 1                                 
                if (image['PREDICTION_CHECK'] == 'NO_PREDICT'):
                    WRONG+=1
                    if ('BBOX_LABEL' in image):
                        if((image['BBOX_LABEL']) == ''):
                            image['BBOX_LABEL'] = '[]'
                        BBOX_LABEL = json.loads(image['BBOX_LABEL'])
                        for LABEL in BBOX_LABEL:
                            if(not LABEL['label'] in DICT_TOTAL):
                                DICT_TOTAL[LABEL['label']] = 0
                                DICT_WRONG[LABEL['label']] = 0
                                DICT_RIGHT[LABEL['label']] = 0
                            DICT_TOTAL[LABEL['label']] += 1
                            DICT_WRONG[LABEL['label']] += 1
                     
'''

'''
# 종합 정확도
CURRENT_PRECISION = int((RIGHT*100)/(TOTAL+0.1))
CURRENT_DATE = 'NOW'
print('CURRENT_PRECISION : ',CURRENT_PRECISION)
'''

for label in DICT_TOTAL:
    DICT_PRECISION[label] = int((DICT_RIGHT[label]*100) / (DICT_TOTAL[label] + 0.01))
    print("%s 정확도 : %s %% (%s/%s)" % (label, str(DICT_PRECISION[label]), str(DICT_RIGHT[label]), str(DICT_TOTAL[label])))
    
#print('CONFIRM_COUNT :',CONFIRM_COUNT)
#print('PREDICT_COUNT :',PREDICT_COUNT)
#print('NO_PREDICT_COUNT :',NO_PREDICT_COUNT)
#print('NOT_CHECKED :',NOT_CHECKED)
#print('TIME_RANGE : ',TIME_RANGE)


