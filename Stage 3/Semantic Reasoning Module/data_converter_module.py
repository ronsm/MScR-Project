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
        self.write_dataset_input_files(num_collections, num_train_collections, num_test_collections, train_collections, test_collections)

    def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')

        if iteration == total: 
            print()

    def get_label(self, full_label):
        label = 0

        if full_label == "bedroom_location_bed":
            label = 2
        elif full_label == "bedroom_location_chair":
            label = 3
        elif full_label == "bedroom_location_wardrobe":
            label = 4
        elif full_label == "bedroom_location_drawers":
            label = 5
        elif full_label == "bedroom_location_mirror":
            label = 6
        elif full_label == "TRA":
            label = 1

        label = str(label)

        return label

    def create_dataset_files(self):
        # training set
        for tag in self.tag_epcs:
            with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "w") as f:
                f.write("")
                f.close

            if self.mode == 2:
                with open("dataset/train/input/{}_antenna.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

                with open("dataset/train/input/{}_phaseAngle.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

                with open("dataset/train/input/{}_velocity.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

        with open("dataset/train/y_train.txt".format(), "w") as f:
                f.write("")
                f.close

        # test set
        for tag in self.tag_epcs:
            with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "w") as f:
                f.write("")
                f.close

            if self.mode == 2:
                with open("dataset/test/input/{}_antenna.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

                with open("dataset/test/input/{}_phaseAngle.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

                with open("dataset/test/input/{}_velocity.txt".format(tag), "w") as f:
                    f.write("")
                    f.close

        with open("dataset/test/y_test.txt".format(), "w") as f:
                f.write("")
                f.close

    def write_dataset_input_files(self, num_collections, num_train_collections, num_test_collections, train_collections, test_collections):
        # write to training set
        print("[data_converter_module][INFO] Writing training set...")
        self.progress_bar(0, num_train_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)

        for i in range(0, num_train_collections):
            self.progress_bar(i + 1, num_train_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)
            collection, pointer = self.database_helper.get_collection(train_collections[i])

            labelled = 0
            sequence_length = 0

            # for every snapshot in sample (collection)
            for document in pointer:
                sequence_length = sequence_length + 1

                if labelled == 0:
                    label = self.get_label(document["activity_label"])

                    with open("dataset/train/y_train.txt".format(), "a") as f:
                        f.write(label)
                        f.write('\n')
                        f.close()

                    labelled = 1

                # appends value from current snapshot to every vector
                for i in range(0, self.num_tags):
                    epc = document["tags"][i]["_id"]
                    antenna = document["tags"][i]["antenna"]
                    peakRSSI = document["tags"][i]["peakRSSI"]
                    phaseAngle = document["tags"][i]["phaseAngle"]
                    velocity = document["tags"][i]["velocity"]

                    with open("dataset/train/input/{}_peakRSSI.txt".format(epc), "a") as f:
                        f.write(peakRSSI)
                        f.write("  ")
                        f.close()
                    
                    if self.mode == 2:
                        with open("dataset/train/input/{}_antenna.txt".format(epc), "a") as f:
                            f.write(antenna)
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
            if sequence_length < self.unified_sequence_length:
                sequence_length_diff = self.unified_sequence_length - sequence_length
                for tag in self.tag_epcs:
                    for i in range(0, sequence_length_diff):
                        with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "a") as f:
                            f.write("0")
                            f.write("  ")
                            f.close()

                        if self.mode == 2:
                            with open("dataset/train/input/{}_antenna.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

                            with open("dataset/train/input/{}_phaseAngle.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

                            with open("dataset/train/input/{}_velocity.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

            for tag in self.tag_epcs:
                with open("dataset/train/input/{}_peakRSSI.txt".format(tag), "a") as f:
                    f.write('\n')
                    f.close()

                if self.mode == 2:
                    with open("dataset/train/input/{}_antenna.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

                    with open("dataset/train/input/{}_phaseAngle.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

                    with open("dataset/train/input/{}_velocity.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

        print()

        # write to test set
        print("[data_converter_module][INFO] Writing test set...")
        self.progress_bar(0, num_test_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)

        for i in range(0, num_test_collections):
            self.progress_bar(i + 1, num_test_collections, prefix = 'Progress:', suffix = 'Complete', length = 50)
            collection, pointer = self.database_helper.get_collection(test_collections[i])

            labelled = 0
            sequence_length = 0

            for document in pointer:
                sequence_length = sequence_length + 1

                if labelled == 0:
                    label = self.get_label(document["activity_label"])

                    with open("dataset/test/y_test.txt".format(), "a") as f:
                        f.write(label)
                        f.write('\n')
                        f.close()

                    labelled = 1

                for i in range(0, self.num_tags):
                    epc = document["tags"][i]["_id"]
                    antenna = document["tags"][i]["antenna"]
                    peakRSSI = document["tags"][i]["peakRSSI"]
                    phaseAngle = document["tags"][i]["phaseAngle"]
                    velocity = document["tags"][i]["velocity"]

                    with open("dataset/test/input/{}_peakRSSI.txt".format(epc), "a") as f:
                        f.write(peakRSSI)
                        f.write("  ")
                        f.close()

                    if self.mode == 2:
                        with open("dataset/test/input/{}_antenna.txt".format(epc), "a") as f:
                            f.write(antenna)
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
            if sequence_length < self.unified_sequence_length:
                sequence_length_diff = self.unified_sequence_length - sequence_length
                for tag in self.tag_epcs:
                    for i in range(0, sequence_length_diff):
                        with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "a") as f:
                            f.write("0")
                            f.write("  ")
                            f.close()

                        if self.mode == 2:
                            with open("dataset/test/input/{}_antenna.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

                            with open("dataset/test/input/{}_phaseAngle.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

                            with open("dataset/test/input/{}_velocity.txt".format(tag), "a") as f:
                                f.write("0")
                                f.write("  ")
                                f.close()

            for tag in self.tag_epcs:
                with open("dataset/test/input/{}_peakRSSI.txt".format(tag), "a") as f:
                    f.write('\n')
                    f.close()

                if self.mode == 2:
                    with open("dataset/test/input/{}_antenna.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

                    with open("dataset/test/input/{}_phaseAngle.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

                    with open("dataset/test/input/{}_velocity.txt".format(tag), "a") as f:
                        f.write('\n')
                        f.close()

        print()