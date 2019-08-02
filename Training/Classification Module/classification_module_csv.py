from subprocess import check_output
import numpy as np
from numpy import mean
from numpy import std
import pandas as pd
import seaborn as sns
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import sys
import glob, os

seed = 27
num_tags = 196
train_test_ratio = 0.3

def load_dataset(prefix=''):
    dataset = pd.read_csv("dataset/data.csv")

    X = dataset.iloc[:,0:num_tags].values
    Y = dataset.iloc[:,num_tags].values

    encoder = LabelEncoder()
    y1 = encoder.fit_transform(Y)
    Y = pd.get_dummies(y1).values

    return X, Y, encoder

def create_model():
    input_dim = num_tags

    # create model
    model = Sequential()
    model.add(Dense(98, input_dim = input_dim , activation = 'relu'))
    model.add(Dense(49, activation = 'relu'))
    model.add(Dense(49, activation = 'relu'))
    model.add(Dense(49, activation = 'relu'))
    model.add(Dense(5, activation = 'softmax'))

    # Compile model
    model.compile(loss = 'categorical_crossentropy' , optimizer = 'adam' , metrics = ['accuracy'] )

    return model

def evaluate_model(model, X_train, y_train, X_test, y_test):
    callbacks = []
    callbacks.append(EarlyStopping(monitor='val_loss', patience=20, verbose=1))
    callbacks.append(ModelCheckpoint(filepath='epoch_best_model.h5', monitor='val_loss', save_best_only=True))
    callbacks.append(ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.001))

    history = model.fit(X_train,
                      y_train,
                      epochs=100,
                      callbacks=callbacks,
                      verbose=1,
                      batch_size=30,
                      validation_data=(X_test, y_test))

    y_pred = model.predict(X_test)

    y_test_class = np.argmax(y_test, axis = 1)
    y_pred_class = np.argmax(y_pred, axis = 1)

    print(classification_report(y_test_class, y_pred_class))

    cm = confusion_matrix(y_test_class, y_pred_class)
    print(cm)

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

        evaluate_model(model, X_train, y_train, X_test, y_test)

        print(encoder.classes_)

    # summarize results
    print("[MAIN][STAT] Summarizing results... [DONE]")
    summarize_results(scores)
  
if __name__== "__main__":
  main()