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
from keras.utils import plot_model
from keras.layers import Embedding, Masking
from keras.regularizers import l2
from matplotlib import pyplot
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.wrappers.scikit_learn import KerasClassifier
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_classification
import sys
import glob, os

np.random.seed(0)

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

    # zero-offset class values (if they aren't already starting from zero!)
    # trainy = trainy - 1
    # testy = testy - 1

    # one hot encode y
    trainy = to_categorical(trainy)
    testy = to_categorical(testy)
    print(trainX.shape, trainy.shape, testX.shape, testy.shape)

    return trainX, trainy, testX, testy

def evaluate_model_lstm(trainX, trainy, testX, testy):
    # define model
    verbose, epochs, batch_size = 0, 25, 16
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # reshape into subsequences (samples, time steps, rows, cols, channels)
    n_steps, n_length = 2, 15

    # define model
    model = Sequential()
    # model.add(Masking(mask_value=999, input_shape=(n_timesteps, n_features)))
    # add regularizer to below line: kernel_regularizer=l2(0.01), recurrent_regularizer=l2(0.01)
    model.add(LSTM(100, input_shape=(n_timesteps,n_features)))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=2, verbose=1))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_loss', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.001))

    history = model.fit(trainX,
                      trainy,
                      epochs=epochs,
                      callbacks=callbacks,
                      verbose=0,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    model = load_model('epoch_best_model.h5')

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)

    return accuracy, model

def evaluate_model_cnn_lstm(trainX, trainy, testX, testy):
    # define model
    verbose, epochs, batch_size = 0, 25, 64
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # reshape data into time steps of sub-sequences
    n_steps, n_length = 4, 15
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

    callbacks = [EarlyStopping(monitor='val_loss', patience=2, verbose=1), ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_loss', save_best_only=True)]

    history = model.fit(trainX,
                      trainy,
                      epochs=epochs,
                      callbacks=callbacks,
                      verbose=0,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    model = load_model('epoch_best_model.h5')

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)

    return accuracy, model

# fit and evaluate a model
def evaluate_model_convlstm(trainX, trainy, testX, testy):
    # define model
    verbose, epochs, batch_size = 0, 100, 32
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # reshape into subsequences (samples, time steps, rows, cols, channels)
    n_steps, n_length = 2, 15
    trainX = trainX.reshape((trainX.shape[0], n_steps, 1, n_length, n_features))
    testX = testX.reshape((testX.shape[0], n_steps, 1, n_length, n_features))

    # define model
    model = Sequential()
    model.add(ConvLSTM2D(filters=98, kernel_size=(1,3), activation='relu', input_shape=(n_steps, 1, n_length, n_features)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(116, activation='sigmoid'))
    # model.add(Dense(116, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=2, verbose=1))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_loss', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.001))

    history = model.fit(trainX,
                      trainy,
                      epochs=epochs,
                      callbacks=callbacks,
                      verbose=0,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    model = load_model('epoch_best_model.h5')

    # evaluate model
    _, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)

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