import subprocess
from moviepy.editor import VideoFileClip
import pymongo
from pymongo import MongoClient
import pprint
import sys

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
drop_labels = ["TRA", "bedroom_location_chair", "kitchen_location_worktop_stove"]
# drop_labels = ["TRA", "kitchen_location_worktop_corner", "kitchen_location_worktop_sink", "kitchen_location_worktop_sink", "kitchen_location_worktop_stove"]
# drop_labels = ["TRA", "bedroom_location_bed", "bedroom_location_drawers", "bedroom_location_wardrobe", "bedroom_location_chair", "bedroom_location_mirror"]

# configuration variables
time_between_snapshots_millis = 1000

def get_collection(db, collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def get_all_collection_names(db):
    collections = db.collection_names()

    num_collections = len(collections)

    return num_collections, collections

def create_collection(db, collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def get_video_length(filename):
    clip = VideoFileClip(filename)
    duration_millis = clip.duration * 1000
    return duration_millis

def read_annotations(annotation_times, annotation_location_labels, annotation_activity_labels, annotation_activity_indexes):
    f = open(annotation_times, "r")
    start_times = []
    end_times = []

    for x in f:
        splits = x.split('-')
        splits[1] = splits[1].rstrip('\n')

        start_times.append(splits[0])
        end_times.append(splits[1])

    f.close()

    # location_labels
    f = open(annotation_location_labels, "r")
    location_labels = []

    for x in f:
        label = x.rstrip('\n')
        location_labels.append(label)

    # activity_labels
    f = open(annotation_activity_labels, "r")
    activity_labels = []

    for x in f:
        label = x.rstrip('\n')
        activity_labels.append(label)

    # location_indexes
    f = open(annotation_activity_indexes, "r")
    activity_indexes = []

    for x in f:
        label = x.rstrip('\n')
        activity_indexes.append(label)

    return start_times, end_times, location_labels, activity_labels, activity_indexes

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

def get_activity_index_for_snapshot(document_num, start_times, end_times, activity_indexes):
    found = 0
    activity_index = 'err:activity_index_error'

    document_time = (document_num * time_between_snapshots_millis) + time_between_snapshots_millis

    for i in range(0, len(start_times)):
        if found == 1:
            break
        if document_time > end_times[i]:
            found = 0
        else:
            activity_index = activity_indexes[i]
            found = 1

    return activity_index

def label_location_database(start_times, end_times, db, location_labels, collection_name, activity_indexes):
    colelction, pointer = get_collection(db, collection_name)

    document_num = 0
    for document in pointer:
        query = { "_id": document["_id"]}
        location_label = { "$set": { "location_label": get_label_for_snapshot(document_num, end_times, end_times, location_labels) } }
        activity_index = { "$set": { "activity_index": get_activity_index_for_snapshot(document_num, end_times, end_times, activity_indexes) } }

        colelction.update_one(query, location_label)
        colelction.update_one(query, activity_index)

        document_num = document_num + 1

def label_activity_database(start_times, end_times, db, activity_labels, collection_name, activity_indexes):
    colelction, pointer = get_collection(db, collection_name)

    document_num = 0
    for document in pointer:
        query = { "_id": document["_id"]}
        activity_label = { "$set": { "activity_label": get_label_for_snapshot(document_num, end_times, end_times, activity_labels) } }
        activity_index = { "$set": { "activity_index": get_activity_index_for_snapshot(document_num, end_times, end_times, activity_indexes) } }

        colelction.update_one(query, activity_label)
        colelction.update_one(query, activity_index)

        document_num = document_num + 1

def split_location_collections(db, collection_name):
    collection, pointer = get_collection(db, collection_name)

    suffix = 0

    previousDocument = None
    for document in pointer:
        if previousDocument == None:
            previousDocument = document

        sub_collection = collection_name + '-L' + str(suffix)

        if document["location_label"] == previousDocument["location_label"]:
            collection_new, pointer_new = get_collection(db, sub_collection)
            collection_new.insert_one(document)
        else:
            suffix = suffix + 1
            sub_collection = collection_name + '-L' + str(suffix)
            collection_new, pointer_new = get_collection(db, sub_collection)
            collection_new.insert_one(document)

        previousDocument = document


def split_activity_collections(db, collection_name):
    collection, pointer = get_collection(db, collection_name)

    previousDocument = None
    for document in pointer:
        if previousDocument == None:
            previousDocument = document

        sub_collection = collection_name + '-A' + str(document["activity_index"])

        collection_new, pointer_new = get_collection(db, sub_collection)
        collection_new.insert_one(document)

        previousDocument = document

def drop_location_transitions(db, collection_name):
    num_collections, collections = get_all_collection_names(db)

    for c in collections:
        collection, pointer = get_collection(db, c)
        collection_name_len = len(collection_name)
        prefix = c[:collection_name_len]

        if prefix == collection_name:
            for document in pointer:
                location_label = document["location_label"]
                if location_label in drop_labels:
                    collection.drop()
                break

def drop_activity_transitions(db, collection_name):
    num_collections, collections = get_all_collection_names(db)

    collection, pointer = get_collection(db, collection_name)
    collection.drop()

    for c in collections:
        collection, pointer = get_collection(db, c)
        collection_name_len = len(collection_name)
        prefix = c[:collection_name_len]

        if prefix == collection_name:
            for document in pointer:
                activity_label = document["activity_label"]
                if activity_label == "TRA":
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

    num_arguments = len(sys.argv)

    if num_arguments == 3:
        database_prefix = sys.argv[1]
        collection_name = sys.argv[2]
    else:
        print("[MAIN][INFO] Invalid arguments. Usage: python3 data_segmentation_module.py database_prefix collection_name")
        exit()

    annotation_times = 'annotations/' + str(collection_name) + '_times.txt'
    annotation_location_labels = 'annotations/' + str(collection_name) + '_location_labels.txt'
    annotation_activity_labels = 'annotations/' + str(collection_name) + '_activity_labels.txt'
    annotation_activity_indexes = 'annotations/' + str(collection_name) + '_activity_indexes.txt'

    db_l_name = database_prefix + '-L'
    db_a_name = database_prefix + '-A'

    db_l = client[db_l_name]
    db_a = client[db_a_name]

    # read in annotation times from user-supplied .txt file
    print("[MAIN][STAT] Reading in annotation times...", end="", flush=True)
    start_times, end_times, location_labels, activity_labels, activity_indexes = read_annotations(annotation_times, annotation_location_labels, annotation_activity_labels, annotation_activity_indexes)
    print("[DONE]")
    
    # convert to milliseconds so that they are in same format as in database
    print("[MAIN][STAT] Converting annotation times to milliseconds...", end="", flush=True)
    start_times, end_times = annotations_to_milliseconds(start_times, end_times)
    print("[DONE]")

    # apply labels to the live database collections
    print("[MAIN][STAT] Applying labels to location database collection...", end="", flush=True)
    label_location_database(start_times, end_times, db_l, location_labels, collection_name, activity_indexes)
    print("[DONE]")

    print("[MAIN][STAT] Applying labels to activity database collection...", end="", flush=True)
    label_activity_database(start_times, end_times, db_a, activity_labels, collection_name, activity_indexes)
    print("[DONE]")

    # split the top-level collection into individual collections for each sample
    print("[MAIN][STAT] Splitting master location collection into sample collections...", end="", flush=True)
    split_location_collections(db_l, collection_name)
    print("[DONE]")

    print("[MAIN][STAT] Splitting master activity collection into sample collections...", end="", flush=True)
    split_activity_collections(db_a, collection_name)
    print("[DONE]")

    # remove transitioning (TRA) activities from the collection (optional)
    print("[MAIN][STAT] Removing location transitional activities...", end="", flush=True)
    drop_location_transitions(db_l, collection_name)
    print("[DONE]")

    print("[MAIN][STAT] Removing activity transitional activities...", end="", flush=True)
    drop_activity_transitions(db_a, collection_name)
    print("[DONE]")

if __name__== "__main__":
    main()