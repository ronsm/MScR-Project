# Data Collector Module

Based on the LLRP Toolkit (LTK) from Impinj, available [here](https://support.impinj.com/hc/en-us/articles/202756168-Hello-LLRP-Low-Level-Reader-Protocol-), with additional code to generate periodic snapshots of tag data and post them to a MongoDB server.

## Change to Schema Format

A change was made to the snapshot schema on 15/05/2019, to make it easier for data to be manipulated without datatype conversion in other Python modules used in this project. The code below shows how to store tags within the snapshot inside a 'tags' array, rather than as individual documents within the snapshot.

```
testObject.put("suitename", testsuite);
testObject.put("testname", testcase);         
List<BasicDBObject> milestones = new ArrayList<>();
milestones.add(new BasicDBObject("milestone_id", "2333"));
testObject.put("milestones", milestones);
locations.insert(testObject);
```