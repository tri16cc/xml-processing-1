# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 13:26:12 2018

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
rootdir = "C:/IRE_Stockholm_35cases/"
# dictionary data type structure where measurements TPE will be saved
IRE_data = []
patID_list = []

for root, dirs, files in os.walk(rootdir):

    for file in files:
#        if file extension is *.xml and if it contains the name validation
        fileName,fileExtension = os.path.splitext(file)
        if fileExtension.lower().endswith('.xml') and 'validation'in fileName.lower():
            xmlFilePathName = os.path.join(root, file)
            xmlfilename = os.path.normpath(xmlFilePathName)
#            print(xmlfilename)
            idx = xmlfilename.index('_Pat')
            # only works if patient_id has max 2 digits
            if xmlfilename[idx-2].isdigit():
                patientID = xmlfilename[idx-2:idx]
            else:
                patientID = xmlfilename[idx-1]
                
            patID_list.append(patientID)
            
            obj = ut.parse(xmlfilename)
            try:
                data = obj.Eagles.Trajectories.Trajectory
                CAS_version = obj.Eagles['version']
                
                for trajectory in data:
                     if (trajectory['type']) and 'IRE' in trajectory['type']:
                                epRef = trajectory.EntryPoint.cdata  # entry point coordinates for the reference IRE trajectory
                                tpRef = trajectory.TargetPoint.cdata # target point coordinates for the reference IRE trajectory
                                # iterate through IRE ChildrenTrajectories
                                childrenTrajectory = trajectory.Children.Trajectory
                                NeedleCount = 0
                                for singleTrajectory in childrenTrajectory:
                                    # extract TPE errors from children Trajectories (angular, lateral, residual)
                                    # extract 
                                    NeedleCount +=1
                                    try:
                                        if (singleTrajectory.Measurements.Measurement.TPEErrors['targetLateral']):
                                            single_measurement_errors = {
                                                                 'PatientID': patientID,
                                                                 'casVersion': CAS_version,
                                                                 'NeedleCount': NeedleCount,
                                                                 'LateralError': singleTrajectory.Measurements.Measurement.TPEErrors['targetLateral'][0:5],
                                                                 'LongitudinalError': singleTrajectory.Measurements.Measurement.TPEErrors['targetLongitudinal'][0:5],
                                                                 'AngularError': singleTrajectory.Measurements.Measurement.TPEErrors['targetAngular'][0:5],
                                                                 'ResidualError': singleTrajectory.Measurements.Measurement.TPEErrors['targetResidualError'][0:5],
                                                                 'entryNeedle': singleTrajectory.Measurements.Measurement.EntryPoint.cdata,
                                                                 'targetNeedle': singleTrajectory.Measurements.Measurement.TargetPoint.cdata,
                                                                 'entryRef': epRef,
                                                                 'targetRef': tpRef}
                                            IRE_data.append(single_measurement_errors)
                                    except Exception:
                                        print('no measurement found', xmlfilename)
            except AttributeError:
                    print('Trajectories have no attribute Trajectory:', xmlfilename)
#%%
'''convert dictionary to dataframe for easier manipulation'''                               
df = pd.DataFrame(IRE_data)  
patient_unique = df['PatientID'].unique()          