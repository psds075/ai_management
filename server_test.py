import os
import pandas as pd
import json
import collections

with open('label_dict.json',encoding = 'utf-8') as json_file:
    data = json.load(json_file)
    LABEL_DICT = data['LABEL_DICT']


'''
with open('env.json') as json_file:
    data = json.load(json_file)
    BASE_DIR = data['BASE_DIR']

# 폴더명 확인
    
folderlist = []
for DB_NAME in os.listdir(BASE_DIR):
    if(os.path.isdir(BASE_DIR+DB_NAME)):
        if not os.path.isfile(BASE_DIR+DB_NAME+'.xls'):
            df = pd.DataFrame({'FILENAME':os.listdir(BASE_DIR+DB_NAME)})
            df.to_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', index = False, float_format=None)
        folderlist.append(DB_NAME)

print(folderlist)
DATASET_NAME = folderlist[1]

LABEL_LIST = []

for forder in folderlist:
    df = pd.read_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1', na_rep='')
    for i in range(len(df)):
        if not df['BBOX_LABEL'].isnull().iloc[i]:
            BBOX_LABEL = json.loads(df['BBOX_LABEL'].iloc[i])
            for j in range(len(BBOX_LABEL)):
                LABEL_LIST.append(BBOX_LABEL[0]['label'])
            
DiseaseStatistics = collections.Counter(LABEL_LIST)
print(DiseaseStatistics)
'''

#BBOX_LABEL = json.loads(df['BBOX_LABEL'].iloc[i])
#BBOX_LABEL = json.loads(df['BBOX_LABEL'].iloc[0])
#print(len(BBOX_LABEL))

