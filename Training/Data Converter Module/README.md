# Data Converter Module

This module converts data from the MongoDB timeseries into a machine learning ready format. If configured to access a MongoDB database created by the Data Collector Module, this application generates a corresponding ML dataset as a collection of structured .txt files.

## Usage

You **must** have an instance of MongoDB server installed and running *before* you can use this module.

Open `data_converter_module.py` and adjust the following parameters if needed:
* `db = client['DATABASE_NAME']` - change the 'DATABASE_NAME' to match the one used by the DCM
* `num_tags` - set this equal to the total number of tags in the database, counting static *and* object
* `unified_sequence_length` - adjust this to set the length all sequences will be padded to i.e. number of snapshots per window
* `train_test_ratio` - adjust this to modify the % split of train/test (default is 0.7, i.e. 70/30% train/test)

You **must** modify `static.txt` to include the EPCs of all static tags (NOT object tags) for which TXT files are to be generated. The number of lines in this file **must** match the value of `num_tags`.

With the root directory of this module as your working directory, use the following command to start the module:

> python3 data_converter_module.py

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

The application automatically splits the data into train/test sets, at a 70/30% split. In this case, each measureable property (antenna, peakRSSI, phaseAngle, and velocity) are treated as distinct sensor inputs. Each file in the 'input' folder for each set represents an input feature, while the labels.txt file in each contains the class labels.

Data within each input text file is structured so that each line represents one sample window (i.e. one label), with each line containing white-space seperated values that represent state values for each snapshot recorded during the sample window.