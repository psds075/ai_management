# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd
import json


# Connection
myclient = pymongo.MongoClient("mongodb://ai:1111@127.0.0.1:27017/")


# Image Data Update
DENTIQUB = myclient["DENTIQUB"]
imagedata = DENTIQUB["imagedata"]
dataset = DENTIQUB["dataset"]

dataset.update_many({},{ "$set": { "STATUS": "INSERTED" } })
imagedata.update_many({},{ "$set": { "CONFIRM_CHECK": "UNCONFIRM" } })




