# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""

import os
import time
import numpy as np
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



def extractTPES(tpes):
    '''function to extract the TPEs values'''
    
    if elementExists('singleTrajectory.Measurements.Measurement.TPEErrors', 'targetLateral'):
        targetLateral = tpes['targetLateral'][0:5]
        targetLongitudinal = tpes['targetLongitudinal'][0:5]
        targetAngular = tpes['targetAngular'][0:5]
        targetResidual = tpes['targetResidualError'][0:5]
    else:
        # the case where the TPE errors are 0 in the TPE<0>. instead they are attributes of the measurement   
        targetLateral = tpes['targetLateral'][0:5]
        targetLongitudinal = tpes['targetLongitudinal'][0:5]
        targetAngular = tpes['targetAngular'][0:5]
        targetResidual = tpes['targetResidualError'][0:5]
        
    return targetLateral, targetLongitudinal, targetAngular, targetResidual


def I_parseRecordingXML(filename, patient):
    try:
        xmlobj = ut.parse(xmlfilename)
        return xmlobj
    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None


def IV_parseNeedles(childrenTrajectories, lesion):
    
    for singleTrajectory in childrenTrajectories:
        if elementExists('singleTrajectory', 'Measurements') is False:
            print('No Measurement for this needle') 
            # nothing to replace
        else:
            targetLateral,targetAngular,targetLongitudinal, targetResidual \
                = extractTPES(singleTrajectory.Measurements.Measurement.TPEErrors)
                
         # TO DO: check if the <Measurements> exists, overwrite it
         #
        needle = lesion.NewNeedle(False)
        epV = singleTrajectory.Measurements.Measurement.EntryPoint.cdata
        tpV = singleTrajectory.Measurements.Measurement.TargetPoint.cdata
        epP = singleTrajectory.EntryPoint.cdata
        tpP = singleTrajectory.TargetPoint.cdata
        needle.setPlannedTrajectory(ie.Trajectory(epP,tpP))
        needle.setValidationTrajectory(ie.Trajectory(epV,tpV))
        tps = needle.setTPE(ie.TPEErrors())
        tps.setTPEErrors(targetLateral, targetAngular,targetLongitudinal, targetResidual)
    


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
            needle1 = lesion.newNeedle(True)
            ep = np.array([float(i) for i in xmlTrajectory.EntryPoint.cdata.split()])
            tp = np.array([float(i) for i in xmlTrajectory.TargetPoint.cdata.split()])
            needle1.setPlannedTrajectory(ie.Trajectory(ep,tp))
            childrenTrajectories = xmlTrajectory.Children.Trajectory
    
        elif not(xmlTrajectory['type'] and 'EG_ATOMIC' in xmlTrajectory['type']):
            # no reference trajectory defined - special case
            childrenTrajectories = xmlTrajectory
            #  special case TO DO
        else:
            print('MWA Needle') # and continue to loop through the trajectories
            continue
        
        # call function to assign the needles for each lesion
        IV_parseNeedles(childrenTrajectories, lesion)



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
    
