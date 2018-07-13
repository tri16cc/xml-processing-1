Workflow:
1. extract the needle information - trajectory plan and validation
2. extract the Target Positioning Errors (TPEs)
3. extract the Segmentation Filepaths
Optional
3. calculate the angle in-between the needles (IRE)
4. connect with database of needle ellipsoide radii (MWA, IRE etc)

General tasks:
- iterate through all folders and subfolders
- generally the log files are in the folder "XML Recording"
- if file extension is *.xml and if it contains the name validation then it contains the validated needle informatio
- create zip dump if necessary 
- iterate through all files that contain IRE measurement
- save the most recent to date information (as multiple records are automatically generated during the intervention)
- not all the needle validations are in the same log file (Validation XML)
 
The date from the XML log files has the following format:
2017-05-12_09-09-36 10.22.23
where:
- the last time represents the actual time used for the respective needle
- the first time represents the starting time of the intervention
