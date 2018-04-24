# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 14:12:55 2017

@author: Raluca Sandu
"""
import os
import time 
import numpy as np
import pandas as pd
import untangle as ut
from datetime import datetime
#%%
#rootdir = "C:/Users/Raluca Sandu/Documents/LiverInterventionsBern_Ablations/4patients/"
rootdir = "C:/Users/Raluca Sandu/Documents/LiverInterventionsBern_Ablations/4patients/Pat_Chonge Tamdi Ongju_0003067149_2017-10-24_10-02-47/Technical Report/XML Recordings"
#
IR_data = []
# assign random number to LesionCount column, update it later after removing duplicates/errors

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
#        if file extension is *.xml and if it contains the name validation
        fileName,fileExtension = os.path.splitext(file)
        if fileExtension.lower().endswith('.xml') and 'validation'in fileName.lower():
            xmlFilePathName = os.path.join(subdir, file)
            xmlFilePath = os.path.normpath(xmlFilePathName)
            try:
                obj = ut.parse(xmlFilePath)
                data = obj.Eagles.Trajectories.Trajectory
                # count the number of trajectories defined in the validation log file.
                # the number of trajectories just indicat the number of needles used.
                NCount = []
                NCount = [ 1 for trajectory in data if 'EG_ATOMIC_TRAJECTORY' in trajectory['type']]  
                NeedleCount = 0
                for trajectory in data:
                    
                    try:
                        # check if it's IRE trajectory
                        if 'EG_ATOMIC_TRAJECTORY' in trajectory['type']:
                            patientID = obj.Eagles.PatientData['patientID']
                            casVersion  = obj.Eagles['version']
                            timeIR = obj.Eagles['time']
                            seriesID = obj.Eagles.PatientData['seriesID']
                            seriesNo = obj.Eagles.PatientData['seriesNumber']
                            epRef = trajectory.EntryPoint.cdata  # entry point coordinates for the reference IRE trajectory
                            tpRef = trajectory.TargetPoint.cdata # target point coordinates for the reference IRE trajectory

                            # extract TPE errors from Measurements Trajectories (angular, lateral, residual)
                            NeedleCount +=1
                            single_measurement_errors = {
                                                 'PatientID': patientID,
                                                 'casVersion': casVersion,
                                                 'time': timeIR,
                                                 'seriesID': seriesID,
                                                 'seriesNo': seriesNo,
                                                 'NeedleCount': NeedleCount,
                                                 'NCount': len(NCount),
                                                 'LateralError': trajectory.Measurements.Measurement.TPEErrors['targetLateral'][0:4],
                                                 'LongitudinalError': trajectory.Measurements.Measurement.TPEErrors['targetLongitudinal'][0:4],
                                                 'AngularError': trajectory.Measurements.Measurement.TPEErrors['targetAngular'][0:4],
                                                 'ResidualError': trajectory.Measurements.Measurement.TPEErrors['targetResidualError'][0:4],
                                                 'entryNeedle': trajectory.Measurements.Measurement.EntryPoint.cdata,
                                                 'targetNeedle':trajectory.Measurements.Measurement.TargetPoint.cdata,
                                                 'entryRef': epRef,
                                                 'targetRef': tpRef}
                                
                            IR_data.append(single_measurement_errors)
                            
                    except Exception:
                        print(xmlFilePath)
                        pass
            # the xml doesn't contain any trajectory or is impossible to parse due some weird error/trailing characters
            except Exception:
                print(xmlFilePath)
                pass
#%%
'''
    - format the data frame
    - remove duplicate measurements (in case the log file appears several times in several folders)
    - drop duplicate needle trajectory (sometimes only one need trajectory is changed, so the other needles is repeated)
'''  
                      
df1 = pd.DataFrame(IR_data)   # convert list of dicts to pandas dataframe
# drop duplicates measurements
df2 = df1.drop_duplicates(subset=['ResidualError'], keep='last')
#
# drop duplicates rows (check by needle count) and keep the last value row. assuming the last value it's the latest and the correct trajectory value used
df3 = df2.loc[(df2['NeedleCount'].shift(-1) != df2['NeedleCount'])]

#%%
''' generate unique PatientID'''
patient_unique = df3['PatientID'].unique()
#d = dict([(y,x+1) for x,y in enumerate(set(sorted(df3['patientID'])))])
d = dict([(y,x+1) for x,y in enumerate(patient_unique)])
patientID_column = [d[x] for x in df3['PatientID']]
df4 = df3.assign(PatientIndex = patientID_column)

#%%
''' update the number of lesions for each unique patient number, each number of needles'''
NeedleCount = []
for patient  in patient_unique:
    # select all the rows belonging to a patient
    patient_data = df4[df4['PatientID']==patient]
    NeedleCount.append(np.arange(1,patient_data['NCount'].iloc[1]+1))

NeedleCount_flattened = [item for sublist in NeedleCount for item in sublist]
  
df4['NeedleCount'] = NeedleCount_flattened 
#%%

# re-arrange th columns order
df5 = df4[['PatientIndex','PatientID','NeedleCount',\
           'casVersion','time','seriesNo','seriesID', 'LateralError',
           'LongitudinalError', 'AngularError', 'ResidualError', \
           'entryNeedle', 'targetNeedle', 'entryRef', 'targetRef']]

# update the index
df5 = df5.reset_index(drop=True)
#%%


timestr = time.strftime("%Y%m%d-%H%M%S")
filename = 'MWA_NeedleInformation_' + timestr + '.xlsx' 
filepathExcel = os.path.join(rootdir, filename )
writer = pd.ExcelWriter(filepathExcel)
df5.to_excel(writer, index=False, na_rep='NaN'),
writer.save()
#










