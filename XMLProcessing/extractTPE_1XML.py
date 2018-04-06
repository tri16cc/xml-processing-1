# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 18:46:34 2017

@author: Raluca Sandu
"""

import numpy as np
import pandas as pd
import untangle as ut
from datetime import datetime
#%%
'''Functions for Parsing the XML Structure'''

def elementExists(node, attr):
    '''check if elements exists, as a xml tag or as an attribute'''
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
      
xmlfilename = 'multipleLesionsIRE.xml'
LesionCount = 0 # if the patient has multiple lesions with several IREs

IRE_data = []
patientID = 'test'

try:
    obj = ut.parse(xmlfilename)
except Exception:
    print('XML file structure is broken, cannot read XML')
#    continue

try:
    trajectories = obj.Eagles.Trajectories.Trajectory
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

#%%
NeedleCount = 0
LesionCount = 0
# count how many children trajectories are defined --> number of lesions
for trajectory in trajectories:
    
    if (trajectory['type']) and 'IRE' in trajectory['type']:
        LesionCount +=1
        childrenTrajectory = trajectory.Children.Trajectory
    elif not(trajectory['type'] and 'EG_ATOMIC' in trajectory['type']):
        childrenTrajectory = trajectory
        LesionCount +=1

Lesions = [[] for x in range(LesionCount)]

for trajectory in trajectories:
    Needle = 0       
    for singletrajectory in childrenTrajectory:
        NeedleCount +=1
# define lists for lesion and needle

Needles = [[] for x in range(NeedleCount)]
# count how many trajectories are defined into the children trajectory --> number of needles for each trajectory
#%%
for trajectory in trajectories:
    if (trajectory['type']) and 'IRE' in trajectory['type']:
        epRef = trajectory.EntryPoint.cdata  # entry point coordinates for the reference IRE trajectory
        tpRef = trajectory.TargetPoint.cdata # target point coordinates for the reference IRE trajectory
        # iterate through IRE ChildrenTrajectories
        childrenTrajectory = trajectory.Children.Trajectory
    elif not(trajectory['type'] and 'EG_ATOMIC' in trajectory['type']):
        childrenTrajectory = trajectory
        epRef = ''
        tpRef = ''
    else:
        print('MWA Needle')
        continue
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
#            NeedleCount+=1
            IRE_data.append(single_measurement_errors)

#%%                
df1 = pd.DataFrame(IRE_data)              

