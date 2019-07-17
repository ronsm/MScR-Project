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

This module must be run first. To run the Data Collector Module you must change directory into the `example` sub-directory of the root module folder. You will require Apache Ant and an up-to-date Java runtime environemt (JRE).

> ant all

> ant -Dreadername=<ip or hostame> run-datacollector

> ant -Dreadername=192.168.1.3 run-datacollector

### Data Segmentation Module (DSM)

Text

### Data Converter Module

Text

### Classification Module

Text