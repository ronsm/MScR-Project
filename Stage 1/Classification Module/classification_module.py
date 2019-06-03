from numpy import mean
from numpy import std
from numpy import dstack
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
import sys
import glob, os

def load_file(filepath):
    print(filepath)
    dataframe = read_csv(filepath, header=None, delim_whitespace=True)
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
    for file in glob.glob("*.txt"):
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

	# zero-offset class values
	trainy = trainy - 1
	testy = testy - 1

	# one hot encode y
	trainy = to_categorical(trainy)
	testy = to_categorical(testy)
	print(trainX.shape, trainy.shape, testX.shape, testy.shape)

	return trainX, trainy, testX, testy

# fit and evaluate a model
def evaluate_model(trainX, trainy, testX, testy):
	# define model
	verbose, epochs, batch_size = 0, 25, 64
	n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

	# reshape into subsequences (samples, time steps, rows, cols, channels)
	n_steps, n_length = 4, 32
	trainX = trainX.reshape((trainX.shape[0], n_steps, 1, n_length, n_features))
	testX = testX.reshape((testX.shape[0], n_steps, 1, n_length, n_features))

	# define model
	model = Sequential()
	model.add(ConvLSTM2D(filters=64, kernel_size=(1,3), activation='relu', input_shape=(n_steps, 1, n_length, n_features)))
	model.add(Dropout(0.5))
	model.add(Flatten())
	model.add(Dense(100, activation='relu'))
	model.add(Dense(n_outputs, activation='softmax'))
	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

	# fit network
	model.fit(trainX, trainy, epochs=epochs, batch_size=batch_size, verbose=verbose)
	# evaluate model
	_, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)
	return accuracy

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
    for r in range(repeats):
        string = "[MAIN][STAT] Evaluating model, run " + str(r+1) + "/" + str(repeats) + "..."
        print(string)
        score = evaluate_model(trainX, trainy, testX, testy)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)

    # summarize results
    print("[MAIN][STAT] Summarizing results... [DONE]")
    summarize_results(scores)
  
if __name__== "__main__":
  main()