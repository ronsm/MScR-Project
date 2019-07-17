# Data Collector Module

## Usage

You will require Apache Ant, an up-to-date Java runtime environemt (JRE), and a local install of MongoDB server. You **must** start an instance of MongoDB server *before* running DCM.

To run the Data Collector Module you must change directory into the `example` sub-directory of the root module folder.

To start the module, use the following command, replacing 'IP_ADDRESS' with the IP of your Speedway Revolution reader.

> ant -Dreadername=<IP_ADDRESS> run-datacollector

For example, if your Speedway Revolution reader has an IP address of 192.168.1.3, you would use the following command:

> ant -Dreadername=192.168.1.3 run-datacollector

The module will load and after a few seconds will request that you provide a label for the recording session, which will be used to label the collection that will be inserted into the MongoDB database.

## Acknowledgement

Based on the LLRP Toolkit (LTK) from Impinj, available [here](https://support.impinj.com/hc/en-us/articles/202756168-Hello-LLRP-Low-Level-Reader-Protocol-), with additional code to generate periodic snapshots of tag data and post them to a MongoDB server.