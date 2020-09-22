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
DICT_FALSETOTAL = dict()
DICT_FALSENEGATIVE = dict()
DICT_FALSEPOSITIVE = dict()
DICT_TRUENEGATIVE = dict()
DICT_TRUEPOSITIVE = dict()
DICT_SENSITIVITY = dict()
DICT_SPECIFICITY = dict()

FROM_DATE = '2020-07-01'
TO_DATE = '2020-09-20'

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
                    DICT_FALSENEGATIVE[LABEL['label']] = 0
                    DICT_TRUEPOSITIVE[LABEL['label']] = 0
                DICT_TRUETOTAL[LABEL['label']] += 1
                if(LABEL['label'] in PREDICTED_LABEL_SET):
                    DICT_TRUEPOSITIVE[LABEL['label']] += 1
        
for label in DICT_TRUETOTAL:
    DICT_SENSITIVITY[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_TRUETOTAL[label] + 0.01))
    print("%s Sensitivity : %s %% (%s/%s)" % (label, str(DICT_SENSITIVITY[label]), str(DICT_TRUEPOSITIVE[label]), str(DICT_TRUETOTAL[label])))

#Specificity 평가
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
                    DICT_FALSENEGATIVE[LABEL['label']] = 0
                    DICT_TRUEPOSITIVE[LABEL['label']] = 0
                DICT_TRUETOTAL[LABEL['label']] += 1
                if(LABEL['label'] in PREDICTED_LABEL_SET):
                    DICT_TRUEPOSITIVE[LABEL['label']] += 1
        
for label in DICT_FALSETOTAL:
    DICT_SENSITIVITY[label] = int((DICT_TRUEPOSITIVE[label]*100) / (DICT_TRUETOTAL[label] + 0.01))
    print("%s Sensitivity : %s %% (%s/%s)" % (label, str(DICT_SENSITIVITY[label]), str(DICT_TRUEPOSITIVE[label]), str(DICT_TRUETOTAL[label])))


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


    
#print('CONFIRM_COUNT :',CONFIRM_COUNT)
#print('PREDICT_COUNT :',PREDICT_COUNT)
#print('NO_PREDICT_COUNT :',NO_PREDICT_COUNT)
#print('NOT_CHECKED :',NOT_CHECKED)
#print('TIME_RANGE : ',TIME_RANGE)


