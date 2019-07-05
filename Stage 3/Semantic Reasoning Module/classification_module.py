from numpy import mean
from numpy import std
from numpy import dstack
import numpy as np
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import ConvLSTM2D
from keras.utils import to_categorical
from matplotlib import pyplot
from keras.models import load_model
import sys
import glob, os
import operator
import pprint

class classification_module:
    def __init__(self, unified_sequence_length):
        print("[classification_module][INFO] Starting up... ")
        self.model = load_model('models/best_model.h5')
        self.unified_sequence_length = unified_sequence_length
        print("[classification_module][INFO] Starting up... [OK]")

    def start(self):
        new_data = self.load_dataset()
        master_list = self.predict(new_data)
        master_list = self.one_hot_decoding(master_list)

        return master_list

    def load_file(self, filepath):
        dataframe = read_csv(filepath, header=None, delim_whitespace=True)
        return dataframe.values

    def load_group(self, filenames, prefix=''):
        loaded = list()
        for name in filenames:
            data = self.load_file(prefix + name)
            loaded.append(data)
        loaded = dstack(loaded)
        return loaded

    def load_dataset_group(self):
        filepath = 'unclassified/'
        filenames = list()

        os.chdir(filepath)
        for file in glob.glob("*.txt"):
            filenames += [file]
        os.chdir('..')

        X = self.load_group(filenames, filepath)
        return X

    def load_dataset(self, prefix=''):
        new_data = self.load_dataset_group()

        new_data = new_data.astype(int)

        n_features = new_data.shape[2]
        n_steps = 2
        n_length = int(self.unified_sequence_length / 2)
        new_data = new_data.reshape((new_data.shape[0], n_steps, 1, n_length, n_features))

        return new_data

    def predict(self, new_data):
        predictions = self.model.predict(new_data)

        master_list = []
        for i in range(0, len(predictions)):
            prediction_dict = {}
            for j in range(0, len(predictions[i])):
                prediction_dict[j] = predictions[i][j]
            sorted_prediction_dict = sorted(prediction_dict.items(), key=operator.itemgetter(1), reverse=True)
            master_list.append(sorted_prediction_dict)

        return master_list

    def one_hot_decoding(self, master_list):
        one_hot_encodings = self.load_label_map()

        for i in range(0, len(master_list)):
            for j in range(0, len(master_list[i])):
                master_list[i][j] = list(master_list[i][j])

        for i in range(0, len(master_list)):
            for j in range(0, len(master_list[i])):
                master_list[i][j][0] = one_hot_encodings[master_list[i][j][0]]

        return master_list

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