# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
import json
import datetime


def up_val(imagedata, filename, variable):
    filename = list(filename)
    filename[-4] = '.'
    filename = ''.join(filename)
    query = {'FILENAME':filename}
    target = imagedata.find_one(query)
    if(variable in target):
        newvalues = { "$set": {variable:target[variable]+1}}
        imagedata.update_one(query, newvalues)
    else:
        newvalues = { "$set": {variable:1}}
        imagedata.update_one(query, newvalues)

def reset_val(imagedata, filename, variable):
    filename = list(filename)
    filename[-4] = '.'
    filename = ''.join(filename)
    query = {'FILENAME':filename}
    newvalues = { "$set": {variable:0}}
    imagedata.update_one(query, newvalues)

if(__name__=="__main__"):

    # Connection
    myclient = pymongo.MongoClient("mongodb://ai:1111@dentiqub.iptime.org:27017/")
    db = myclient["DENTIQUB"]
    my_image = db["imagedata"]
        
    #filename = '20210503141042_315_jpg'
    #variable = "USER_READ"

    a = [1,2,3]

    for i in reversed(range(len(a))):
        if(a[i] == 2):
            del a[i]

    print(a)



