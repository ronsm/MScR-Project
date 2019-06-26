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
db = client['RALT_RFID_HAR_System']

# user defined variables
num_object_tags = 50

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def create_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def split_tags(collection_name):
    collection, pointer = get_collection(collection_name)

    for document in pointer:
        query = {"_id": document["_id"]}

        object_tags = []
        for i in range(0, len(document['tags'])):
            if '3333' in document['tags'][i]['_id']:
                object_tags.append(document['tags'][i])
                
                document_id = document['tags'][i]['_id']
                remove = {"$pull": {"tags": {"_id": document_id}}}
                # collection.update_one(query, remove)
        
        new_array = {"$set": {"object_tags": object_tags}}

        collection.update_one(query, new_array)

def get_object_timeseries(collection_name):
    collection, pointer = get_collection(collection_name)

    h = collection.count()
    w = num_object_tags
    object_tags_rssi = np.zeros((w, h), np.int32)

    i = 0
    for document in pointer:
        for j in range(0, num_object_tags):
            object_tags_rssi[j][i] = document['object_tags'][j]['peakRSSI']
        i = i + 1

    return object_tags_rssi

def change_point_detection(object_tags_rssi):
    object_tags_rssi_cp = np.zeros(object_tags_rssi.shape, np.int32)

    rows, cols = object_tags_rssi.shape
    for i in range(0, rows):
        signal = object_tags_rssi[i]

        algo = rpt.Pelt(model="l2").fit(signal)
        result = algo.predict(pen=10)

        # rpt.display(signal, result)
        # plt.show()

        print(result)

        for res in result:
            print(res)
            if res != cols:
                object_tags_rssi_cp[i][res] = 1

    return object_tags_rssi_cp

def write_change_points(collection_name, object_tags_rssi_cp):
    collection, pointer = get_collection(collection_name)

    rows, cols = object_tags_rssi_cp.shape

    object_tags_rssi_cp = object_tags_rssi_cp.tolist()

    for document in pointer:
        i = 0
        document_object_cp = []
        for j in range(0, rows):
            document_object_cp.append(object_tags_rssi_cp[j][i])
        i = i + 1

        query = {"_id": document["_id"]}
        add_cp = { "$set": { "object_tags_change_points": document_object_cp } }

        collection.update_one(query, add_cp)

def main():
    # clear the terminal
    print(chr(27) + "[2J")
    print("* * * * * * * * * * * * * * * * * * * *")
    print("* Object Activation Detection Module  *")
    print("* * * * * * * * * * * * * * * * * * * *")
    print("- Version 1.0")
    print("- Developed by Ronnie Smith")
    print("- github: @ronsm | email: ronnie.smith@ed.ac.uk | web: ronsm.com")
    print()

    num_arguments = len(sys.argv)

    if num_arguments == 2:
        collection_name = sys.argv[1]
    else:
        print("[MAIN][INFO] Invalid arguments. Usage: python3 object_activation_detection_module.py collection_name")
        exit()

    # split the 'tags' array in each snapshot into 'tags' and 'object_tags'
    print("[MAIN][STAT] Splitting tags into static and object tags in collection...", end="", flush=True)
    split_tags(collection_name)
    print("[DONE]")

    # get 2D array of tags and their timeseries of RSSI values
    print("[MAIN][STAT] Retrieving 2D array of tag RSSI timeseries...", end="", flush=True)
    object_tags_rssi = get_object_timeseries(collection_name)
    print("[DONE]")

    # use rupture changepoint detection library to detect significant changes in object RSSI values over time
    print("[MAIN][STAT] Detecting changepoints for each object tag...", end="", flush=True)
    object_tags_rssi_cp = change_point_detection(object_tags_rssi)
    print("[DONE]")
    
    # add changepoint detections to the dataset at each snapshot in the timeseries
    print("[MAIN][STAT] Adding change points to collection snapshots...", end="", flush=True)
    write_change_points(collection_name, object_tags_rssi_cp)
    print("[DONE]")

if __name__== "__main__":
    main()