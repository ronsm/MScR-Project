# MScR Project

Title: **Activity Recognition with Radio-Frequency Identification in Cognitive Assistive Robotic Environments**

Author: Ronnie Smith ([@ronsm](https://github.com/ronsm))

Submitted: 16th August 2019

## Repository Information

This repository stores all of the code developed during the project. The software within the `Training` directory is a collection of standalone module that can be run (in a specific order, see below) to generate an LSTM or ConvLSTM model from raw RFID data gathered from an IMPINJ Speedway Revolution system. Within the `Deployment` directory you will find a single application, comprised of a number of modules (including re-worked versions of those from the training stage), that combines the previously generated LSTM or ConvLSTM model and some ontological knowledge to make coarse-to-fine grained predictions of activities.