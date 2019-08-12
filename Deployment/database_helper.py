import pymongo
from pymongo import MongoClient
import pprint
import sys
from random import shuffle

# mongodb connection setup
client = MongoClient("localhost", 27017, maxPoolSize=50)

class database_helper:
    def __init__(self, database_name):
        print("[database_helper][INFO] Starting up... ", end="", flush=True)
        self.database_name = database_name
        print("[OK]")

    def get_collection(self, collection_name):
        db = client[self.database_name]
        collection = db[collection_name]
        pointer = collection.find({})
        return collection, pointer

    def get_all_collection_names(self):
        db = client[self.database_name]
        collections = db.collection_names()

        num_collections = len(collections)

        return num_collections, collections

    def get_split_collection_names(self, train_test_ratio):
        num_collections, collections =  self.get_all_collection_names()

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

    def split_static_and_object_tags(self, collection_name):
        collection, pointer = self.get_collection(collection_name)

        for document in pointer:
            query = {"_id": document["_id"]}

            object_tags = []
            for i in range(0, len(document['tags'])):
                if '9999' in document['tags'][i]['_id']:
                    object_tags.append(document['tags'][i])
                    
                    document_id = document['tags'][i]['_id']
                    remove = {"$pull": {"tags": {"_id": document_id}}}
                    # remove = { "$unset": { "object_tags_change_points": "", "object_tags_cpd": "", "activityLabel": ""} }
                    # comment out line below to delete copy of object tags in original tag pool
                    collection.update_one(query, remove)
            
            new_array = {"$set": {"object_tags": object_tags}}

            collection.update_one(query, new_array)