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
    def __init__(self, database_name):
        self.unified_sequence_length = 24
        self.num_static_tags = 244
        self.num_object_tags = 17
        self.train_test_ratio = 0.0
        self.dcvm_mode = 1
        self.ontology_name = 'sho.owl'
        self.ontology_IRI = 'file://' + self.ontology_name + '#'

        self.verbose = 0

        self.static_tag_epcs = self.load_static_tag_data()
        self.object_tag_epcs, self.object_tag_labels, self.object_tag_dict = self.load_object_tag_data()

        # self.database_helper = database_helper(database_name)
        # self.data_converter_module = data_converter_module(self.dcvm_mode, self.database_helper, self.static_tag_epcs, self.num_static_tags, self.unified_sequence_length, self.train_test_ratio)
        # self.object_activation_detection_module = object_activation_detection_module(self.database_helper, self.num_object_tags, self.object_tag_epcs, self.object_tag_labels, self.object_tag_dict)
        # self.classification_module = classification_module(self.unified_sequence_length)
        self.semantic_reasoning_module = semantic_reasoning_module(self.verbose, self.ontology_name, self.ontology_IRI)

        self.start()

    def start(self):
        # object_activations = self.object_activation_detection_module.start()
        # location_classifications = self.classification_module.start()

        location_classifications = [["kitchen_location_worktop_corner", "kitchen_location_worktop_sink", "kitchen_location_worktop_table", "kitchen_location_worktop_stove"],
                                    ["kitchen_location_worktop_sink", "kitchen_location_worktop_corner", "kitchen_location_worktop_table", "kitchen_location_worktop_stove"],
                                    ["bedroom_location_mirror", "bedroom_location_bed", "bedroom_location_drawers", "bedroom_location_wardrobe"],
                                    ["bedroom_location_bed", "bedroom_location_mirror", "bedroom_location_drawers", "bedroom_location_wardrobe"],
                                    ["kitchen_location_worktop_sink", "kitchen_location_worktop_corner", "kitchen_location_worktop_table", "kitchen_location_worktop_stove"]]
        object_activations = [["object_kettle", "object_mug", "object_coffee_container", "object_tea_container", "object_plate"],
                            ["object_kettle", "object_mug", "object_coffee_container", "object_book"],
                            ["object_toothbrush"],
                            ["object_toothbrush"],
                            ["object_cake", "object_plate"]]


        self.semantic_reasoning_module.start(location_classifications, object_activations)

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

if num_arguments == 2:
    database_name = sys.argv[1]
else:
    print("[MAIN][INFO] Invalid arguments. Usage: python3 control_module.py database_name")
    exit()

control_module = control_module(database_name)