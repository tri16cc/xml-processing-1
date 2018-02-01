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
from datetime import datetime
#%%
'''Functions for Parsing the XML Structure'''

def elementExists(node, attr):
    try:
        xmlElement = eval(node +'.' + attr)
        return True
    except Exception:
        nodeE = eval(node)
        if (nodeE[attr]):
             return True
        else:
            return False

#%%
#def read_recording_xml(xmlfilename):
      
#xmlfilename = 'C:/IRE_Stockholm_35cases/10_Pat_KAFAIE MARYAM/Study_1/Series_1/CAS-One Recordings/2015-07-14_09-43-39/Validation_Series_2_12_49_04.xml'
xmlfilename = 'testCas_2_5_v2.xml'
LesionCount = 0 # if the patient has multiple lesions with several IREs

IRE_data = []
patientID = 'test'


try:
    obj = ut.parse(xmlfilename)
except Exception:
    print('XML file structure is broken, cannot read XML')
#    continue

try:
    data = obj.Eagles.Trajectories.Trajectory
except Exception:
    print('No trajectory was found in the excel file')
#    continue

CAS_version = obj.Eagles['version']

# extract the time of the IR
timeIR = obj.Eagles['time']
# parse the time into datetime format
year, times = timeIR.split('_')
timeStart, timeEnd = times.split(' ')
datetime_End = datetime.strptime(year + ' ' + timeEnd, '%Y-%m-%d %H.%M.%S')
datetime_Start =  datetime.strptime(year + ' ' + timeStart, '%Y-%m-%d %H-%M-%S')

NeedleCount = 1
LesionCount = 1
# count how many children trajectories are defined --> number of lesions
#            for trajectory in data:
#                if (trajectory['type']) and 'IRE' in trajectory['type']:
#                    LesionCount +=1
#                    childrenTrajectory = trajectory.Children.Trajectory
#                    for singletrajectory in ChildrenTrajectory:
#                        Need 

# count how many trajectories are defined into the children trajectory --> number of needles for each trajectory
#%%
for trajectory in data:
    if (trajectory['type']) and 'IRE' in trajectory['type']:
        epRef = trajectory.EntryPoint.cdata  # entry point coordinates for the reference IRE trajectory
        tpRef = trajectory.TargetPoint.cdata # target point coordinates for the reference IRE trajectory
        # iterate through IRE ChildrenTrajectories
        childrenTrajectory = trajectory.Children.Trajectory
        for singleTrajectory in childrenTrajectory:
            if elementExists('singleTrajectory', 'Measurements') is False:
                print('No Measurement for this needle')
            else:
                if elementExists('singleTrajectory.Measurements.Measurement.TPEErrors', 'targetLateral'):
                    targetLateral = singleTrajectory.Measurements.Measurement.TPEErrors['targetLateral'][0:5]
                    targetLongitudinal = singleTrajectory.Measurements.Measurement.TPEErrors['targetLongitudinal'][0:5]
                    targetAngular = singleTrajectory.Measurements.Measurement.TPEErrors['targetAngular'][0:5]
                    targetResidual = singleTrajectory.Measurements.Measurement.TPEErrors['targetResidualError'][0:5]
                else:
                    # the case where the TPE errors are 0 in the TPE<0>. instead they are attributes of the measurement   
                    targetLateral = singleTrajectory.Measurements.Measurement['targetLateral'][0:5]
                    targetLongitudinal = singleTrajectory.Measurements.Measurement['targetLongitudinal'][0:5]
                    targetAngular = singleTrajectory.Measurements.Measurement['targetAngular'][0:5]
                    targetResidual = singleTrajectory.Measurements.Measurement['targetResidualError'][0:5]
                    
                single_measurement_errors = {
                                     'PatientID': patientID,
                                     'casVersion': CAS_version,
                                     'NeedleCount': NeedleCount,
                                     'LateralError': targetLateral,
                                     'LongitudinalError': targetLongitudinal,
                                     'AngularError': targetAngular,
                                     'ResidualError': targetResidual,
                                     'entryNeedle_Validation': singleTrajectory.Measurements.Measurement.EntryPoint.cdata,
                                     'targetNeedle_Validation': singleTrajectory.Measurements.Measurement.TargetPoint.cdata,
                                     'entryNeedle_Planning': singleTrajectory.EntryPoint.cdata,
                                     'targetNeedle_Planning': singleTrajectory.TargetPoint.cdata,
                                     'entryRef': epRef,
                                     'targetRef': tpRef,
                                     'datetime_Start':datetime_Start,
                                     'datetime_End': datetime_End}
                NeedleCount+=1
                IRE_data.append(single_measurement_errors)
            
    
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
