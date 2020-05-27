import os
import pandas as pd
import json
import collections

# 디렉토리 불러오기
with open('env.json') as json_file:
    data = json.load(json_file)
    BASE_DIR = data['BASE_DIR']
    
# 폴더명 확인
folderlist = []
for DATASET_NAME in os.listdir(BASE_DIR):
    if(os.path.isdir(BASE_DIR+DATASET_NAME)):
        if os.path.isfile(BASE_DIR+DATASET_NAME+'.xls'):
            df = pd.read_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1', na_rep='')
            if 'CONFIRM_CHECK' in df:
                if((df['CONFIRM_CHECK'] == 'CONFIRM').sum() != len(df)):
                    folderlist.append(DATASET_NAME)
                    print(DATASET_NAME)
                else:
                    print(DATASET_NAME)

'''
if not os.path.isdir('train'):
    os.mkdir('train')
if not os.path.isdir('test'):
    os.mkdir('test')

LABEL_LIST = []
data_list = []

# 개수 카운팅
for DATASET_NAME in folderlist[:]:
    df = pd.read_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1', na_rep='')
    print((df['CONFIRM_CHECK'] == 'CONFIRM').sum() == len(df))
    
    
    if 'BBOX_LABEL' in df:
        for i in range(len(df)):
            if (not df['BBOX_LABEL'].isnull().iloc[i]) and (df['CONFIRM_CHECK'].iloc[i] == 'CONFIRM'):
                BBOX_LABEL = json.loads(df['BBOX_LABEL'].iloc[i])
                for j in range(len(BBOX_LABEL)):
                    class_name = str(BBOX_LABEL[j]['label'])
                    LABEL_LIST.append(class_name)


LABEL_COUNTER = collections.Counter(LABEL_LIST)
LABEL_RANK = []
LABEL_SET = set()

for key, value in sorted(LABEL_COUNTER.items(), key=lambda item: item[1], reverse = True):
    #if(value > 50):
    LABEL_RANK.append((key, value))
    LABEL_SET.add(key)

    '''