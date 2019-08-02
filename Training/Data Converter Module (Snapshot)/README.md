# Data Converter Module

This module converts data from the MongoDB timeseries into a machine learning ready format. If configured to access a MongoDB database created by the Data Collector Module, this application generates a corresponding CSV file that can be used to train on individual snapshots of data (not timeseries).

## Usage

You **must** have an instance of MongoDB server installed and running *before* you can use this module.

Open `data_converter_module.py` and adjust the following parameters if needed:
* `db = client['DATABASE_NAME']` - change the 'DATABASE_NAME' to match the one used by the DCM
* `num_tags` - set this equal to the total number of tags in the database, counting static *and* object

You **must** modify `static.txt` to include the EPCs of all static tags (NOT object tags) for which TXT files are to be generated. The number of lines in this file **must** match the value of `num_tags`.

With the root directory of this module as your working directory, use the following command to start the module:

> python3 data_converter_module.py

## Data Format

When you run this application, a single file titled 'data.csv' is created within the 'dataset' directory.

Data within the CSV file is structured so that each line contains the RSSI values from all tags, and the corresponding label for one snapshot of data.