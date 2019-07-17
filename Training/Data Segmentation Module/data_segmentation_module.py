import subprocess
from moviepy.editor import VideoFileClip
import pymongo
from pymongo import MongoClient
import pprint
import sys

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['RALT_RFID_HAR_System_4']

# configuration variables
time_between_snapshots_millis = 1000

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def get_all_collection_names():
    collections = db.collection_names()

    num_collections = len(collections)

    return num_collections, collections

def create_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def get_video_length(filename):
    clip = VideoFileClip(filename)
    duration_millis = clip.duration * 1000
    return duration_millis

def read_annotations(annotation_labels, annotation_times):
    f = open(annotation_times, "r")
    start_times = []
    end_times = []

    for x in f:
        splits = x.split('-')
        splits[1] = splits[1].rstrip('\n')

        start_times.append(splits[0])
        end_times.append(splits[1])

    f.close()

    f = open(annotation_labels, "r")
    labels = []

    for x in f:
        label = x.rstrip('\n')
        labels.append(label)

    return start_times, end_times, labels

def annotations_to_milliseconds(start_times, end_times):
    start_time_millis = []
    end_time_millis = []

    for i in range(0, len(start_times)):
        millis = get_sec(start_times[i])
        start_time_millis.append(millis)

        millis = get_sec(end_times[i])
        end_time_millis.append(millis)

    return start_time_millis, end_time_millis

def get_sec(human_time):
    h = 0
    m, s = human_time.split(':')
    seconds = int(h) * 3600 + int(m) * 60 + int(s)
    milliseconds = seconds * 1000

    return milliseconds

def get_label_for_snapshot(document_num, start_times, end_times, labels):
    found = 0
    label = 'err:label_error'

    document_time = (document_num * time_between_snapshots_millis) + time_between_snapshots_millis

    for i in range(0, len(start_times)):
        if found == 1:
            break
        if document_time > end_times[i]:
            found = 0
        else:
            label = labels[i]
            found = 1

    return label

def label_database(start_times, end_times, labels, collection_name):
    colelction, pointer = get_collection(collection_name)

    document_num = 0
    for document in pointer:
        query = { "_id": document["_id"]}
        activity_label = { "$set": { "activity_label": get_label_for_snapshot(document_num, end_times, end_times, labels) } }

        colelction.update_one(query, activity_label)

        document_num = document_num + 1

def split_collections(collection_name):
    collection, pointer = get_collection(collection_name)

    suffix = 1

    previousDocument = None
    for document in pointer:
        if previousDocument == None:
            previousDocument = document

        sub_collection = collection_name + '_' + str(suffix)

        if document["activity_label"] == previousDocument["activity_label"]:
            collection_new, pointer_new = get_collection(sub_collection)
            collection_new.insert_one(document)
        else:
            suffix = suffix + 1
            sub_collection = collection_name + '_' + str(suffix)
            collection_new, pointer_new = get_collection(sub_collection)
            collection_new.insert_one(document)

        previousDocument = document

def drop_transitions(collection_name):
    num_collections, collections = get_all_collection_names()

    for c in collections:
        collection, pointer = get_collection(c)
        collection_name_len = len(collection_name)
        prefix = c[:collection_name_len]

        if prefix == collection_name:
            for document in pointer:
                if document["activity_label"] == "TRA":
                    collection.drop()
                break
            
def main():
    # clear the terminal
    print(chr(27) + "[2J")
    print("* * * * * * * * * * * * * * *")
    print("* Data Segmentation Module  *")
    print("* * * * * * * * * * * * * * *")
    print("- Version 1.0")
    print("- Developed by Ronnie Smith")
    print("- github: @ronsm | email: ronnie.smith@ed.ac.uk | web: ronsm.com")
    print()

    # collection_name = 'Sample Dataset Segmentation'
    # annotation_labels = 'annotation_labels.txt'
    # annotation_times = 'annotation_times.txt'

    num_arguments = len(sys.argv)

    if num_arguments == 4:
        collection_name = sys.argv[1]
        annotation_labels = sys.argv[2]
        annotation_times = sys.argv[3]
    else:
        print("[MAIN][INFO] Invalid arguments. Usage: python3 data_segmentation_module.py collection_name annotation_labels annotation_times")
        exit()

    # read in annotation times from user-supplied .txt file
    print("[MAIN][STAT] Reading in annotation times...", end="", flush=True)
    start_times, end_times, labels = read_annotations(annotation_labels, annotation_times)
    print("[DONE]")
    
    # convert to milliseconds so that they are in same format as in database
    print("[MAIN][STAT] Converting annotation times to milliseconds...", end="", flush=True)
    start_times, end_times = annotations_to_milliseconds(start_times, end_times)
    print("[DONE]")

    # apply labels to the live database collection
    print("[MAIN][STAT] Applying labels to database collection...", end="", flush=True)
    label_database(start_times, end_times, labels, collection_name)
    print("[DONE]")

    # split the top-level collection into individual collections for each sample
    print("[MAIN][STAT] Splitting master collection into sample collections...", end="", flush=True)
    split_collections(collection_name)
    print("[DONE]")

    # remove transitioning (TRA) activities from the collection (optional)
    print("[MAIN][STAT] Removing transitional activities...", end="", flush=True)
    drop_transitions(collection_name)
    print("[DONE]")

if __name__== "__main__":
    main()