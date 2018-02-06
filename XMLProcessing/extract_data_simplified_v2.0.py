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

def I_parseRecordingXML(filename, patient):
    try:
        obj = ut.parse(xmlfilename)
    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None


def III_parseTrajectory(trajectories):
    # lesion level
    for xmlTrajectory in trajectories:
        # check whether it's IRE trajectory
        if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:
            # check if patient[i].lesion[k] already exists
            # if lesion doesn't exist create, otherwise overwrite
            targetPoint = xmlTrajectory.TargetPoint.cdata
            location = np.array([float(i) for i in targetPoint.split()])
            lesion = patient.addNewLesion(ie.Lesion(location))
            needle1 = lesion.newNeedle()
#            trajectory.set(xmlTrajectory.EntryPoint.cdata)
#            trajectory.set(xmlTrajectory.TargetPoint.cdata)
            # tpNeedle1_xyz = np.array([float(i) for i in tpNeedle.split()])
            for singleTrajectory in xmlTrajectory.Children.Trajectory:
                parseTrajectory(singleTrajectory)
    
        elif not(trajectory['type'] and 'EG_ATOMIC' in trajectory['type']):
            trajectory = ie.Trajectory(False)
            trajectory = ie.Patient
        else:
            pass
    
        if elementExists('singleTrajectory', 'Measurements') is False:
                print('No Measurement for this needle')
            else:


def II_parseTrajectories(xmlobj):
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        return trajectories
    except Exception:
        print('No trajectory was found in the excel file')
        return None
    

xmlfilename = 'multipleLesionsIRE.xml'
xmlobj = I_parseRecordingXML(xmlfilename,'1')
patient = ie.Patient(1)
if xmlobj is not None:
    trajectories = II_parseTrajectories(xmlobj)
    
