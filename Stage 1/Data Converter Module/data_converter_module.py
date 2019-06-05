import pymongo
from pymongo import MongoClient
import pprint
import sys

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['RALT_RFID_HAR_System']

# user modifable variables
collection_name_prefix = None
num_samples = 7
num_tags = 150
unified_sequence_length = 128

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return pointer

def read_tag_epcs():
    with open("tags.txt") as f:
        tag_epcs = f.read().splitlines() 
    f.close()

    return tag_epcs

def print_collection(pointer):
    for document in pointer:
        pprint.pprint(document)

def create_dataset_files(tag_epcs):
    # training set
    for tag in tag_epcs:
        with open("dataset/train/input/{}_antenna.txt".format(tag), "w") as f:
            f.write("")
            f.close

        with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "w") as f:
            f.write("")
            f.close

        with open("dataset/train/input/{}_phaseAngle.txt".format(tag), "w") as f:
            f.write("")
            f.close

        with open("dataset/train/input/{}_velocity.txt".format(tag), "w") as f:
            f.write("")
            f.close

    with open("dataset/train/labels.txt".format(), "w") as f:
            f.write("")
            f.close

    # test set
    for tag in tag_epcs:
        with open("dataset/test/input/{}_antenna.txt".format(tag), "w") as f:
            f.write("")
            f.close

        with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "w") as f:
            f.write("")
            f.close

        with open("dataset/test/input/{}_phaseAngle.txt".format(tag), "w") as f:
            f.write("")
            f.close

        with open("dataset/test/input/{}_velocity.txt".format(tag), "w") as f:
            f.write("")
            f.close

    with open("dataset/test/labels.txt".format(), "w") as f:
            f.write("")
            f.close

def write_dataset_input_files(tag_epcs):    
    train_collections = 0.7 * num_samples
    train_collections = round(train_collections)
    test_collections = (num_samples-train_collections)

    # write to training set
    for i in range(1, train_collections + 1):
        collection_name = collection_name_prefix + "_" + str(i)
        pointer = get_collection(collection_name)

        labelled = 0
        sequence_length = 0

        for document in pointer:
            sequence_length = sequence_length + 1

            if labelled == 0:
                label = document["activityLabel"]

                with open("dataset/train/labels.txt".format(), "a") as f:
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

                with open("dataset/train/input/{}_antenna.txt".format(epc), "a") as f:
                    f.write(antenna)
                    f.write("  ")
                    f.close()

                with open("dataset/train/input/{}_peakRSSI.txt".format(epc), "a") as f:
                    f.write(peakRSSI)
                    f.write("  ")
                    f.close()

                with open("dataset/train/input/{}_phaseAngle.txt".format(epc), "a") as f:
                    f.write(str(phaseAngle))
                    f.write("  ")
                    f.close()

                with open("dataset/train/input/{}_velocity.txt".format(epc), "a") as f:
                    f.write(velocity)
                    f.write("  ")
                    f.close()

        # pad timeseries and add new lines at end of every sample
        for tag in tag_epcs:
            if sequence_length < unified_sequence_length:
                sequence_length_diff = unified_sequence_length - sequence_length
                for i in range(0, sequence_length_diff):
                    with open("dataset/train/input/{}_antenna.txt".format(tag), "a") as f:
                        f.write("0.0")
                        f.write("  ")
                        f.close()

                    with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "a") as f:
                        f.write("0.0")
                        f.write("  ")
                        f.close()

                    with open("dataset/train/input/{}_phaseAngle.txt".format(tag), "a") as f:
                        f.write("0.0")
                        f.write("  ")
                        f.close()

                    with open("dataset/train/input/{}_velocity.txt".format(tag), "a") as f:
                        f.write("0.0")
                        f.write("  ")
                        f.close()

            with open("dataset/train/input/{}_antenna.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

            with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

            with open("dataset/train/input/{}_phaseAngle.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

            with open("dataset/train/input/{}_velocity.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

    # write to test set
    for i in range(train_collections + 1, num_samples + 1):
        collection_name = collection_name_prefix + "_" + str(i)
        pointer = get_collection(collection_name)

        labelled = 0

        for document in pointer:
            if labelled == 0:
                label = document["activityLabel"]

                with open("dataset/test/labels.txt".format(), "a") as f:
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

                with open("dataset/test/input/{}_antenna.txt".format(epc), "a") as f:
                    f.write(antenna)
                    f.write("  ")
                    f.close()

                with open("dataset/test/input/{}_peakRSSI.txt".format(epc), "a") as f:
                    f.write(peakRSSI)
                    f.write("  ")
                    f.close()

                with open("dataset/test/input/{}_phaseAngle.txt".format(epc), "a") as f:
                    f.write(str(phaseAngle))
                    f.write("  ")
                    f.close()

                with open("dataset/test/input/{}_velocity.txt".format(epc), "a") as f:
                    f.write(velocity)
                    f.write("  ")
                    f.close()

        # add new lines at end of every sample
        for tag in tag_epcs:
            with open("dataset/test/input/{}_antenna.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

            with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

            with open("dataset/test/input/{}_phaseAngle.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

            with open("dataset/test/input/{}_velocity.txt".format(tag), "a") as f:
                f.write('\n')
                f.close()

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

    global collection_name_prefix

    if num_arguments == 2:
        collection_name_prefix = sys.argv[1]
    else:
        print("[MAIN][INFO] Invalid arguments. Usage: python3 data_converter_module.py collection_name")
        exit()

    # read in tag EPCs
    print("[MAIN][STAT] Reading in tag EPCs from tags.txt...", end="", flush=True)
    tag_epcs = read_tag_epcs()
    print("[DONE]")

    # create output files in 'Dataset' folder
    print("[MAIN][STAT] Creating (overwriting) output files in dataset folder...", end="", flush=True)
    create_dataset_files(tag_epcs)
    print("[DONE]")

    # write to dataset input files from database
    print("[MAIN][INFO] Dataset will be split 70/30 for train/test sets.")
    print("[MAIN][STAT] Writing to dataset files with database (MongoDB) data...", end="", flush=True)
    write_dataset_input_files(tag_epcs)
    print("[DONE]")
  
if __name__== "__main__":
  main()