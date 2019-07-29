# Data Segmentation Module

The Data Segmentation Module (DSM) automatically segments given location and activity collections, stored in their repsective location and activity MongoDB databases, into collections representing the discrete activities within the original collection.

For example, you have two copies of the original collection 'Participant_1', one in database 'TEST1-L' and one in database 'TEST1-A', which represents 23 discrete locations and 17 discerete activities. After running the DSM correctly, you will have collections 'Participant_1_1', 'Participant_1_2', ... 'Participant_1_23' within 'TEST1-L' and collections 'Participant_1_1', 'Participant_1_2', ... 'Participant_1_17' within 'TEST1-A'.

Documents in each collection in the location database also encode the index of the corresponding activity collection in the activity database. This helps to handle situations where the location may change, but the activity does not, and vice versa.

## Usage

You **must** have an instance of MongoDB server installed and running *before* you can use this module.

Open `data_segmentation_module.py` and adjust the following parameter if needed:
* `time_between_snapshots_millis` - set this equal to the time between snapshots set in the DCM (default is 1000)

For each collection you wish to segment you must generate four text (.txt) files: one containing the labels for each location, one containing the labels for each activity, one containing the timestamps for when each label applies, and one containing the activity indexes to relate the resulting location collections to the activity collections. You must achieve coverage for **every second** covered by the original collection. For example, for an original collection of 10 minutes long, your files may look as below.

**annotation_times.txt**
```
00:00-01:00
01:01-01:20
01:21-01:50
01:51-02:05
02:06-04:30
04:31-04:45
04:46-10:00
```

**annotation_location_labels.txt**
```
kitchen_location_worktop_corner
kitchen_location_worktop_sink
kitchen_location_worktop_corner
kitchen_location_worktop_stove
kitchen_location_worktop_corner
kitchen_location_worktop_sink
kitchen_location_worktop_corner
```

**annotation_activity_labels.txt**
```
activity_prepare_sandwich
activity_prepare_sandwich
activity_prepare_coffee
activity_prepare_coffee
activity_prepare_coffee
activity_prepare_coffee
activity_prepare_coffee
```

**annotation_activity_indexes.txt**
```
25
25
26
26
26
26
26
```

With the root directory of this module as your working directory, use the following command to start the module:

> python3 data_segmentation_module.py database_prefix collection_name

The 'database_prefix' refers to the shared root name of your location and activity databases (i.e. you have databases 'PID001-L' and 'PID002-A', where the prefix is 'PID002'. So, for example, your command may look as follows:

> python3 data_segmentation_module.py TEST_DB PID001