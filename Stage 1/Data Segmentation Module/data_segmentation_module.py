import subprocess
from moviepy.editor import VideoFileClip
import pymongo
from pymongo import MongoClient
import pprint
import sys

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['RALT_RFID_HAR_System']

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return collection, pointer

def get_video_length(filename):
    clip = VideoFileClip(filename)
    durationMillis = clip.duration * 1000
    return durationMillis

def read_annotations(annotation_labels, annotation_times):
    f = open(annotation_times, "r")
    startTimes = []
    endTimes = []

    for x in f:
        splits = x.split('-')
        splits[1] = splits[1].rstrip('\n')

        startTimes.append(splits[0])
        endTimes.append(splits[1])

    f.close()

    f = open(annotation_labels, "r")
    labels = []

    for x in f:
        label = x.rstrip('\n')
        labels.append(label)

    return startTimes, endTimes, labels

def annotations_to_milliseconds(startTimes, endTimes):
    startTimesMillis = []
    endTimesMillis = []

    for i in range(0, len(startTimes)):
        millis = get_sec(startTimes[i])
        startTimesMillis.append(millis)

        millis = get_sec(endTimes[i])
        endTimesMillis.append(millis)

    return startTimesMillis, endTimesMillis

def get_sec(human_time):
    h = 0
    m, s = human_time.split(':')
    seconds = int(h) * 3600 + int(m) * 60 + int(s)
    milliseconds = seconds * 1000

    return milliseconds

def get_label_for_snapshot(time, startTimes, endTimes, labels):
    found = 0
    for i in range(0, len(startTimes)):
        if found == 1:
            break
        if int(time) > endTimes[i]:
            found = 0
        else:
            label = labels[i]
            found = 1

    return label

def label_database(startTimes, endTimes, labels, collection_name):
    colelction, pointer = get_collection(collection_name)

    for document in pointer:
        query = { "_id": document["_id"]}
        newValue = { "$set": { "activityLabel": get_label_for_snapshot(document["elapsedTime"], startTimes, endTimes, labels) } }

        colelction.update_one(query, newValue)

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
    startTimes, endTimes, labels = read_annotations(annotation_labels, annotation_times)
    print("[DONE]")
    
    # convert to milliseconds so that they are in same format as in database
    print("[MAIN][STAT] Converting annotation times to milliseconds...", end="", flush=True)
    startTimes, endTimes = annotations_to_milliseconds(startTimes, endTimes)
    print("[DONE]")

    # apply labels to the live database collection
    print("[MAIN][STAT] Applying labels to database collection...", end="", flush=True)
    label_database(startTimes, endTimes, labels, collection_name)
    print("[DONE]")

if __name__== "__main__":
    main()