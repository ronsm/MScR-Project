import pymongo
from pymongo import MongoClient
import pprint
import sys

from database_helper import database_helper
from data_converter_module import data_converter_module
from object_activitation_detection_module import object_activation_detection_module
from classification_module import classification_module

class semantic_reasoning_module:
    def __init__(self, database_name):
        self.unified_sequence_length = 24
        self.num_tags = 244
        self.unified_sequence_length = 24
        self.train_test_ratio = 0.7
        self.num_object_tags = 50

        self.tag_epcs = self.read_tag_epcs()

        self.database_helper = database_helper(database_name)
        self.data_converter_module = data_converter_module(1, self.database_helper, self.tag_epcs, self.num_tags, self.unified_sequence_length, self.train_test_ratio)
        self.object_activation_detection_module = object_activation_detection_module(self.database_helper, self.num_object_tags)
        self.classification_module = classification_module(self.unified_sequence_length)

        self.start()

    def start(self):
        # self.data_converter_module.start()
        # self.object_activation_detection_module.start()
        self.classification_module.start()

    def read_tag_epcs(self):
        with open("tags.txt") as f:
            tag_epcs = f.read().splitlines() 
        f.close()

        return tag_epcs

# clear the terminal
print(chr(27) + "[2J")
print("* * * * * * * * * * * * * * *")
print("* Semantic Reasoning Module *")
print("* * * * * * * * * * * * * * *")
print("- Version 1.0")
print("- Developed by Ronnie Smith")
print("- github: @ronsm | email: ronnie.smith@ed.ac.uk | web: ronsm.com")
print()

num_arguments = len(sys.argv)

global database_name

if num_arguments == 2:
    database_name = sys.argv[1]
else:
    print("[MAIN][INFO] Invalid arguments. Usage: python3 semantic_reasoning_module.py database_name")
    exit()

semantic_reasoning_module = semantic_reasoning_module(database_name)