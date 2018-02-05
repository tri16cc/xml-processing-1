# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""

import os
import time 
import untangle as ut
from datetime import datetime
import IRE_Extract as ie    

xmlfilename = 'multipleLesionsIRE.xml'

def parseRecordingXML(filename, patient):
    try:
        obj = ut.parse(xmlfilename)
        

    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None
    
    
def parseTrajectory(xmlTrajectory):
    trajectory = None
    if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:
        trajectory = ie.Trajectory(True)
        trajectory.set(xmlTrajectory.EntryPoint.cdata)
        trajectory.set(xmlTrajectory.TargetPoint.cdata)
        for singleTrajectory in xmlTrajectory.Children.Trajectory:
            parseTrajectory(singleTrajectory)
            
    elif not(trajectory['type'] and 'EG_ATOMIC' in trajectory['type']):
        trajectory = ie.Trajectory(False)
    else:
        pass
    
    if elementExists('singleTrajectory', 'Measurements') is False:
            print('No Measurement for this needle') 
        else:

    
def parseTrajectories(xmlobj):
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        
        for trajectory in trajectories:
            parseTrajectory(trajectory)
    except Exception:
        print('No trajectory was found in the excel file')
#    continue

    