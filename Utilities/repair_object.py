import subprocess
from moviepy.editor import VideoFileClip
import pymongo
from pymongo import MongoClient
import pprint
import sys
import matplotlib.pyplot as plt
import ruptures as rpt
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['ES_ALL-A']

# user defined variables
num_object_tags = 23

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def add_object_24(collection_name):
    collection, pointer = get_collection(collection_name)

    for document in pointer:
        object_tags = document["object_tags"]

        object_tag_24 = object_tags[22]
        object_tag_24["_id"] = "300833B2DDD9014099990024"
        object_tag_24["peakRSSI"] = 0

        object_tags.append(object_tag_24)
    
        # print(object_tags)

        query = {"_id": document["_id"]}
        add_cp = { "$set": { "object_tags": object_tags } }

        collection.update_one(query, add_cp)

def main():
    collection_names = []
    for i in range(0, 100):
        name = 'PID001-A' + str(i)
        collection_names.append(name)

    for collection in collection_names:
        add_object_24(collection)

if __name__== "__main__":
    main()