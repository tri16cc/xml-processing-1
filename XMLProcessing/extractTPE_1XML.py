# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 18:46:34 2017

@author: Raluca Sandu
"""

import untangle as ut
#import os
#import math
#import numpy as np
import pandas as pd


#%%
#def read_recording_xml(xmlfilename):
      
#xmlfilename = 'C:/IRE_Stockholm_35cases/10_Pat_KAFAIE MARYAM/Study_1/Series_1/CAS-One Recordings/2015-07-14_09-43-39/Validation_Series_2_12_49_04.xml'
xmlfilename = 'testCas_2_9_IRE.xml'
LesionCount = 0 # if the patient has multiple lesions with several IREs

IRE_data = []
obj = ut.parse(xmlfilename)
patientID = 'test'


#try:
data = obj.Eagles.Trajectories.Trajectory
CAS_version = obj.Eagles['version']
NeedleCount = 1
for trajectory in data:
    if (trajectory['type']) and 'IRE' in trajectory['type']:
                epRef = trajectory.EntryPoint.cdata  # entry point coordinates for the reference IRE trajectory
                tpRef = trajectory.TargetPoint.cdata # target point coordinates for the reference IRE trajectory
                # iterate through IRE ChildrenTrajectories
                childrenTrajectory = trajectory.Children.Trajectory
                for singleTrajectory in childrenTrajectory:
                    # extract TPE errors from children Trajectories (angular, lateral, residual)
                    # extract 
                    try:
                        if (singleTrajectory.Measurements):
                            try:
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
                                NeedleCount+=1
                                IRE_data.append(single_measurement_errors)
                                
                            except Exception:
                                single_measurement_errors = {
                                                     'PatientID': patientID,
                                                     'casVersion': CAS_version,
                                                     'NeedleCount': NeedleCount,
                                                     'LateralError': singleTrajectory.Measurements.Measurement['targetLateral'][0:5],
                                                     'LongitudinalError': singleTrajectory.Measurements.Measurement['targetLongitudinal'][0:5],
                                                     'AngularError': singleTrajectory.Measurements.Measurement['targetAngular'][0:5],
                                                     'ResidualError': singleTrajectory.Measurements.Measurement['targetResidualError'][0:5],
                                                     'entryNeedle': singleTrajectory.Measurements.Measurement.EntryPoint.cdata,
                                                     'targetNeedle': singleTrajectory.Measurements.Measurement.TargetPoint.cdata,
                                                     'entryRef': epRef,
                                                     'targetRef': tpRef}
                                
                                NeedleCount+=1
                                IRE_data.append(single_measurement_errors)
                    except Exception:
#                            print('no MEASUREMENT found for this angle:', xmlfilename)
                        pass
    else:
        try:
            single_measurement_errors = {
                     'PatientID': patientID,
                     'casVersion': CAS_version,
                     'NeedleCount': NeedleCount,
                     'LateralError': trajectory.Measurements.Measurement.TPEErrors['targetLateral'][0:5],
                     'LongitudinalError': trajectory.Measurements.Measurement.TPEErrors['targetLongitudinal'][0:5],
                     'AngularError': trajectory.Measurements.Measurement.TPEErrors['targetAngular'][0:5],
                     'ResidualError': trajectory.Measurements.Measurement.TPEErrors['targetResidualError'][0:5],
                     'entryNeedle': trajectory.Measurements.Measurement.EntryPoint.cdata,
                     'targetNeedle': trajectory.Measurements.Measurement.TargetPoint.cdata,
                     'entryRef': '',
                     'targetRef': ''}
            NeedleCount+=1
            IRE_data.append(single_measurement_errors)
        except Exception:
            print('no MEASUREMENT found for this angle:', xmlfilename)
            pass
        
                
#except AttributeError:
#        print('Trajectories have no attribute Trajectory:', xmlfilename)
        
#%%                
df1 = pd.DataFrame(IRE_data)              
#columns = ['PatientID','CasVersion','time','seriesNo','seriesID','LesionCount', 'needleCount', 'LateralErr', \
#           'LongitudinalErr', 'AngularErr', 'ResidualErr']
#
#df = pd.DataFrame(index=[], columns=columns)    
#df = df.fillna(0)
#
#df['LateralErr'] = Lateral
#df['LongitudinalErr'] = Longitudinal
#df['AngularErr'] = Angular
#df['ResidualErr'] = ResidualError
#
#df['PatientID'] = 99
#df['CasVersion'] = obj.Eagles['version']
#df['time'] = obj.Eagles['time']
##df['seriesID'] = obj.Eagles.PatientData['seriesID']
##df['seriesNo'] = obj.Eagles.PatientData['seriesNumber']
#df['LesionCount'] = 1

# if new file with IRE  measurement --> check if patient iD exists already
# if patID exists, append below it (later change to insertion) information
# increase the number of lesions accordingly
# write DataFrame to CSV after parsing through all files
#    
