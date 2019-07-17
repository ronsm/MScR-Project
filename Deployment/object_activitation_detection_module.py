import subprocess
import pymongo
from pymongo import MongoClient
import pprint
import sys
import matplotlib.pyplot as plt
import ruptures as rpt
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

class object_activation_detection_module:
    def __init__(self, database_helper, num_object_tags, object_tag_epcs, object_tag_labels, object_tag_dict):
        print("[object_activation_detection_module][INFO] Starting up... ", end="", flush=True)
        self.database_helper = database_helper
        self.num_object_tags = num_object_tags
        self.object_tag_dict = object_tag_dict
        self.object_tag_epcs = object_tag_epcs
        self.object_tag_labels = object_tag_labels
        self.num_collections, self.collection_names = self.database_helper.get_all_collection_names()
        print("[OK]")

    def start(self):
        # split the 'tags' array in each snapshot into 'tags' and 'object_tags'
        print("[object_activation_detection_module][STAT] Splitting tags into static and object tags in collection... ", end="", flush=True)
        self.split_tags()
        print("[DONE]")

        # apply object labels to the database, using the object tag dictionary
        print("[object_activation_detection_module][STAT] Applying labels to object tags... ", end="", flush=True)
        self.label_tags()
        print("[DONE]")

        # get timeseries of object RSSI, calculate CPD, return results
        print("[object_activation_detection_module][STAT] Calculating and storing CPD for each sample... ", end="", flush=True)
        self.calculate_cpd_store()
        print("[DONE]")

        # generate the master list (list of lists) of object activiations by label
        print("[object_activation_detection_module][STAT] Generating master list (list of lists) of object activiations (by label)... ", end="", flush=True)
        master_list = self.generate_activated_object_lists()
        print("[DONE]")

        return master_list

    def split_tags(self):
        self.num_collections, self.collection_names = self.database_helper.get_all_collection_names()
        for collection in self.collection_names:
            self.database_helper.split_static_and_object_tags(collection)

    def label_tags(self):
        self.num_collections, self.collection_names = self.database_helper.get_all_collection_names()
        for collection in self.collection_names:
            collection, pointer = self.database_helper.get_collection(collection)

            for document in pointer:

                object_tag_labels = []
                for i in range(0, len(document['object_tags'])):
                    object_tag_labels.append(self.object_tag_dict[document['object_tags'][i]['_id']])

                query = {"_id": document["_id"]}
                add_cp = { "$set": { "object_tag_labels": object_tag_labels } }

                collection.update_one(query, add_cp)

    def calculate_cpd_store(self):
        for collection in self.collection_names:
            object_tags_rssi = self.get_object_timeseries(collection)
            object_tags_rssi_cp = self.change_point_detection(object_tags_rssi)
            self.write_change_points(collection, object_tags_rssi_cp)

    def get_object_timeseries(self, collection):
        collection, pointer = self.database_helper.get_collection(collection)

        h = collection.count()
        w = self.num_object_tags
        object_tags_rssi = np.zeros((w, h), np.int32)

        i = 0
        for document in pointer:
            for j in range(0, self.num_object_tags):
                object_tags_rssi[j][i] = document['object_tags'][j]['peakRSSI']
            i = i + 1

        return object_tags_rssi

    def change_point_detection(self, object_tags_rssi):
        object_tags_rssi_cp = np.zeros(object_tags_rssi.shape, np.int32)

        rows, cols = object_tags_rssi.shape
        for i in range(0, rows):
            signal = object_tags_rssi[i]

            if len(signal) > 1:
                algo = rpt.Pelt(model="l2").fit(signal)
                result = algo.predict(pen=10)

                # rpt.display(signal, result)
                # plt.show()

                for res in result:
                    if res != cols:
                        object_tags_rssi_cp[i][res] = 1
            else:
                object_tags_rssi_cp[i][0] = 0

        return object_tags_rssi_cp

    def write_change_points(self, collection_name, object_tags_rssi_cp):
        collection, pointer = self.database_helper.get_collection(collection_name)

        rows, cols = object_tags_rssi_cp.shape

        object_tags_rssi_cp = object_tags_rssi_cp.transpose()
        object_tags_rssi_cp = object_tags_rssi_cp.tolist()

        i = 0
        for document in pointer:
            query = {"_id": document["_id"]}
            add_cp = { "$set": { "object_tag_cps": object_tags_rssi_cp[i] } }

            collection.update_one(query, add_cp)
            i = i + 1

    def generate_activated_object_lists(self):
        master_list = []

        self.num_collections, self.collection_names = self.database_helper.get_all_collection_names()
        for collection in self.collection_names:
            collection, pointer = self.database_helper.get_collection(collection)

            collection_list = []
            for document in pointer:
                for i in range(0, self.num_object_tags):
                    if document["object_tag_cps"][i] == 1:
                        collection_list.append(document["object_tag_labels"][i])

            if len(collection_list) == 0:
                collection_list.append('none')
            collection_list = list(dict.fromkeys(collection_list))
            master_list.append(collection_list)

        return master_list