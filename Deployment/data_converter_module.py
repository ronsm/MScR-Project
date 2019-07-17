import pymongo
from pymongo import MongoClient
import pprint
import sys
from random import shuffle

class data_converter_module:
    def __init__(self, mode, database_helper, tag_epcs, num_tags, unified_sequence_length, train_test_ratio):
        print("[data_converter_module][STAT] Starting up... ", end="", flush=True)
        self.mode = mode
        self.database_helper = database_helper
        self.tag_epcs = tag_epcs
        self.num_tags = num_tags
        self.unified_sequence_length = unified_sequence_length
        self.train_test_ratio = train_test_ratio
        print("[OK]")

    def start(self):
        # get the names of all collections (sessions) in the given database
        print("[data_converter_module][STAT] Getting all collection (session) names from database... ", end="", flush=True)
        num_collections, collections, num_train_collections, num_test_collections, train_collections, test_collections = self.database_helper.get_split_collection_names(self.train_test_ratio)
        print("[DONE]")

        # create output files in 'Dataset' folder
        print("[data_converter_module][STAT] Creating (overwriting) output files in dataset folder... ", end="", flush=True)
        self.create_dataset_files()
        print("[DONE]")

        # write to dataset input files from database
        print("[data_converter_module][STAT] Writing to dataset files with database (MongoDB) data... ")
        self.write_dataset_input_files(num_collections, num_test_collections, test_collections)

    def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')

        if iteration == total: 
            print()

    def create_dataset_files(self):
        # test set
        for tag in self.tag_epcs:
            with open("unclassified/{}_peakRSSI.txt".format(tag), "w") as f:
                f.write("")
                f.close

            if self.mode == 2:
                with open("unclassified/{}_antenna.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

                with open("unclassified/{}_phaseAngle.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

                with open("unclassified/{}_velocity.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

    def write_dataset_input_files(self, num_collections, num_test_collections, test_collections):
        # write to test set
        print("[data_converter_module][INFO] Writing test set...")
        self.progress_bar(0, num_test_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)

        for i in range(0, num_test_collections):
            self.progress_bar(i + 1, num_test_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)
            collection, pointer = self.database_helper.get_collection(test_collections[i])

            sequence_length = 0

            for document in pointer:
                sequence_length = sequence_length + 1

                for i in range(0, self.num_tags):
                    epc = document["tags"][i]["_id"]
                    antenna = document["tags"][i]["antenna"]
                    peakRSSI = document["tags"][i]["peakRSSI"]
                    phaseAngle = document["tags"][i]["phaseAngle"]
                    velocity = document["tags"][i]["velocity"]

                    with open("unclassified/{}_peakRSSI.txt".format(epc), "a") as f:
                        f.write(peakRSSI)
                        f.write("  ")
                        f.close()

                    if self.mode == 2:
                        with open("unclassified/{}_antenna.txt".format(epc), "a") as f:
                            f.write(antenna)
                            f.write("  ")
                            f.close()

                        with open("unclassified/{}_phaseAngle.txt".format(epc), "a") as f:
                            f.write(str(phaseAngle))
                            f.write("  ")
                            f.close()

                        with open("unclassified/{}_velocity.txt".format(epc), "a") as f:
                            f.write(velocity)
                            f.write("  ")
                            f.close()

            # add new lines at end of every sample
            if sequence_length < self.unified_sequence_length:
                sequence_length_diff = self.unified_sequence_length - sequence_length
                for tag in self.tag_epcs:
                    for i in range(0, sequence_length_diff):
                        with open("unclassified/{}_peakRSSI.txt".format(tag), "a") as f:
                            f.write("0")
                            f.write("  ")
                            f.close()

                        if self.mode == 2:
                            with open("unclassified/{}_antenna.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

                            with open("unclassified/{}_phaseAngle.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

                            with open("unclassified/{}_velocity.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

            for tag in self.tag_epcs:
                with open("unclassified/{}_peakRSSI.txt".format(tag), "a") as f:
                    f.write('\n')
                    f.close()

                if self.mode == 2:
                    with open("unclassified/{}_antenna.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

                    with open("unclassified/{}_phaseAngle.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

                    with open("unclassified/{}_velocity.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

        print()