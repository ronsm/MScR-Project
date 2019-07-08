import pymongo
from pymongo import MongoClient
import pprint
import sys
from random import shuffle
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['RALT_RFID_HAR_System_3']

# user modifable variables
collection_name_prefix = None
num_tags = 244

def read_tag_epcs():
    with open("tags.txt") as f:
        tag_epcs = f.read().splitlines() 
    f.close()

    return tag_epcs

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return pointer

def get_collection_names(database_name):
    collections = db.collection_names()

    shuffle(collections)

    num_collections = len(collections)

    return num_collections, collections

def create_tag_dictionary(tag_epcs):
    tag_dictionary = {}

    for tag in tag_epcs:
        tag_dictionary['{}'.format(tag)] = 0

    return tag_dictionary

def count_tag_readings(tag_epcs, num_collections, collections, tag_dictionary):
    for i in range(0, num_collections):
        pointer = get_collection(collections[i])

        for document in pointer:
            for i in range(0, num_tags):
                epc = document["tags"][i]["_id"]
                peakRSSI = document["tags"][i]["peakRSSI"]

                if peakRSSI != "0":
                    tag_dictionary[epc] = tag_dictionary[epc] + 1

    return tag_dictionary

def create_map(tag_epcs, tag_dictionary):
    tag_pos_x = {}
    tag_pos_y = {}
    square_value = {}

    square_value['T1'] = 0
    square_value['T2']= 0
    square_value['T3'] = 0
    square_value['T4'] = 0
    square_value['T5'] = 0
    square_value['T6'] = 0
    square_value['T7'] = 0
    square_value['T8'] = 0
    square_value['T9'] = 0
    square_value['T10'] = 0
    square_value['T11'] = 0
    square_value['T12'] = 0
    square_value['T13'] = 0
    square_value['T14'] = 0
    square_value['T15'] = 0
    square_value['T16'] = 0
    square_value['T17'] = 0
    square_value['T18'] = 0
    square_value['T19'] = 0
    square_value['T20'] = 0
    square_value['T21'] = 0
    square_value['T22'] = 0
    square_value['T23'] = 0
    square_value['T24'] = 0

    for tag in tag_epcs:
        if tag[16:20] == "3333":
            seg = tag[20:25]
            
            if seg == "0001" or seg == "0002" or seg == "0009" or seg == "0010":
                square_value['T1'] = square_value['T1'] + tag_dictionary[tag]
            elif seg == "0003" or seg == "0004" or seg == "0011" or seg == "0012":
                square_value['T2'] = square_value['T2'] + tag_dictionary[tag]
            elif seg == "0005" or seg == "0006" or seg == "0013" or seg == "0014":
                square_value['T3'] = square_value['T3'] + tag_dictionary[tag]
            elif seg == "0007" or seg == "0008" or seg == "0015" or seg == "0016":
                square_value['T4'] = square_value['T4'] + tag_dictionary[tag]

            elif seg == "0029" or seg == "0030" or seg == "0035" or seg == "0036":
                square_value['T5'] = square_value['T5'] + tag_dictionary[tag]
            elif seg == "0031" or seg == "0032" or seg == "0037" or seg == "0038":
                square_value['T6'] = square_value['T6'] + tag_dictionary[tag]
            elif seg == "0033" or seg == "0034" or seg == "0039" or seg == "0040":
                square_value['T7'] = square_value['T7'] + tag_dictionary[tag]
            elif seg == "0017" or seg == "0018" or seg == "0019" or seg == "0020":
                square_value['T8'] = square_value['T8'] + tag_dictionary[tag]

            elif seg == "0041" or seg == "0042" or seg == "0043" or seg == "0044":
                square_value['T9'] = square_value['T9'] + tag_dictionary[tag]
            elif seg == "0021" or seg == "0022" or seg == "0023" or seg == "0024":
                square_value['T10'] = square_value['T10'] + tag_dictionary[tag]

            elif seg == "0045" or seg == "0046" or seg == "0047" or seg == "0048":
                square_value['T11'] = square_value['T11'] + tag_dictionary[tag]
            elif seg == "0025" or seg == "0026" or seg == "0027" or seg == "0028":
                square_value['T12'] = square_value['T12'] + tag_dictionary[tag]

            elif seg == "0049" or seg == "0050" or seg == "0057" or seg == "0058":
                square_value['T13'] = square_value['T13'] + tag_dictionary[tag]
            elif seg == "0051" or seg == "0052" or seg == "0059" or seg == "0060":
                square_value['T14'] = square_value['T14'] + tag_dictionary[tag]
            elif seg == "0053" or seg == "0054" or seg == "0061" or seg == "0062":
                square_value['T15'] = square_value['T15'] + tag_dictionary[tag]
            elif seg == "0055" or seg == "0056" or seg == "0063" or seg == "0064":
                square_value['T16'] = square_value['T16'] + tag_dictionary[tag]

            elif seg == "0065" or seg == "0066" or seg == "0073" or seg == "0074":
                square_value['T17'] = square_value['T17'] + tag_dictionary[tag]
            elif seg == "0067" or seg == "0068" or seg == "0075" or seg == "0076":
                square_value['T18'] = square_value['T18'] + tag_dictionary[tag]
            elif seg == "0069" or seg == "0070" or seg == "0077" or seg == "0078":
                square_value['T19'] = square_value['T19'] + tag_dictionary[tag]
            elif seg == "0071" or seg == "0072" or seg == "0079" or seg == "0080":
                square_value['T20'] = square_value['T20'] + tag_dictionary[tag]
            
            elif seg == "0081" or seg == "0082" or seg == "0089" or seg == "0090":
                square_value['T21'] = square_value['T21'] + tag_dictionary[tag]
            elif seg == "0083" or seg == "0084" or seg == "0091" or seg == "0092":
                square_value['T22'] = square_value['T22'] + tag_dictionary[tag]
            elif seg == "0085" or seg == "0086" or seg == "0093" or seg == "0094":
                square_value['T23'] = square_value['T23'] + tag_dictionary[tag]
            elif seg == "0087" or seg == "0088" or seg == "0095" or seg == "0096":
                square_value['T24'] = square_value['T24'] + tag_dictionary[tag]

    return square_value

def populate_matrix(tag_epcs, square_value):
    data = np.zeros((7, 4))

    data[0,0] = square_value['T1']
    data[0,1] = square_value['T2']
    data[0,2] = square_value['T3']
    data[0,3] = square_value['T4']

    data[1,0] = square_value['T5']
    data[1,1] = square_value['T6']
    data[1,2] = square_value['T7']
    data[1,3] = square_value['T8']

    data[2,0] = 0
    data[2,1] = 0
    data[2,2] = square_value['T9']
    data[2,3] = square_value['T10']

    data[3,0] = 0
    data[3,1] = 0
    data[3,2] = square_value['T11']
    data[3,3] = square_value['T12']

    data[4,0] = square_value['T13']
    data[4,1] = square_value['T14']
    data[4,2] = square_value['T15']
    data[4,3] = square_value['T16']

    data[5,0] = square_value['T17']
    data[5,1] = square_value['T18']
    data[5,2] = square_value['T19']
    data[5,3] = square_value['T20']

    data[6,0] = square_value['T21']
    data[6,1] = square_value['T22']
    data[6,2] = square_value['T23']
    data[6,3] = square_value['T24']

    data = data.astype(int)

    print(data)

    return data
        
def create_heatmap(data):
    ax = sns.heatmap(data, cmap='coolwarm', annot=True, fmt="d")

    plt.show()

def main():
    tag_epcs = read_tag_epcs()

    num_collections, collections = get_collection_names('RALT_RFID_HAR_System_3')

    tag_dictionary = create_tag_dictionary(tag_epcs)

    tag_dictionary = count_tag_readings(tag_epcs, num_collections, collections, tag_dictionary)

    square_value = create_map(tag_epcs, tag_dictionary)

    data = populate_matrix(tag_epcs, square_value)

    create_heatmap(data)

if __name__== "__main__":
  main()