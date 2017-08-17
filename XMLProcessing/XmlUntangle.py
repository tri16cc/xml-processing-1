# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 18:46:34 2017

@author: Raluca Sandu
"""

import untangle as ut
import os
import math
import pandas as pd
import numpy as np

#
#def read_recording_xml(xmlfilename):
      
xmlfilename = 'xmlTestFile.xml'
folder = os.path.dirname(xmlfilename)
#    myDirname = os.path.normpath("c:/aDirname/")
obj = ut.parse(xmlfilename)
data = obj.Eagles.Trajectories.Trajectory

LesionCount = 0 # if the patient has multiple lesions with several IREs
Lateral = []
Longitudinal = []
Angular = []
ResidualError = []
flag_IRE = 0

for trajectory in data:
    try:
        # check if it's IRE trajectory
        if 'IRE' in trajectory['type']:
            childrenTrajectory = trajectory.Children.Trajectory
            flag_IRE = 1
            for trajectoryIRE in childrenTrajectory:
                # extract TPE errors
                Lateral.append(trajectoryIRE.Measurements.Measurement.TPEErrors['targetLateral'])
                Longitudinal.append(trajectoryIRE.Measurements.Measurement.TPEErrors['targetLongitudinal'])
                Angular.append(trajectoryIRE.Measurements.Measurement.TPEErrors['targetAngular'])
                ResidualError.append(trajectoryIRE.Measurements.Measurement.TPEErrors['targetResidualError'])

    except Exception:
        pass
 
columns = ['PatientID','CasVersion','time','seriesNo','seriesID','LesionCount', 'needleCount', 'LateralErr', \
           'LongitudinalErr', 'AngularErr', 'ResidualErr']
df = pd.DataFrame(index=[], columns=columns)    
df = df.fillna(0)

df['LateralErr'] = Lateral
df['LongitudinalErr'] = Longitudinal
df['AngularErr'] = Angular
df['ResidualErr'] = ResidualError

df['PatientID'] = obj.Eagles.PatientData['patientID']
df['CasVersion'] = obj.Eagles['version']
df['time'] = obj.Eagles['time']
df['seriesID'] = obj.Eagles.PatientData['seriesID']
df['seriesNo'] = obj.Eagles.PatientData['seriesNumber']
df['LesionCount'] = 1

# if new file with IRE  measurement --> check if patient iD exists already
# if patID exists, append below it (later change to insertion) information
# increase the number of lesions accordingly
# write DataFrame to CSV after parsing through all files
#    
