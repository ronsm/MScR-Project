import pymongo
from pymongo import MongoClient
import pprint
import sys
from random import shuffle

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['RALT_RFID_HAR_System_5']

# user modifable variables
collection_name_prefix = None
num_tags = 253
unified_sequence_length = 24
train_test_ratio = 0.7

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return pointer

def get_collection_names(database_name):
    collections = db.collection_names()

    shuffle(collections)

    num_collections = len(collections)

    num_train_collections = train_test_ratio * num_collections
    num_train_collections = round(num_train_collections)
    num_test_collections = (num_collections-num_train_collections)

    train_collections = []
    test_collections = []

    for i in range(0, num_collections):
        if i < num_train_collections:
            train_collections.append(collections[i])
        else:
            test_collections.append(collections[i])

    return num_collections, collections, num_train_collections, num_test_collections, train_collections, test_collections

def progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')

    if iteration == total: 
        print()

def read_tag_epcs():
    with open("static.txt") as f:
        tag_epcs = f.read().splitlines() 
    f.close()

    return tag_epcs

def print_collection(pointer):
    for document in pointer:
        pprint.pprint(document)

def get_label(full_label):
    label = 0

    if full_label == "bedroom_location_bed":
        label = 0
    elif full_label == "bedroom_location_chair":
        label = 1
    elif full_label == "bedroom_location_wardrobe":
        label = 2
    elif full_label == "bedroom_location_drawers":
        label = 3
    elif full_label == "bedroom_location_mirror":
        label = 4
    elif full_label == "TRA":
        label = 5

    label = str(label)

    return label

def create_dataset_files(tag_epcs):
    # training set
    for tag in tag_epcs:
        with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "w") as f:
            f.write("")
            f.close

    with open("dataset/train/y_train.txt".format(), "w") as f:
            f.write("")
            f.close

    # test set
    for tag in tag_epcs:
        with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "w") as f:
            f.write("")
            f.close

    with open("dataset/test/y_test.txt".format(), "w") as f:
            f.write("")
            f.close

def write_dataset_input_files(tag_epcs, num_collections, num_train_collections, num_test_collections, train_collections, test_collections):
    # write to training set
    print("[write_dataset_input_files][INFO] Writing training set...")
    progress_bar(0, num_train_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for i in range(0, num_train_collections):
        progress_bar(i + 1, num_train_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)
        pointer = get_collection(train_collections[i])

        labelled = 0
        sequence_length = 0

        # for every snapshot in sample (collection)
        for document in pointer:
            sequence_length = sequence_length + 1

            if labelled == 0:
                label = get_label(document["activity_label"])

                with open("dataset/train/y_train.txt".format(), "a") as f:
                    f.write(label)
                    f.write('\n')
                    f.close()

                labelled = 1

            # appends value from current snapshot to every vector
            for i in range(0, num_tags):
                epc = document["tags"][i]["_id"]
                antenna = document["tags"][i]["antenna"]
                peakRSSI = document["tags"][i]["peakRSSI"]
                phaseAngle = document["tags"][i]["phaseAngle"]
                velocity = document["tags"][i]["velocity"]

                if epc[:20] != "300833B2DDD901409999":
                    with open("dataset/train/input/{}_peakRSSI.txt".format(epc), "a") as f:
                        f.write(peakRSSI)
                        f.write("  ")
                        f.close()

        # pad timeseries and add new lines at end of every sample
        if sequence_length < unified_sequence_length:
            sequence_length_diff = unified_sequence_length - sequence_length
            for tag in tag_epcs:
                for i in range(0, sequence_length_diff):
                    with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "a") as f:
                        f.write("0")
                        f.write("  ")
                        f.close()

        for tag in tag_epcs:
            with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

    print()

    # write to test set
    print("[write_dataset_input_files][INFO] Writing test set...")
    progress_bar(0, num_test_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for i in range(0, num_test_collections):
        progress_bar(i + 1, num_test_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)
        pointer = get_collection(test_collections[i])

        labelled = 0
        sequence_length = 0

        for document in pointer:
            sequence_length = sequence_length + 1

            if labelled == 0:
                label = get_label(document["activity_label"])

                with open("dataset/test/y_test.txt".format(), "a") as f:
                    f.write(label)
                    f.write('\n')
                    f.close()

                labelled = 1

            for i in range(0, num_tags):
                epc = document["tags"][i]["_id"]
                antenna = document["tags"][i]["antenna"]
                peakRSSI = document["tags"][i]["peakRSSI"]
                phaseAngle = document["tags"][i]["phaseAngle"]
                velocity = document["tags"][i]["velocity"]

                if epc[:20] != "300833B2DDD901409999":
                    with open("dataset/test/input/{}_peakRSSI.txt".format(epc), "a") as f:
                        f.write(peakRSSI)
                        f.write("  ")
                        f.close()

        # add new lines at end of every sample
        if sequence_length < unified_sequence_length :
            sequence_length_diff = unified_sequence_length - sequence_length
            for tag in tag_epcs:
                for i in range(0, sequence_length_diff):
                    with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "a") as f:
                        f.write("0")
                        f.write("  ")
                        f.close()

        for tag in tag_epcs:
            with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

    print()

def main():
    # clear the terminal
    print(chr(27) + "[2J")
    print("* * * * * * * * * * * * *")
    print("* Data Converter Module *")
    print("* * * * * * * * * * * * *")
    print("- Version 1.0")
    print("- Developed by Ronnie Smith")
    print("- github: @ronsm | email: ronnie.smith@ed.ac.uk | web: ronsm.com")
    print()

    num_arguments = len(sys.argv)

    global database_name

    if num_arguments != 1:
        print("[MAIN][INFO] Invalid arguments. Usage: python3 data_converter_module.py")
        exit()

    # read in tag EPCs
    print("[MAIN][STAT] Reading in tag EPCs from tags.txt...", end="", flush=True)
    tag_epcs = read_tag_epcs()
    print("[DONE]")

    # get the names of all collections (sessions) in the given database
    print("[MAIN][STAT] Getting all collection (session) names from database...", end="", flush=True)
    num_collections, collections, num_train_collections, num_test_collections, train_collections, test_collections = get_collection_names(database_name)
    print("[DONE]")

    # create output files in 'Dataset' folder
    print("[MAIN][STAT] Creating (overwriting) output files in dataset folder...", end="", flush=True)
    create_dataset_files(tag_epcs)
    print("[DONE]")

    # write to dataset input files from database
    print("[MAIN][INFO] Dataset will be split 70/30 for train/test sets.")
    print("[MAIN][STAT] Writing to dataset files with database (MongoDB) data...")
    write_dataset_input_files(tag_epcs, num_collections, num_train_collections, num_test_collections, train_collections, test_collections)

if __name__== "__main__":
  main()