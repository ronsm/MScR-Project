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
import csv

import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

bedroom_labels = ["bedroom_location_bed", "bedroom_location_drawers", "bedroom_location_wardrobe", "bedroom_location_mirror"]
kitchen_labels = ["kitchen_location_worktop_corner", "kitchen_location_worktop_sink", "kitchen_location_table"]

class classification_module_snapshot:
    def __init__(self, database_helper, num_tags):
        self.model = load_model('models/snapshot.h5')
        self.database_helper = database_helper
        self.num_tags = num_tags

        print("[classification_module_snapshot][INFO] Starting up... [OK]")

    def start(self):
        self.encoder = self.generate_predictions_csv()
        predictions_dict = self.split_predictions()
        
        return predictions_dict

    def generate_predictions_csv(self, prefix=''):
        dataset = pd.read_csv("unclassified/data.csv")
    
        X = dataset.iloc[:,0:196].values
        Y = dataset.iloc[:,196].values
        location_collections = dataset.iloc[:,197].values
    
        min_max_scaler = preprocessing.MinMaxScaler()
        X_scaled = min_max_scaler.fit_transform(X)
    
        X = pd.DataFrame(X_scaled)
    
        encoder = LabelEncoder()
        y1 = encoder.fit_transform(Y)
        Y = pd.get_dummies(y1).values

        y_pred = self.model.predict(X)

        y_pred = y_pred.tolist()
        y_pred[0].append('location_collection')
        for i in range(1, len(y_pred)):
            y_pred[i].append(location_collections[i])

        f = open("output/predictions.csv", "w")
        writer = csv.writer(f)
        writer.writerow(encoder.classes_)
        writer.writerows(y_pred)
        f.close()
    
        return encoder

    def split_predictions(self):
        predictions_dict = {}

        csv = pd.read_csv('output/predictions.csv', sep=',', header=1, skipinitialspace=True)
        
        num_collections, collections = self.database_helper.get_all_collection_names()
        for collection in collections:
            sub_csv = csv[csv['location_collection'] == collection]
            zipped = self.window_rank(sub_csv)
            predictions_dict[collection] = zipped

        return predictions_dict

    def window_rank(self, sub_csv):
        X = ["bedroom_location_bed", "bedroom_location_drawers", "bedroom_location_mirror", "bedroom_location_wardrobe", "kitchen_location_table",
            "kitchen_location_worktop_corner", "kitchen_location_worktop_sink"]

        sums = sub_csv.sum(axis = 0, skipna = True)

        window = []
        window.append(sums[0])
        window.append(sums[1])
        window.append(sums[2])
        window.append(sums[3])
        window.append(sums[4])
        window.append(sums[5])
        window.append(sums[6])

        zipped = [x for _,x in sorted(zip(window,X))]
        zipped.reverse()

        return zipped