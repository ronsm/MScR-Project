import pymongo
from pymongo import MongoClient
import pprint
import sys

from database_helper import database_helper
from data_converter_module import data_converter_module
from object_activitation_detection_module import object_activation_detection_module
from classification_module import classification_module
from semantic_reasoning_module import semantic_reasoning_module

class control_module:
    def __init__(self, location_database_name, activity_database_name):
        self.unified_sequence_length = 30
        self.num_static_tags = 232
        self.num_object_tags = 24
        self.train_test_ratio = 0.0
        self.dcvm_mode = 1
        self.ontology_name = 'sho.owl'
        self.ontology_IRI = 'file://' + self.ontology_name + '#'

        self.verbose = 0

        self.static_tag_epcs = self.load_static_tag_data()
        self.object_tag_epcs, self.object_tag_labels, self.object_tag_dict = self.load_object_tag_data()

        self.location_database_helper = database_helper(location_database_name)
        self.activity_database_helper = database_helper(activity_database_name)
        # self.data_converter_module = data_converter_module(self.dcvm_mode, self.location_database_helper, self.static_tag_epcs, self.num_static_tags, self.unified_sequence_length, self.train_test_ratio)
        self.object_activation_detection_module = object_activation_detection_module(self.activity_database_helper, self.num_object_tags, self.object_tag_epcs, self.object_tag_labels, self.object_tag_dict)
        self.classification_module = classification_module(self.unified_sequence_length)
        # self.semantic_reasoning_module = semantic_reasoning_module(self.verbose, self.ontology_name, self.ontology_IRI)

        self.start()

    def start(self):
        self.object_activation_detection_module.start()
        location_classifications = self.classification_module.start()

        # self.generate_location_activity_pairs(location_classifications)

        # location_classifications = [["kitchen_location_worktop_corner", "kitchen_location_worktop_sink", "kitchen_location_worktop_table", "kitchen_location_worktop_stove"],
        #                             ["kitchen_location_worktop_sink", "kitchen_location_worktop_corner", "kitchen_location_worktop_table", "kitchen_location_worktop_stove"],
        #                             ["bedroom_location_mirror", "bedroom_location_bed", "bedroom_location_drawers", "bedroom_location_wardrobe"],
        #                             ["bedroom_location_bed", "bedroom_location_mirror", "bedroom_location_drawers", "bedroom_location_wardrobe"],
        #                             ["kitchen_location_worktop_sink", "kitchen_location_worktop_corner", "kitchen_location_worktop_table", "kitchen_location_worktop_stove"],
        #                             ["bedroom_location_bed", "bedroom_location_mirror", "bedroom_location_drawers", "bedroom_location_wardrobe"]]
        # object_activations = [["object_kettle", "object_mug", "object_coffee_container", "object_tea_container", "object_plate"],
        #                     ["object_kettle", "object_mug", "object_coffee_container", "object_book"],
        #                     ["object_toothbrush"],
        #                     ["object_toothbrush"],
        #                     ["object_cake", "object_plate"],
        #                     []]


        # self.semantic_reasoning_module.start(location_classifications, object_activations)

    def load_static_tag_data(self):
        with open("knowledge/static.txt") as f:
            static_tag_epcs = f.read().splitlines() 
        f.close()

        return static_tag_epcs

    def load_object_tag_data(self):
        object_tag_epcs = []
        object_tag_labels = []
        object_tag_dict = {}
        with open("knowledge/object.txt") as f:
            lines = f.read().splitlines()
        f.close()

        for line in lines:
            splits = line.split(":", 1)
            object_tag_epcs.append(splits[0])
            object_tag_labels.append(splits[1])
            object_tag_dict[splits[0]] = splits[1]

        return object_tag_epcs, object_tag_labels, object_tag_dict

    def generate_location_activity_pairs(self, location_classifications):
        num_collections, location_collection_names = self.location_database_helper.get_all_collection_names()
        
        location_collection_names_expanded = []
        activity_collection_names = []
        master_list = []
        for collection_name in location_collection_names:
            collection, pointer = self.location_database_helper.get_collection(collection_name)

            previous_activity_index = 'none'
            for document in pointer:
                current_activity_index = document["activity_index"]

                if current_activity_index != previous_activity_index:
                    activity_collection_name = collection_name[:6] + '-A' + str(document["activity_index"])
                    # print(collection_name, document["activity_index"])
                    activated_objects = self.object_activation_detection_module.get_activited_objects_for_sample(activity_collection_name)

                    location_collection_names_expanded.append(collection_name)
                    master_list.append(activated_objects)
                    activity_collection_names.append(activity_collection_name)

                previous_activity_index = current_activity_index

        for i in range(0, len(location_collection_names_expanded)):
            print(location_collection_names_expanded[i], activity_collection_names[i], master_list[i])

# clear the terminal
print(chr(27) + "[2J")
print("* * * * * * * * * *")
print("* Control Module  *")
print("* * * * * * * * * *")
print("- Version 1.0")
print("- Developed by Ronnie Smith")
print("- github: @ronsm | email: ronnie.smith@ed.ac.uk | web: ronsm.com")
print()

num_arguments = len(sys.argv)

global database_name

if num_arguments == 3:
    location_database_name = sys.argv[1]
    activity_database_name = sys.argv[2]
else:
    print("[MAIN][INFO] Invalid arguments. Usage: python3 control_module.py location_database_name activity_database_name")
    exit()

control_module = control_module(location_database_name, activity_database_name)