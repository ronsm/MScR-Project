from numpy import mean
from numpy import std
from numpy import dstack
import numpy as np
import pandas as pd
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import ConvLSTM2D
from keras.utils import to_categorical
from keras.utils import plot_model
from keras.utils import normalize
from keras.layers import Embedding, Masking
from keras.regularizers import l2
from keras.optimizers import SGD
from matplotlib import pyplot
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.wrappers.scikit_learn import KerasClassifier
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.datasets import make_classification
import sys
import glob, os
import random

# fix seed
np.random.seed(27)

# verbose output
verbose_enable = 1

# shared model parameters
n_steps, n_length = 3, 10
verbose, epochs, batch_size = 0, 200, 5
early_stopping_patience = 15

def load_file(filepath):
    # print(filepath)
    dataframe = read_csv(filepath, header=None, delim_whitespace=True)
    # print(dataframe)
    return dataframe.values

def load_group(filenames, prefix=''):
	loaded = list()
	for name in filenames:
		data = load_file(prefix + name)
		loaded.append(data)
	loaded = dstack(loaded)
	return loaded

def load_dataset_group(group, prefix=''):
    filepath = prefix + group + '/input/'
    filenames = list()

    os.chdir(filepath)
    for file in sorted(glob.glob("*.txt")):
        filenames += [file]
    os.chdir('../../..')

    # print(filenames)

    X = load_group(filenames, filepath)
    y = load_file(prefix + group + '/y_'+group+'.txt')
    return X, y

def load_dataset(prefix=''):
    trainX, trainy = load_dataset_group('train', prefix + 'dataset/')
    print(trainX.shape, trainy.shape)

    testX, testy = load_dataset_group('test', prefix + 'dataset/')
    print(testX.shape, testy.shape)

    trainy = trainy.astype(int)
    testy = testy.astype(int)

    # y augmentation
    trainy = np.concatenate((trainy, trainy))
    testy = np.concatenate((testy, testy))

    # zero-offset class values (if they aren't already starting from zero!)
    # trainy = trainy - 1
    # testy = testy - 1

    # one hot encode y
    trainy = to_categorical(trainy)
    testy = to_categorical(testy)

    # normalize
    trainX = normalize(trainX)
    testX = normalize(testX)

    # x augmentation
    trainX = augment_input(trainX)
    testX = augment_input(testX)

    print(trainX.shape, trainy.shape, testX.shape, testy.shape)

    return trainX, trainy, testX, testy

def augment_input(data):
    data_copy = data
    
    for k in range(0, data_copy.shape[2]):
        for i in range(0, data_copy.shape[0]-1):
            num_changes = random.randint(1,5)
            changes = []

            for j in range(0, num_changes):
                index = random.randint(0, data_copy.shape[1]-1)
                changes.append(index)

            for change in changes:
                modification = random.random() / 6
                pos_neg = random.random()

                # print(modification)
                # print(data_copy[i][change])

                if pos_neg > 0.5:
                    data_copy[i][change][k] = data_copy[i][change][k] + modification
                else:
                    data_copy[i][change][k] = data_copy[i][change][k] - modification

                if data_copy[i][change][k] > 1.0:
                    data_copy[i][change][k] = 1.0
                elif data_copy[i][change][k] < 0.0:
                    data_copy[i][change][k] = 0.0

    concat_data = np.concatenate((data, data_copy))

    return concat_data

def evaluate_model_lstm(trainX, trainy, testX, testy):
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # define model
    model = Sequential()
    # model.add(Masking(mask_value=0, input_shape=(n_timesteps, n_features)))
    # add regularizer to below line: kernel_regularizer=l2(0.01), recurrent_regularizer=l2(0.01)
    model.add(LSTM(98, input_shape=(n_timesteps,n_features)))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=early_stopping_patience, verbose=verbose_enable))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_acc', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001))

    history = model.fit(trainX,
                      trainy,
                      epochs=epochs,
                      callbacks=callbacks,
                      verbose=verbose_enable,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    model = load_model('epoch_best_model.h5')

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)

    predy = model.predict(testX)

    y_test_class = np.argmax(testy, axis = 1)
    y_pred_class = np.argmax(predy, axis = 1)

    print(classification_report(y_test_class, y_pred_class))

    cm = confusion_matrix(y_pred_class, y_test_class)

    print(cm)

    return accuracy, model

def evaluate_model_cnn_lstm(trainX, trainy, testX, testy):
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    trainX = trainX.reshape((trainX.shape[0], n_steps, n_length, n_features))
    testX = testX.reshape((testX.shape[0], n_steps, n_length, n_features))

    # define model
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu'), input_shape=(None,n_length,n_features)))
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu')))
    model.add(TimeDistributed(Dropout(0.5)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(100))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=early_stopping_patience, verbose=verbose_enable))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_acc', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001))

    history = model.fit(trainX,
                      trainy,
                      epochs=epochs,
                      callbacks=callbacks,
                      verbose=verbose_enable,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    model = load_model('epoch_best_model.h5')

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)

    predy = model.predict(testX)

    y_test_class = np.argmax(testy, axis = 1)
    y_pred_class = np.argmax(predy, axis = 1)

    print(classification_report(y_test_class, y_pred_class))

    cm = confusion_matrix(y_pred_class, y_test_class)

    print(cm)

    return accuracy, model

# fit and evaluate a model
def evaluate_model_convlstm(trainX, trainy, testX, testy):
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    trainX = trainX.reshape((trainX.shape[0], n_steps, 1, n_length, n_features))
    testX = testX.reshape((testX.shape[0], n_steps, 1, n_length, n_features))

    # define model
    model = Sequential()
    model.add(ConvLSTM2D(filters=64, kernel_size=(1,3), activation='relu', input_shape=(n_steps, 1, n_length, n_features)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(32, activation='sigmoid'))
    # model.add(Dense(116, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=early_stopping_patience, verbose=verbose_enable))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_acc', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001))

    history = model.fit(trainX,
                      trainy,
                      epochs=epochs,
                      callbacks=callbacks,
                      verbose=verbose_enable,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    model = load_model('epoch_best_model.h5')

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)

    predy = model.predict(testX)

    y_test_class = np.argmax(testy, axis = 1)
    y_pred_class = np.argmax(predy, axis = 1)

    print(classification_report(y_test_class, y_pred_class))

    cm = confusion_matrix(y_pred_class, y_test_class)

    print(cm)

    return accuracy, model

# summarize scores
def summarize_results(scores):
	print(scores)
	m, s = mean(scores), std(scores)
	print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))

def main():
    # clear the terminal
    print(chr(27) + "[2J")
    print("* * * * * * * * * * * * * * * * * *")
    print("* Classification Module (Stage 1) *")
    print("* * * * * * * * * * * * * * * * * *")
    print("- Version 1.0")
    print("- Developed by Ronnie Smith")
    print("- github: @ronsm | email: ronnie.smith@ed.ac.uk | web: ronsm.com")
    print()

    num_arguments = len(sys.argv)

    global collection_name_prefix

    if num_arguments == 2:
        repeats = sys.argv[1]
        repeats = int(repeats)
    else:
        repeats = 10
        print("[MAIN][INFO] Invalid arguments. Usage: python3 classification_module.py num_experiments")
        exit()

	# load dataset
    print("[MAIN][STAT] Load dataset...")
    trainX, trainy, testX, testy = load_dataset()
    print("[DONE]")

	# repeat experiment
    scores = list()
    peak_score = 0
    for r in range(repeats):
        string = "[MAIN][STAT] Evaluating model, run " + str(r+1) + "/" + str(repeats) + "..."
        print(string)
        score, model = evaluate_model_convlstm(trainX, trainy, testX, testy)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)

        if score > peak_score:
            print('[MAIN][INFO] Saving overall best model...')
            peak_score = score
            model.summary()
            model.save('best_model.h5')
            plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)

    # summarize results
    print("[MAIN][STAT] Summarizing results... [DONE]")
    summarize_results(scores)
  
if __name__== "__main__":
  main()