# Data Segmentation Module

The Data Segmentation Module (DSM) automatically segments a given collection in a given MongoDB database into collections representing the discrete activities within the original collection. For example, you have original collection 'Participant_1', which contains 23 activities. After running the DSM correctly, you will have collections 'Participant_1_1', 'Participant_1_2', ... 'Participant_1_23'.

## Usage

You **must** have an instance of MongoDB server installed and running *before* you can use this module.

Open `data_segmentation_module.py` and adjust the following parameters if needed:
* `db = client['DATABASE_NAME']` - change the 'DATABASE_NAME' to match the one used by the DCM
* `time_between_snapshots_millis` - set this equal to the time between snapshots set in the DCM (default is 1000)

For each collection you wish to segment you must generate two text (.txt) files: one containing the labels for each activity, and one containing the timestamps for when each label applies. You must achieve coverage for **every second** covered by the original collection. For example, for an original collection of 10 minutes long, your files may look as below.

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

**annotation_labels.txt**
```
sitting_living_room_sofa
transitioning
using_sink_kitchen
transitioning
preparing_food_drink_kitchen
transitioning
sitting_dining_table
```

With the root directory of this module as your working directory, use the following command to start the module:

> python3 data_segmentation_module.py collection_name annotation_labels annotation_times

So, for example, your command may look as follows:

> python3 data_segmentation_module.py RFID_Storage annotation_labels.txt annotation_times.txt