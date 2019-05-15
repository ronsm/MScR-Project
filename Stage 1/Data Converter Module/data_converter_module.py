import pymongo
from pymongo import MongoClient
import pprint

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['RALT_RFID_HAR_System']

# user modifable variables
collection_name_prefix = 'Sample Dataset '
num_samples = 3

def get_collection(collection_name):
    collection = db[collection_name]
    pointer = collection.find({})
    return pointer

def print_collection(pointer):
    for document in pointer:
        pprint.pprint(document)

def create_dataset_files():
    files = ["antenna", "peakRSSI", "phaseAngle", "velocity"]

    for file in files:
        with open("dataset/train/input/{}.txt".format(file), "w") as f:
            f.write("")
            f.close

    with open("dataset/train/labels.txt".format(), "w") as f:
            f.write("")
            f.close

    for file in files:
        with open("dataset/test/input/{}.txt".format(file), "w") as f:
            f.write("")
            f.close

    with open("dataset/test/labels.txt".format(), "w") as f:
            f.write("")
            f.close

def write_dataset_input_files():    
    train_collections = 0.7 * num_samples
    train_collections = round(train_collections)
    test_collections = (num_samples-train_collections)
    
    files = ["antenna", "peakRSSI", "phaseAngle", "velocity"]

    # write to training set
    for i in range(1, train_collections + 1):
        collection_name = collection_name_prefix + str(i)
        pointer = get_collection(collection_name)

        for document in pointer:
            with open('dataset/train/input/antenna.txt', 'a') as f:
                f.write('some_antenna  ')
                f.close()
            with open('dataset/train/input/peakRSSI.txt', 'a') as f:
                f.write('some_peakRSSI  ')
                f.close()
            with open('dataset/train/input/phaseAngle.txt', 'a') as f:
                f.write('some_phaseAngle  ')
                f.close()
            with open('dataset/train/input/velocity.txt', 'a') as f:
                f.write('some_velocity  ')
                f.close()

        for file in files:
            with open("dataset/train/input/{}.txt".format(file), "a") as f:
                f.write('\n')
                f.close()

        # write to test set
    for i in range(train_collections + 1, num_samples + 1):
        collection_name = collection_name_prefix + str(i)
        pointer = get_collection(collection_name)

        for document in pointer:
            with open('dataset/test/input/antenna.txt', 'a') as f:
                f.write('some_antenna  ')
                f.close()
            with open('dataset/test/input/peakRSSI.txt', 'a') as f:
                f.write('some_peakRSSI  ')
                f.close()
            with open('dataset/test/input/phaseAngle.txt', 'a') as f:
                f.write('some_phaseAngle  ')
                f.close()
            with open('dataset/test/input/velocity.txt', 'a') as f:
                f.write('some_velocity  ')
                f.close()

            pprint.pprint(document["tags"][0]["_id"])

        for file in files:
            with open("dataset/test/input/{}.txt".format(file), "a") as f:
                f.write('\n')
                f.close()

# def get_data_test():
#     collection_name = 'Sample Dataset 1'
#     pointer = get_collection(collection_name)

#     for document in pointer:

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

    # create output files in 'Dataset' folder
    print("[MAIN] Creating (overwriting) output files in dataset folder...", end="", flush=True)
    create_dataset_files()
    print("[DONE]")

    # write to dataset input files from database
    print("[MAIN] Dataset will be split 70/30 for train/test sets.")
    print("[MAIN] Writing to dataset files with database (MongoDB) data...", end="", flush=True)
    write_dataset_input_files()
    print("[DONE]")
  
if __name__== "__main__":
  main()