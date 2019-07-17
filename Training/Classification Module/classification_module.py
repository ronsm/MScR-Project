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
from matplotlib import pyplot
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.wrappers.scikit_learn import KerasClassifier
from keras.callbacks import EarlyStopping, ModelCheckpoint
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

    # zero-offset class values (if they don't already!)
    # trainy = trainy - 1
    # testy = testy - 1

    # one hot encode y
    trainy = to_categorical(trainy)
    testy = to_categorical(testy)
    print(trainX.shape, trainy.shape, testX.shape, testy.shape)

    return trainX, trainy, testX, testy

# fit and evaluate a model
def evaluate_model(trainX, trainy, testX, testy):
    # define model
    verbose, epochs, batch_size = 0, 10, 4
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    # reshape into subsequences (samples, time steps, rows, cols, channels)
    n_steps, n_length = 2, 12
    trainX = trainX.reshape((trainX.shape[0], n_steps, 1, n_length, n_features))
    testX = testX.reshape((testX.shape[0], n_steps, 1, n_length, n_features))

    # define model
    model = Sequential()
    model.add(ConvLSTM2D(filters=122, kernel_size=(1,3), activation='relu', input_shape=(n_steps, 1, n_length, n_features)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    callbacks = [EarlyStopping(monitor='val_loss', patience=2, verbose=1), ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_loss', save_best_only=True)]

    history = model.fit(trainX,
                      trainy,
                      epochs=20,
                      callbacks=callbacks,
                      verbose=0,
                      batch_size=batch_size,
                      validation_data=(testX, testy))

    # plot model
    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)

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
        score, model = evaluate_model(trainX, trainy, testX, testy)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)

        if score > peak_score:
            print('[MAIN][INFO] Saving overall best model...')
            peak_score = score
            model.save('best_model.h5')

    # summarize results
    print("[MAIN][STAT] Summarizing results... [DONE]")
    summarize_results(scores)
  
if __name__== "__main__":
  main()