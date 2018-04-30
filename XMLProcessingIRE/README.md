
1. extract the IRE needle information 
2. calculate the angle in-between the needles
3. extract the Target Positioning Errors

General tasks:
- iterate through all folders and subfolders
- generally the log files are in the folder "XML Recording"
- if file extension is *.xml and if it contains the name validation then it contains the validated needle information
- create zip dump if necessary 
- iterate through all files that contain IRE measurement
- save the most recent to date information (as multiple records are automatically generated during the intervention)
- not all the needle validations are in the same log file (Validation XML)
 
The date from the XML log files has the following format:
2017-05-12_09-09-36 10.22.23
where:
- the last time represents the actual time used for the respective needle
- the first time represents the starting time of the intervention
