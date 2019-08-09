from numpy import mean
from numpy import std
from numpy import dstack
import pandas as pd
import numpy as np
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from collections import Counter
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import ConvLSTM2D
from keras.utils import to_categorical
from matplotlib import pyplot
from keras.models import load_model
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
import sys
import glob, os
import operator
import pprint

import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

class classification_module_snapshot:
    def __init__(self, database_helper, num_tags):
        print("[classification_module_snapshot][INFO] Starting up... ")
        self.model = load_model('models/snapshot.h5')
        self.database_helper = database_helper
        self.num_tags = num_tags
        print("[classification_module_snapshot][INFO] Starting up... [OK]")

    def start(self):
        num_collections, collections = self.database_helper.get_all_collection_names()

        master_list = {}
        for collection in collections:
            snapshots = self.get_sample_batches(collection)
            predictions = self.predict(snapshots)
            predictions = self.decode_predictions(predictions)
            predictions = self.predictions_reduce(predictions)
            
            master_list[collection] = predictions

        print(master_list)
        return master_list

    def get_sample_batches(self, collection):
        snapshots = []
        collection, pointer = self.database_helper.get_collection(collection)

        for document in pointer:
            snapshot = []

            for i in range(0, self.num_tags):
                epc = document["tags"][i]["_id"]
                peakRSSI = document["tags"][i]["peakRSSI"]
                if epc[:20] != "300833B2DDD901401111":
                    snapshot.append(peakRSSI)

            snapshot.append(document["location_label"])
            snapshot.append(document["activity_index"])

            snapshots.append(snapshot)

        return snapshots

    def predict(self, samples):        
        prediction_samples = []
        for sample in samples:
            sample_slice = sample[:196]
            prediction_samples.append(sample_slice)

        prediction_samples = np.array(prediction_samples)

        min_max_scaler = preprocessing.MinMaxScaler()
        prediction_samples_scaled = min_max_scaler.fit_transform(prediction_samples)
    
        prediction_samples_scaled = pd.DataFrame(prediction_samples_scaled)

        predictions = self.model.predict(prediction_samples_scaled)

        return predictions

    def decode_predictions(self, predictions):
        master_list = []
        for i in range(0, len(predictions)):
            prediction_dict = {}
            for j in range(0, len(predictions[i])):
                prediction_dict[j] = predictions[i][j]
            sorted_prediction_dict = sorted(prediction_dict.items(), key=operator.itemgetter(1), reverse=True)
            master_list.append(sorted_prediction_dict)

        one_hot_encodings = self.load_label_map()

        for i in range(0, len(master_list)):
            for j in range(0, len(master_list[i])):
                master_list[i][j] = list(master_list[i][j])

        for i in range(0, len(master_list)):
            for j in range(0, len(master_list[i])):
                master_list[i][j][0] = one_hot_encodings[master_list[i][j][0]]

        return master_list

    def predictions_reduce(self, predictions):
        rank_1 = []
        for prediction in predictions:
            rank_1.append(prediction[0][0])

        c = Counter(rank_1)

        ranked = c.most_common(7)

        return ranked

    def load_label_map(self):
        one_hot_encodings = {}
        with open("knowledge/label_map.txt") as f:
            lines = f.read().splitlines()
        f.close()

        for line in lines:
            splits = line.split(":", 1)
            splits[0] = int(splits[0])
            one_hot_encodings[splits[0]] = splits[1]

        return one_hot_encodings

    # def debug_print(self, master_list):
    #     i = 1
    #     for location_classification in master_list:
    #         print('ROW', i)
    #         print(location_classification)
    #         i = i + 1