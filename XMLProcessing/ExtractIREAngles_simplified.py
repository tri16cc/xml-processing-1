# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 13:21:23 2017

@author: Raluca Sandu
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 15:25:23 2017
main file. 
- unzip folders and find XML files.
- extract IRE needle information into CSV/Excel File
@author: Raluca Sandu
"""

import os
import time
import itertools
import numpy as np
import pandas as pd
import untangle as ut
import AngleNeedles

#%%

# iterate through all folders and subfolders
# generally the log files are in the folder "XML Recording"
# create zip dump if necessary (probably it is)
# iterate through all files that contain IRE measurement
# 

#%%
rootdir = "C:/Users/Raluca Sandu/Documents/MATLAB/My CAS-One Data/"

IRE_data = []
# assign random number to LesionCount column, update it later after removing duplicates/errors
LesionCount = 1

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
#        if file extension is *.xml and if it contains the name validation
        fileName,fileExtension = os.path.splitext(file)
        if fileExtension.lower().endswith('.xml') and 'validation'in fileName.lower():
            xmlFilePathName = os.path.join(subdir, file)
          
            xmlfilename = os.path.normpath(xmlFilePathName)
            obj = ut.parse(xmlfilename)
            data = obj.Eagles.Trajectories.Trajectory
            
            LesionCount = 1
            
            for trajectory in data:
                try:
                    # check if it's IRE trajectory
                    if 'IRE' in trajectory['type']:
                        patientID = obj.Eagles.PatientData['patientID']
                        casVersion  = obj.Eagles['version']
                        timeIRE = obj.Eagles['time']
                        seriesID = obj.Eagles.PatientData['seriesID']
                        seriesNo = obj.Eagles.PatientData['seriesNumber']
                        epRef = trajectory.EntryPoint.cdata  # entry point coordinates for the reference IRE trajectory
                        tpRef = trajectory.TargetPoint.cdata # target point coordinates for the reference IRE trajectory
                        
                        childrenTrajectory = trajectory.Children.Trajectory
                        NeedleCount = 0
                        for trajectoryIRE in childrenTrajectory:
                            # extract TPE errors from children Trajectories (angular, lateral, residual)
                            # extract 
                            NeedleCount +=1
                            single_measurement_errors = {
                                                 'PatientID': patientID,
                                                 'casVersion': casVersion,
                                                 'time': timeIRE,
                                                 'seriesID': seriesID,
                                                 'seriesNo': seriesNo,
                                                 'NeedleCount': NeedleCount,
                                                 'LesionCount': LesionCount,
                                                 'LateralError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetLateral'][0:5],
                                                 'LongitudinalError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetLongitudinal'][0:5],
                                                 'AngularError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetAngular'][0:5],
                                                 'ResidualError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetResidualError'][0:5],
                                                 'entryNeedle': trajectoryIRE.Measurements.Measurement.EntryPoint.cdata,
                                                 'targetNeedle':trajectoryIRE.Measurements.Measurement.TargetPoint.cdata,
                                                 'entryRef': epRef,
                                                 'targetRef': tpRef}
                            
                            IRE_data.append(single_measurement_errors)
                        
                except Exception:
                    print(xmlfilename)
                    pass

#%%
'''
    - format the data frame
    - remove duplicate measurements (in case the log file appears several times in several folders)
    - drop duplicate needle trajectory (sometimes only one need trajectory is changed, so the other needles is repeated)
'''  
#convert list of dicts to pandas dataframe                        
df1 = pd.DataFrame(IRE_data)  
# drop duplicates measurements
df2 = df1.drop_duplicates(subset=['ResidualError'], keep='last')
#
## drop duplicates rows (check by needle column) and keep the last value row. assuming the last value it's the latest and the correct trajectory value used
df3 = df2.loc[(df2['NeedleCount'].shift(1) != df2['NeedleCount'])]


#%%
# generate unique PatientID
patient_unique = df2['PatientID'].unique()
d = dict([(y,x+1) for x,y in enumerate(patient_unique)])
patientID_column = [d[x] for x in df3['PatientID']]
df4 = df3.assign(PatientIndex = patientID_column)

# re-arrange th columns order
df5 = df4[['PatientIndex','PatientID','NeedleCount','LesionCount',\
           'casVersion','time','seriesNo','seriesID', 'LateralError',
           'LongitudinalError', 'AngularError', 'ResidualError', \
           'entryNeedle', 'targetNeedle', 'entryRef', 'targetRef']]

# update the index
df5 = df5.reset_index(drop=True)
#%%
# update the number of lesions for each unique patient number, each number of needles
LesionCount = []
for patient  in patient_unique:
    # select all the rows belonging to a patient
    patient_data = df5[df5['PatientID']==patient]
    NeedleCount = patient_data['NeedleCount'].tolist()
    LesionIdx = 1
    LesionCount.append(LesionIdx)
    
    for i in range(1,len(NeedleCount)):
        
        if NeedleCount[i] < NeedleCount[i-1]:
             # theta angle needle 0 and needle 1
             LesionIdx +=1
             LesionCount.append(LesionIdx)
             
        else:
             LesionCount.append(LesionIdx)
             
df5['LesionCount'] = LesionCount


#%% calculate the angle between needles
'''
- extract the EntryPoint, Target Point, Reference Trajectory
- calculate angle in-between each needle
- calculate the angle between each needle and the reference trajectory needle 
- call the functions AngleNeedles
'''

needleA = []
needleB = []
AngleDegrees = []
LesionNr = []
PatientID_angles = [] 
PatientIdx_angles = []
    
for PatientIdx, patient in enumerate(patient_unique):
    
    patient_data = df5[df5['PatientID']==patient]
    lesion_unique = patient_data['LesionCount'].unique()
    # for each unique number of lesion select the corresponding patient data
    # compute permutations of the needles count used in that lesion
    # calculate angles for each permutations, add the vaalues to the corresponding columns
    #
    for i, lesion in enumerate(lesion_unique):
        lesion_data = patient_data[patient_data['LesionCount']==lesion]
        needles_lesion = lesion_data['NeedleCount'].tolist()
        entryNeedle = lesion_data['entryNeedle'].tolist()
        targetNeedle = lesion_data['targetNeedle'].tolist()
        entryRef = lesion_data['entryRef'].tolist()
        targetRef = lesion_data['targetRef'].tolist()
        needleA_lesion = []
        needleB_lesion = []
        AngleDegrees_lesion = []
        
        
        for combination_angles in itertools.combinations(needles_lesion,2):
            # we substract 1 because indexing starts from 0 in Python
            # add permutations to list/table
            list_needleA = combination_angles[0]
            list_needleB = combination_angles[1]
            epNeedle1 = entryNeedle[combination_angles[0]-1]
            tpNeedle1 = targetNeedle[combination_angles[0]-1]
            epNeedle2 = entryNeedle[combination_angles[1]-1]
            tpNeedle2 = targetNeedle[combination_angles[1]-1]
            
            angle = AngleNeedles.angle_between(epNeedle1,tpNeedle1, epNeedle2,tpNeedle2)
            # round to 2 decimals
            angle_value = float("{0:.2f}".format(angle))
            needleA_lesion.append(combination_angles[0]) 
            needleB_lesion.append(combination_angles[1])
            AngleDegrees_lesion.append(angle_value)
            
        for k, entry_needle in enumerate(entryRef): 
            angle = AngleNeedles.angle_between(entryNeedle[k],targetNeedle[k],entry_needle,targetRef[k])
            angle_value = float("{0:.2f}".format(angle))
            # add the angle with the central target reference on the last column
            needleA_lesion.append(k+1)
            needleB_lesion.append('Reference')
            AngleDegrees_lesion.append(angle_value)
        
        # generate new lesion column based on the length of needleA/needleB column
        LesionNr.append(np.ones((len(AngleDegrees_lesion),1))*lesion)
        PatientID_angles.append(np.ones((len(AngleDegrees_lesion),1))*int(patient))
        PatientIdx_angles.append(np.ones((len(AngleDegrees_lesion),1))*(int(PatientIdx)+1))
        needleA.append(needleA_lesion)
        needleB.append(needleB_lesion)
        AngleDegrees.append(AngleDegrees_lesion)
        

# flatten list of lists using nested list comprehension

PatientIdx_all = np.concatenate(PatientIdx_angles).ravel().astype(int).tolist()
PatientID = np.concatenate(PatientID_angles).ravel().astype(str)
PatientID_all = [substring[:-2] for substring in PatientID]
LesionNr_all = np.concatenate(LesionNr).ravel().astype(int).tolist()
needleA_all = np.concatenate(needleA).ravel().tolist()
needleB_all = np.concatenate(needleB).ravel().tolist()
AngleDegrees_all = np.concatenate(AngleDegrees).ravel().tolist()


# convert to DataFrame 
df_angles = pd.DataFrame(np.column_stack([PatientIdx_all, PatientID_all, LesionNr_all, needleA_all,
                                          needleB_all, AngleDegrees_all]), 
                               columns=['PatientNr', 'PatientID', 'LesionNr',
                                        'NeedleA', 'NeedleB', 'AngleDegrees'])
        
df_angles[['AngleDegrees']] = df_angles[['AngleDegrees']].apply(pd.to_numeric)

#%% write to Excel
'''
#- convert list_angles to DataFrame type
#- write the DataFrame to the Excel file
#''' 

## Write to Excel File
timestr = time.strftime("%Y%m%d-%H%M%S")
filename = 'IRE_justAngles_' + timestr + '.xlsx' 
filepathExcel = os.path.join(rootdir, filename)
writer = pd.ExcelWriter(filepathExcel)
df_angles.to_excel(writer,sheet_name='IRE_Angles', index=False, na_rep='NaN')

workbook = writer.book
worksheet = writer.sheets['IRE_Angles']
worksheet.set_zoom(90)
# set row/columns width
worksheet.set_column('A:W', 14)
worksheet.set_default_row(26)
worksheet.set_row(0, 30)

 # #E5E8E8                                 
format1 = workbook.add_format({'bg_color': '#d5d8dc',
                               'font_color': '#000000'})


worksheet.conditional_format('Q2:V100', {'type':  'text',
                                        'criteria': 'begins with',
                                        'value':    'N',
                                        'format':   format1})

