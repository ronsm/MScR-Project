# Data Converter Module

This module converts data from the MongoDB timeseries into a machine learning ready format. If configured to access the 'RALT_RFID_HAR_System' database created by the Data Collector Module, this application generates a corresponding ML dataset as a collection of structured .txt files.

## Data Format

When you run this application, a folder named 'dataset' is generated within the application directory. The structure of which is outlined below.

    .
    ├── ...
    ├── dataset
    │   ├── test
    │   │   ├── input
    │   │   │   ├── {epc_0}_antenna.txt
    │   │   │   ├── {epc_0}_peakRSSI_.txt
    │   │   │   ├── {epc_0}_phaseAngle.txt
    │   │   │   ├── {epc_0}_velocity_.txt
    │   │   │   ├── ...
    │   │   │   ├── {epc_n}_antenna.txt
    │   │   │   ├── {epc_n}_peakRSSI_.txt
    │   │   │   ├── {epc_n}_phaseAngle.txt
    │   │   │   └──{epc_n}_velocity_.txt 
    │   │   └── labels.txt
    │   └── train
    │       ├── input
    │       │   ├── {epc_0}_antenna.txt
    │       │   ├── {epc_0}_peakRSSI_.txt
    │       │   ├── {epc_0}_phaseAngle.txt
    │       │   ├── {epc_0}_velocity_.txt
    │       │   ├── ...
    │       │   ├── {epc_n}_antenna.txt
    │       │   ├── {epc_n}_peakRSSI_.txt
    │       │   ├── {epc_n}_phaseAngle.txt
    │       │   └──{epc_n}_velocity_.txt 
    │       └── labels.txt
    └── ...

The application automatically splits the data into train and test sets, at a 70/30% split.