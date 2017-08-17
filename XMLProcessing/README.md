
# extract the IRE needle information 
# calculate the angle in-between the needles
# extract the Target Positioning Errors

General tasks:
- iterate through all folders and subfolders
- generally the log files are in the folder "XML Recording"
- if file extension is *.xml and if it contains the name validation then it contains the validated needle information
- create zip dump if necessary (probably it is) !!!!
- iterate through all files that contain IRE measurement
 
The date from the XML log files has the following format:
2017-05-12_09-09-36 10.22.23
where:
- the last time represents the actual time used for the respective needle
- the first time represents the starting time of the intervention
