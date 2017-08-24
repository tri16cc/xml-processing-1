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
import  AngleNeedles
from datetime import datetime
#%%

# iterate through all folders and subfolders
# generally the log files are in the folder "XML Recording"
# create zip dump if necessary (probably it is) !!!!
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
                                                 'LateralError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetLateral'][0:4],
                                                 'LongitudinalError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetLongitudinal'][0:4],
                                                 'AngularError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetAngular'][0:4],
                                                 'ResidualError': trajectoryIRE.Measurements.Measurement.TPEErrors['targetResidualError'][0:4],
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
df1 = pd.DataFrame(IRE_data)   # convert list of dicts to pandas dataframe
# drop duplicates measurements
df2 = df1.drop_duplicates(subset=['ResidualError'], keep='last')
#
## drop duplicates rows (check by needle column) and keep the last value row. assuming the last value it's the latest and the correct trajectory value used
df3 = df2.loc[(df2['NeedleCount'].shift() != df2['NeedleCount'])]


#%%
# generate unique PatientID
patient_unique = df3['PatientID'].unique()
#d = dict([(y,x+1) for x,y in enumerate(set(sorted(df3['patientID'])))])
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
- extract the EntryPoint, Target Point
- calculate angle in-between each needle
- calculate the angle between each needle and the reference trajectory needle 
- call the functions AngleNeedles
'''
max_Needles = max(df5['NeedleCount'])
NeedleCount = df5['NeedleCount'].tolist()
LesionCount = df5['LesionCount'].tolist()
entryNeedle = df5['entryNeedle'].tolist()
targetNeedle = df5['targetNeedle'].tolist()
entryRef = df5['entryRef'].tolist()
targetRef = df5['targetRef'].tolist()

# between each needle and the target reference needle (+1)
list_angles = np.empty((0,max_Needles+1))
        
for patient in patient_unique:
    
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
        matrix_angles = np.empty(shape=(len(needles_lesion),max_Needles+1))
        matrix_angles[:] = np.NAN
        
        for permutation_angles in itertools.permutations(needles_lesion,2):
            # we substract 1 because indexing starts from 0 in Python
            epNeedle1 = entryNeedle[permutation_angles[0]-1]
            tpNeedle1 = targetNeedle[permutation_angles[0]-1]
            epNeedle2 = entryNeedle[permutation_angles[1]-1]
            tpNeedle2 = targetNeedle[permutation_angles[1]-1]
            
            angle_degrees = AngleNeedles.angle_between(epNeedle1,tpNeedle1, epNeedle2,tpNeedle2)
            # round to 2 decimals
            angle_value = float("{0:.2f}".format(angle_degrees))
            matrix_angles[permutation_angles[0]-1,permutation_angles[1]-1] = angle_value
            matrix_angles[permutation_angles[1]-1,permutation_angles[0]-1] = angle_value
            
        for k, entry_needle in enumerate(entryRef): 
            angle_degrees = AngleNeedles.angle_between(entryNeedle[k],targetNeedle[k],entry_needle,targetRef[k])
            angle_value = float("{0:.2f}".format(angle_degrees))
            # add the angle with the central target reference on the last column
            matrix_angles[k,max_Needles] = angle_value
            
        list_angles = np.append(list_angles,matrix_angles,axis=0)
        
#%% write to Excel
'''
- convert list_angles to DataFrame type
- convert columns to numeric type to allow Excel operations over columns
- write the DataFrame to the Excel file
''' 
# drop columns that are not needed anymore in visualization mode
df5.drop({'entryNeedle', 'entryRef', 'targetNeedle', 'targetRef'},axis=1, inplace=True)
list_angles_df = pd.DataFrame(list_angles)
#create columns names string vector
angles_columns_names = [('Angle' + str(i+1)) for i in range(0,max_Needles)]
angles_columns_names.append('AngleReference')
list_angles_df.columns = angles_columns_names
df_final = pd.concat([df5, list_angles_df], axis=1)

df_final.apply(pd.to_numeric, errors='ignore')
df_final[['LateralError','LongitudinalError', 'AngularError', 'ResidualError']] = \
df_final[['LateralError','LongitudinalError', 'AngularError', 'ResidualError']].apply(pd.to_numeric)

#convert to datetime
s2 = df_final['time']
d = s2.str.split('_').str.get(0)
t = s2.str.split('_').str.get(1)
t1 = t.str.split().str.get(0)
t2 = t.str.split().str.get(1).str.replace('.',':')
df_final['time'] = d.astype(str) + ' ' + t2
#datetime_object = datetime.strptime(df_final['time'].to_string, '%Y-%m-%d %H:%M:%S')

# rename columns - add [mm]  in the title columns
df_final.rename(columns={'LateralError': 'LateralError[mm]', 'LongitudinalError': 'LongitudinalError[mm]',
                         'AngularError':'AngularError[mm]','ResidualError':'ResidualError[mm]',
                         'LesionCount':'LesionNr', 'NeedleCount':'NeedleNr'}, inplace=True)
#%%
# Write to Excel File
timestr = time.strftime("%Y%m%d-%H%M%S")
filename = 'IRE_NeedleInformation_' + timestr + '.xlsx' 
writer = pd.ExcelWriter(filename)
df_final.to_excel(writer,sheet_name='IRE_Angles', index=False, na_rep='NaN')
df3.to_excel(writer,'Sheet2', index=False) 
df1.to_excel(writer,'Sheet4', index=False)

workbook = writer.book
worksheet = writer.sheets['IRE_Angles']
worksheet.set_zoom(90)
# set row/columns width
worksheet.set_column('A:W', 20)
worksheet.set_default_row(26)
worksheet.set_row(0, 30)

# Add a format. Light red fill with dark red text.
format2 = workbook.add_format({'bg_color': '#D3D3D3',
                               'font_color': '	#000000'})                               
                                               
# might need to update the range for angles if new columns are added to the DataFrame
worksheet.conditional_format('A2:W200', {'type':  'text',
                                        'criteria': 'begins with',
                                        'value':    'N',
                                        'format':   format2})

writer.save()