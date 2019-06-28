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

class classification_module:
    def __init__(self, unified_sequence_length):
        print("[classification_module][INFO] Starting up... ")
        self.model = load_model('models/model.h5')
        self.unified_sequence_length = unified_sequence_length
        print("[classification_module][INFO] Starting up... [OK]")

    def start(self):
        new_data = self.load_dataset()
        predictions = self.predict(new_data)
        
        print(predictions)

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
        model = load_model('models/model.h5')
        predictions = model.predict_classes(new_data)

        return predictions