# MScR Project

Title: **Activity Recognition with Radio-Frequency Identification in Cognitive Assistive Robotic Environments**

Author: Ronnie Smith ([@ronsm](https://github.com/ronsm))

Submitted: 16th August 2019

## Repository Information

This repository stores all of the code developed during the project. The software within the `Training` directory is a collection of standalone module that can be run (in a specific order, see below) to generate an LSTM or ConvLSTM model from raw RFID data gathered from an IMPINJ Speedway Revolution system. Within the `Deployment` directory you will find a single application, comprised of a number of modules (including re-worked versions of those from the training stage), that combines the previously generated LSTM or ConvLSTM model and some ontological knowledge to make coarse-to-fine grained predictions of activities.

To understand fully the purpose and design of this software, you may first wish to read the accompanying thesis, available on my website: [https://ronsm.com/courses/mscr-project/thesis.pdf](https://ronsm.com/courses/mscr-project/thesis.pdf)

## Training

The following modules are provided within the `Training` directory:
* Data Collector Module
* Data Segmentation Module
* Data Converter Module
* Classification Module

There are individual readmes for each module. Here we will simply discuss some parameters and the order of execution of the modules to ultimately generate an LSTM or ConvLSTM model.

### Data Collector Module (DCM)

This module must be run first. To run the Data Collector Module you must change directory into the `example` sub-directory of the root module folder. You will require Apache Ant, an up-to-date Java runtime environemt (JRE), and a local install of MongoDB server. You **must** start an instance of MongoDB server *before* running DCM.

To start the module, use the following command, replacing 'IP_ADDRESS' with the IP of your Speedway Revolution reader.

> ant -Dreadername=<IP_ADDRESS> run-datacollector

For example, if your Speedway Revolution reader has an IP address of 192.168.1.3, you would use the following command:

> ant -Dreadername=192.168.1.3 run-datacollector

The module will load and after a few seconds will request that you provide a label for the recording session, which will be used to label the collection that will be inserted into the MongoDB database.

### Data Segmentation Module (DSM)

Using the label that you have previously provided to the DCM, the Data Segmentation Module can help you automatically split the original collection, which contains many activities, into a single collection for each activity.

You must run this module before attempting to run either the Data Converter Module or the Classification Module.

See the README inside this module's directory for information on how to setup and use it.

### Data Converter Module (DCvM)

The standalone Data Converter Module needs to be run before the Classification Module, since it requires a dataset to be provided to it from DCvM.

It will generate a dataset inside its own directory (titled `dataset`) which you should copy in its entirety to wtihin the root directory of the Classification Module - overwriting a previous 'dataset' folder if need be.

See the README inside this module's directory for information on how to setup and use it.

### Classification Module

Once the files have been provided from the DCvM, the Classification Module will generate and evaluate numerous LSTM or ConvLSTM models (ConvLSTM is the default).

The best performing model will be saved within the root directory of the module as `best_model.h5`. This file is required by the sofware in the `Deployment` directory to make predictions. Place the `best_model.h5` file into the `Deployment/models` directory - again, overwriting a previous model if need be.

See the README inside this module's directory for information on how to setup and use it.