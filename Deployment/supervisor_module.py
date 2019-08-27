import pymongo
from pymongo import MongoClient
import pprint
import sys
import csv

from database_helper import database_helper
from data_converter_module import data_converter_module
from object_activitation_detection_module import object_activation_detection_module
from classification_module_timeseries import classification_module_timeseries
from classification_module_snapshot import classification_module_snapshot
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
        self.object_tag_weights = self.load_object_tag_weights()

        self.location_database_helper = database_helper(location_database_name)
        self.activity_database_helper = database_helper(activity_database_name)

        self.ground_truth_objects, self.ground_truth_activities, self.ground_truth_locations = self.populate_ground_truths()

        # self.data_converter_module = data_converter_module(self.dcvm_mode, self.location_database_helper, self.static_tag_epcs, self.num_static_tags, self.unified_sequence_length, self.train_test_ratio)

        self.object_activation_detection_module = object_activation_detection_module(self.activity_database_helper, self.num_object_tags, self.object_tag_epcs, self.object_tag_labels, self.object_tag_dict, self.object_tag_weights)
        
        self.classification_module_timeseries = classification_module_timeseries(self.unified_sequence_length)
        self.classification_module_snapshot = classification_module_snapshot(self.location_database_helper, self.num_static_tags)        

        self.semantic_reasoning_module = semantic_reasoning_module(self.verbose, self.ontology_name, self.ontology_IRI)

        self.start()

    def start(self):
        # self.object_activation_detection_module.start()
        
        location_classifications = self.classification_module_snapshot.start()

        self.generate_location_activity_pairs(location_classifications)

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

    def load_object_tag_weights(self):
        object_tag_weights = {}

        with open("knowledge/object_weights.txt") as f:
            lines = f.read().splitlines()
        f.close()

        for line in lines:
            splits = line.split(":", 1)
            object_tag_weights[splits[0]] = splits[1]

        return object_tag_weights

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
                    if collection_name[6:7] != "-":
                        activity_collection_name = collection_name[:7] + '-A' + str(document["activity_index"])
                    else:
                        activity_collection_name = collection_name[:6] + '-A' + str(document["activity_index"])
                    activated_objects = self.object_activation_detection_module.get_activated_objects_for_sample(activity_collection_name)

                    location_collection_names_expanded.append(collection_name)
                    master_list.append(activated_objects)
                    activity_collection_names.append(activity_collection_name)

                previous_activity_index = current_activity_index

        ground_truth = []
        object_matches = 0
        for i in range(0, len(master_list)):
            matches = self.ground_truth_object_matches(activity_collection_names[i], master_list[i])
            ground_truth.append(matches)
            if len(matches) > 0:
                object_matches = object_matches + 1

        print('Total number of collections:', len(location_collection_names_expanded))
        print('Collections with object matches:', object_matches)

        # test only cases where objects are detected, with GT locations
        # for i in range(0, len(location_collection_names_expanded)):
        #     if len(ground_truth[i]) > 0:
        #         gtl = self.ground_truth_locations.get(location_collection_names_expanded[i])
        #         if gtl:
        #             print(location_collection_names_expanded[i], activity_collection_names[i], master_list[i], ground_truth[i])
        #             # print([self.ground_truth_locations[location_collection_names_expanded[i]]], master_list[i])
        #             self.semantic_reasoning_module.start([[self.ground_truth_locations[location_collection_names_expanded[i]]]], [master_list[i]])
        #             print('Ground truth activity:', self.ground_truth_activities[activity_collection_names[i]])
        #             print()

        # test all cases with real location estimations
        rows = []
        for i in range(0, len(location_collection_names_expanded)):
            gtl = self.ground_truth_locations.get(location_collection_names_expanded[i])
            if gtl:
                loc_exists = location_classifications.get(location_collection_names_expanded[i])
                if loc_exists:
                    print('Location:', location_collection_names_expanded[i], '(', self.ground_truth_locations[location_collection_names_expanded[i]], ')')
                    print('Activity:', activity_collection_names[i], '(', self.ground_truth_activities[activity_collection_names[i]], ')')
                    print('Location (CM):', location_classifications[location_collection_names_expanded[i]][0])
                    print('Objects (GT):', self.ground_truth_objects[self.ground_truth_activities[activity_collection_names[i]]])
                    print('Objects (OADM):', master_list[i])
                    # selected_round, selected_activity, selected_location = self.semantic_reasoning_module.start([location_classifications[location_collection_names_expanded[i]]], [self.ground_truth_objects[self.ground_truth_activities[activity_collection_names[i]]]])

                    selected_round, selected_activity, selected_location = self.semantic_reasoning_module.start([[self.ground_truth_locations[location_collection_names_expanded[i]]]], [master_list[i]])
                    print()
                    
                    row = [ self.ground_truth_locations[location_collection_names_expanded[i]], self.ground_truth_activities[activity_collection_names[i]],
                    location_classifications[location_collection_names_expanded[i]][0], selected_round, selected_location, selected_activity]

                    rows.append(row)

        f = open("output/output.csv", "w")
        writer = csv.writer(f)
        writer.writerows(rows)
        f.close()
                
    def ground_truth_object_matches(self, activity_collection_name, objects):
        activity = self.ground_truth_activities[activity_collection_name]

        matches = []
        for object in objects:
            if object in self.ground_truth_objects[activity]:
                matches.append(object)

        return matches

    def populate_ground_truths(self):
        ground_truth_objects = {}
        ground_truth_activities = {}
        ground_truth_locations = {}

        ground_truth_objects["activity_brushing_hair"] = ["object_hairbrush"]
        ground_truth_objects["activity_brushing_teeth"] = ["object_toothbrush", "object_toothpaste"]
        ground_truth_objects["activity_dressing"] = ["object_clothing"]
        ground_truth_objects["activity_eating_drinking"] = ["object_tableware", "object_drinkware", "object_mug", "object_plate", "object_glass"]
        ground_truth_objects["activity_prepare_cake"] = ["object_cake"]
        ground_truth_objects["activity_prepare_coffee"] = ["object_mug", "object_coffee_container", "object_sugar_container", "object_kettle"]
        ground_truth_objects["activity_prepare_tea"] = ["object_mug", "object_tea_container", "object_sugar_container", "object_kettle"]
        ground_truth_objects["activity_prepare_sandwich"] = ["object_bread", "object_plate", "object_butter", "object_sandwich_topping"]
        ground_truth_objects["activity_reading"] = ["object_book", "object_newspaper"]
        ground_truth_objects["activity_sleeping"] = ["none"]
        ground_truth_objects["activity_wash_dishes"] = ["object_tableware", "object_drinkware", "object_plate", "object_mug", "object_glass", "object_dish_soap"]

        num_collections, collections = self.activity_database_helper.get_all_collection_names()
        
        for c in collections:
            collection, pointer = self.activity_database_helper.get_collection(c)
            document = collection.find_one()
            if self.verbose == 1:
                print('Ground truth for activity', c, 'is', document["activity_label"])
            ground_truth_activities[c] = document["activity_label"]

        num_collections, collections = self.location_database_helper.get_all_collection_names()
    
        for c in collections:
            collection, pointer = self.location_database_helper.get_collection(c)
            document = collection.find_one()
            if self.verbose == 1:
                print('Ground truth for location', c, 'is', document["location_label"])
            ground_truth_locations[c] = document["location_label"]

        return ground_truth_objects, ground_truth_activities, ground_truth_locations


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
    database_prefix = sys.argv[1]
else:
    print("[MAIN][INFO] Invalid arguments. Usage: python3 supervisor_module.py database_prefix")
    exit()

location_database_name = database_prefix + '-L'
activity_database_name = database_prefix + '-A'

control_module = control_module(location_database_name, activity_database_name)