
RUNNING The LTKJava examples.

THe examples will build and run from this directory.  They access files from this relative 
path, so they may not run properly from other directories.

to compile the examples use

> ant all

To run a specific example, you must have a reader connected to the PC 
on which the examples are run.  The hostname or IP address of the reader
must be known.

> ant -Dreadername=<ip or hostame> run-docsampleX

where X is the sample you want to run.  For example, assuming your
reader is 192.168.1.5, you could type

ant -Dreadername=192.168.1.5 run-docsample1

