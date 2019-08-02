# Classification Module

The Classification Module (CM) is configured to automatically generate a simple Keras sequential neural network, for the mutli-label classification of activities/locations, from raw RFID data. Note that this module cares little about the exact labelling strategy used within the dataset. In the case of this project, the resulting model was used only to predict the location of an individual within a home environment within a few metres (through rooms and zones within them), but there is nothing stopping you (in theory) from conducting activity classification outright.

## Usage

Snapshot data is required for the classification module to work, which is exactly what the snapshot variant of the Data Converter Module (DCvM) provides. If you have not done so already, you **must** copy the `data.csv` file output by the snapshot DCvM into the `dataset` directory of this module - potentially overwriting an existing dataset, if one already exists.

From there, you should then simply be able to run the module with the following command, where `num_experiments` is the number of unique models that will be generated an evaluated (each over a number of epochs):

> python3 classification_module.py num_experiments

Only the best model will be saved by default, although each model is temporarily stored as `model.h5`, so if you wish to capture another model you will have to either stop the program at the correct time (before it is overwritten by the next model) or change the code to save mutliple models.

You may also wish to modify the parameters of the neural network yourself.