# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
import os
import json
import pandas as pd

app = Flask(__name__)

DB_INFO = 'DB_INFO'
BASE_DIR = '/Project/8. Web Service/2. AI Management Solution/DB/'
DB_NAME = ''
DB_DIR = BASE_DIR + DB_NAME + '/'
DEBUG_MODE = False 
TABLE_LIST = ['GUIDED_FILENAME','SEX','AGE','STATUS','TMJ_LEFT','TMJ_RIGHT','OSTEOPOROSIS','COMMENT_TEXT','REVIEW_CHECK','BBOX_LABEL']

@app.route("/", methods=['GET', 'POST'])
def index():
    filelist = os.listdir(os.path.join('static','px'))
    return render_template('index.html',filelist=json.dumps(filelist))

@app.route("/viewer", defaults={'DATASET_NAME' : 'NONE'},methods=['GET', 'POST'])
@app.route("/viewer/<string:DATASET_NAME>", methods=['GET', 'POST'])
def viewer(DATASET_NAME):
    if DATASET_NAME == 'NONE':
        datalist = []
        datasetlist = []
        for DIR in os.listdir(BASE_DIR):
            if(os.path.isdir(BASE_DIR+DIR)):
                datasetlist.append({'DATASET_STATUS' : '','DATASET_NAME' : DIR})
        return render_template('viewer.html', datalist = datalist, datasetlist = datasetlist)
    else:
        global DB_DIR
        global DB_NAME
        DB_NAME = DATASET_NAME
        DB_DIR = BASE_DIR + DATASET_NAME + '/'
        if not os.path.isfile(BASE_DIR+DATASET_NAME+'.xls'):
            df = pd.DataFrame({'FILENAME':os.listdir(BASE_DIR+DATASET_NAME)})
            df.to_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1', index = False, float_format=None)
        df = pd.read_excel(BASE_DIR+DATASET_NAME+'.xls', sheet_name='Sheet1', na_rep='')
        df = df.fillna('')

        check_row = False
        for filename in os.listdir(BASE_DIR+DATASET_NAME):
            if not (filename in list(df.FILENAME)):
                df = df.append({"FILENAME":filename}, ignore_index=True)
        if(check_row == True):
            df.to_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', index = False, na_rep='', float_format=None)
            df = df.fillna('')

        check_column = False
        for column in TABLE_LIST:
            if not column in df.columns.tolist():
                check_column = True
                df[column] = ''
        if(check_column == True):
            df.to_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', index = False, na_rep='', float_format=None)
            df = df.fillna('')

        datalist = []
        for i in range(len(df)):
            if(df['REVIEW_CHECK'].iloc[i] == ''):
                df['REVIEW_CHECK'].iloc[i] = 'UNREAD'
            data = {'FILENAME' : df['FILENAME'].iloc[i],
                    'SEX' : str(df['SEX'].iloc[i]), 
                    'AGE' : str(df['AGE'].iloc[i]), 
                    'STATUS':'N/A',
                    'REVIEW_CHECK':str(df['REVIEW_CHECK'].iloc[i])
                    }
            datalist.append(data)
        datasetlist = []
        for DIR in os.listdir(BASE_DIR):
            if(os.path.isdir(BASE_DIR+DIR)):
                if not os.path.isfile(BASE_DIR+DIR+'.xls'):
                    df = pd.DataFrame({'FILENAME':os.listdir(BASE_DIR+DIR)})
                    df.to_excel(BASE_DIR+DIR+'.xls', sheet_name='Sheet1', index = False, float_format=None)
                datasetlist.append({'DATASET_STATUS' : '','DATASET_NAME' : DIR})
        return render_template('viewer.html', datalist = datalist, datasetlist = datasetlist)

@app.route("/_JSON", methods=['GET', 'POST'])
def sending_data():
    if(request.json['ORDER'] == 'LIST'):
        df = pd.read_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', na_rep='')
        datalist = []
        for i in range(len(df)):
            data = {'FILENAME' : df['FILENAME'].iloc[i], 
                    'SEX' : df['SEX'].iloc[i], 
                    'AGE' : str(df['AGE'].iloc[i]),
                    'STATUS':str(df['STATUS'].iloc[i]),
                    'TMJ_LEFT':str(df['TMJ_LEFT'].iloc[i]), 
                    'TMJ_RIGHT':str(df['TMJ_RIGHT'].iloc[i]),
                    'OSTEOPOROSI':str(df['OSTEOPOROSIS'].iloc[i]), 
                    'COMMENT_TEXT':str(df['COMMENT_TEXT'].iloc[i]),
                    'REVIEW_CHECK':str(df['REVIEW_CHECK'].iloc[i]),
                    'BBOX_LABEL':str(df['BBOX_LABEL'].iloc[i])
                    }
            datalist.append(data)
        return json.dumps(datalist)

    if(request.json['ORDER'] == 'TARGET'):
        df = pd.read_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1')
        df = df.fillna('')
        i = df.index[df['FILENAME'] == request.json['FILENAME']].tolist()[0]
        data = {'FILENAME' : df['FILENAME'].iloc[i], 
                'SEX' : df['SEX'].iloc[i], 
                'AGE' : str(df['AGE'].iloc[i]),
                'STATUS':str(df['STATUS'].iloc[i]),
                'TMJ_LEFT':str(df['TMJ_LEFT'].iloc[i]), 
                'TMJ_RIGHT':str(df['TMJ_RIGHT'].iloc[i]),
                'OSTEOPOROSIS':str(df['OSTEOPOROSIS'].iloc[i]), 
                'COMMENT_TEXT':str(df['COMMENT_TEXT'].iloc[i]),
                'REVIEW_CHECK':str(df['REVIEW_CHECK'].iloc[i]),
                'BBOX_LABEL':str(df['BBOX_LABEL'].iloc[i])
                }
        df['REVIEW_CHECK'].iloc[i]='READ'
        df.to_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', index = False, na_rep='', float_format=None)
        if(DEBUG_MODE == True):
            pass
            #print(data)
        return json.dumps(json.dumps(data))

    if(request.json['ORDER'] == 'LABEL'):
        print('check')
        df = pd.read_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', na_rep='')
        i = df.index[df['FILENAME'] == request.json['FILENAME']].tolist()[0]
        df[request.json['PARAMETER']].iloc[i]=str(request.json['SETVALUE'])
        if(request.json['PARAMETER'] == 'BBOX_LABEL'):
            BBOX_LABEL = json.loads(df[request.json['PARAMETER']].iloc[i])
            for EACH_LABEL in BBOX_LABEL:
                EACH_LABEL['left'] = int(EACH_LABEL['left'] / request.json['RATIO'])
                EACH_LABEL['top'] = int(EACH_LABEL['top'] / request.json['RATIO'])
                EACH_LABEL['width'] = int(EACH_LABEL['width'] / request.json['RATIO'])
                EACH_LABEL['height'] = int(EACH_LABEL['height'] / request.json['RATIO'])
                print(EACH_LABEL)
            df[request.json['PARAMETER']].iloc[i] = json.dumps(BBOX_LABEL)
        if(DEBUG_MODE == True):
            print(df)
            pass
        df.to_excel(BASE_DIR+DB_NAME+'.xls', sheet_name='Sheet1', index = False, na_rep='', float_format=None)
        return json.dumps('Success')

    if(request.json['ORDER'] == 'DB_INFO'):
        df = pd.read_excel(BASE_DIR+DB_INFO+'.xls', sheet_name='Sheet1', na_rep='')
        df = df.fillna('')
        i = df.index[df['DATASET_NAME'] == DB_NAME].tolist()[0]
        df['DATASET_STATUS'].iloc[i] = 'COMPLETE'
        df.to_excel(BASE_DIR+DB_INFO+'.xls', sheet_name='Sheet1', index = False, na_rep='', float_format=None)
        return json.dumps('Success')

@app.route('/database/<path:path>')
def database(path):
    return send_from_directory(DB_DIR, path) 

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port = 80)


