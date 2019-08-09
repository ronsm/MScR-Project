from subprocess import check_output
import numpy as np
from numpy import mean
from numpy import std
import pandas as pd
import seaborn as sns
from keras.models import Sequential
from keras.layers import Dropout
from keras.layers import Dense
from keras.optimizers import Adam
from keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn import preprocessing
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import sys
import glob, os
import pprint
import random

seed = 27
num_tags = 196
train_test_ratio = 0.3

def load_dataset(prefix=''):
    dataset = pd.read_csv("dataset/data.csv")

    X = dataset.iloc[:,0:num_tags].values
    Y1 = dataset.iloc[:,num_tags].values
    Y2 = dataset.iloc[:,num_tags].values

    Y = np.concatenate((Y1, Y2))

    min_max_scaler = preprocessing.MinMaxScaler()
    X_scaled = min_max_scaler.fit_transform(X)

    X = pd.DataFrame(X_scaled)

    encoder = LabelEncoder()
    y1 = encoder.fit_transform(Y)
    Y = pd.get_dummies(y1).values

    X = augment_input(X)

    return X, Y, encoder

def augment_input(data):
    data_copy = data.copy()
    
    for i in range(0, len(data_copy)):
        num_changes = random.randint(1,20)
        changes = []

        for j in range(0, num_changes):
            index = random.randint(0, num_tags-1)
            changes.append(index)

        for change in changes:
            modification = random.random() / 5
            pos_neg = random.random()

            # print(modification)
            # print(data_copy[i][change])

            if pos_neg > 0.5:
                data_copy[change][i] = data_copy[change][i] + modification
            else:
                data_copy[change][i] = data_copy[change][i] + modification

            if data_copy[change][i] > 1.0:
                data_copy[change][i] = 1.0
            elif data_copy[change][i] < 0.0:
                data_copy[change][i] = 0.0

    # data_copy = data_copy + data
    frames = [data, data_copy]
    concat_data = pd.concat(frames)

    return concat_data

def create_model():
    input_dim = num_tags

    # define model
    model = Sequential()
    model.add(Dense(98, input_dim = input_dim , activation = 'relu'))
    model.add(Dense(49, activation = 'relu'))
    model.add(Dropout(0.2))
    model.add(Dense(49, activation = 'relu'))
    model.add(Dense(49, activation = 'relu'))
    model.add(Dense(7, activation = 'softmax'))

    model.compile(loss = 'categorical_crossentropy' , optimizer = 'adam' , metrics = ['accuracy'] )

    return model

def evaluate_model(model, X_train, y_train, X_test, y_test):
    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=15, verbose=1))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_acc', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.001))

    history = model.fit(X_train,
                      y_train,
                      epochs=500,
                      callbacks=callbacks,
                      verbose=1,
                      batch_size=50,
                      validation_data=(X_test, y_test))

    y_pred = model.predict(X_test)
    _, accuracy = model.evaluate(X_test, y_test, batch_size=50, verbose=0)

    y_test_class = np.argmax(y_test, axis = 1)
    y_pred_class = np.argmax(y_pred, axis = 1)

    print(classification_report(y_test_class, y_pred_class))

    cm = confusion_matrix(y_test_class, y_pred_class)
    print(cm)

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
    print("[MAIN][STAT] Load dataset...", end="", flush=True)
    X, Y, encoder = load_dataset()
    print("[DONE]")

    print("[MAIN][STAT] Splitting dataset to train/test...", end="", flush=True)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = train_test_ratio, random_state = 0)
    print("[DONE]")

	# repeat experiment
    scores = list()
    peak_score = 0
    for r in range(repeats):
        string = "[MAIN][STAT] Evaluating model, run " + str(r+1) + "/" + str(repeats) + "..."
        print(string)

        model = create_model()

        score = evaluate_model(model, X_train, y_train, X_test, y_test)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)

        if score > peak_score:
            print('[MAIN][INFO] Saving overall best model...')
            peak_score = score
            model.summary()
            model.save('best_model.h5')

        print(encoder.classes_)

    # summarize results
    print("[MAIN][STAT] Summarizing results... [DONE]")
    summarize_results(scores)

    print("[MAIN][INFO] Confusion matrix for best model...")
    # confusion matrix for best model
    model = load_model('best_model.h5')
    
    y_pred = model.predict(X_test)
    _, accuracy = model.evaluate(X_test, y_test, batch_size=50, verbose=0)

    y_test_class = np.argmax(y_test, axis = 1)
    y_pred_class = np.argmax(y_pred, axis = 1)

    print(classification_report(y_test_class, y_pred_class))

    cm = confusion_matrix(y_test_class, y_pred_class)
    print(cm)
  
if __name__== "__main__":
  main()