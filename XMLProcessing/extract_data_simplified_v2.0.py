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
import IREExtractClass as ie
from extractTPEsXml import extractTPES
from elementExistsXml import elementExists
#%%

def I_parseRecordingXML(filename, patient):
    ''' try to open and parse the xml filename
        if error, return message
    '''
    # TO DO: add the patient ID from the folder name
    try:
        xmlobj = ut.parse(xmlfilename)
        return xmlobj
    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None


def IV_parseNeedles(childrenTrajectories, lesion):
    ''' Parse Invidiual Needle Trajectories. Extract the TPE Errors
        INPUT: 1. xml tree structure for child trajectories 2. lesion object
        OUTPUT: doesn't return anything, just sets the TPEs
    '''
#    print(childrenTrajectories)
    for singleTrajectory in childrenTrajectories:
        if elementExists(singleTrajectory,'singleTrajectory', 'Measurements') is False:
            print('No Measurement for this needle') 
            # nothing to replace
        else:
            targetLateral,targetAngular,targetLongitudinal, targetResidual \
                = extractTPES(singleTrajectory.Measurements.Measurement.TPEErrors)
                
             # TO DO: check if the <Measurements> exists, overwrite it
             # Search function implemented in IREExract Class
            needle = lesion.NewNeedle(False) # False - the needle is not a reference trajectory
            epV = singleTrajectory.Measurements.Measurement.EntryPoint.cdata
            tpV = singleTrajectory.Measurements.Measurement.TargetPoint.cdata
            epP = singleTrajectory.EntryPoint.cdata
            tpP = singleTrajectory.TargetPoint.cdata
            needle.setPlannedTrajectory(ie.Trajectory(epP,tpP))
            needle.setValidationTrajectory(ie.Trajectory(epV,tpV))
            tps = needle.setTPE(ie.TPEErrors())
            tps.setTPEErrors(targetLateral, targetAngular,targetLongitudinal, targetResidual)
    


def III_parseTrajectory(trajectories):
    
    ''' Parse Trajectories at lesion level. For each lesion, a new Parent Trajectory is defined
        INPUT: list of Parent Trajectories
        OUTPUT: list of Needle Trajectories
    '''
    # lesion level
    for xmlTrajectory in trajectories:
        # check whether it's IRE trajectory
        if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:
            # TO DO: -check if patient[i].lesion[k] already exists
            # if lesion doesn't exist create, otherwise overwrite
            targetPoint = xmlTrajectory.TargetPoint.cdata
            location = np.array([float(i) for i in targetPoint.split()])
            # does a different lesion need to be created every time
            lesion = patient.addNewLesion(location)
            needle1 = lesion.newNeedle(True)
            ep = np.array([float(i) for i in xmlTrajectory.EntryPoint.cdata.split()])
            tp = np.array([float(i) for i in xmlTrajectory.TargetPoint.cdata.split()])
            needle1.setPlannedTrajectory(ie.Trajectory(ep,tp))
            childrenTrajectories = xmlTrajectory.Children.Trajectory
    
        elif not(xmlTrajectory['type'] and 'EG_ATOMIC' in xmlTrajectory['type']):
            # TO DO: no reference trajectory defined - CAS old version
            childrenTrajectories = xmlTrajectory
            # 
        else:
            print('MWA Needle') # and continue to loop through the parent trajectories
            continue
        
#        return childrenTrajectories, lesion
        # call function to assign the needles for each lesion
        IV_parseNeedles(childrenTrajectories, lesion)



def II_parseTrajectories(xmlobj):
    ''' INPUT: xmlobj tree structured parsed by function
        OUTPUT: Trajectories (if exist) extracted from XML File
    '''
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        return trajectories
    except Exception:
        print('No trajectory was found in the excel file')
        return None

#%%   
xmlfilename = 'multipleLesionsIRE.xml'
xmlobj = I_parseRecordingXML(xmlfilename,'1')
patient = ie.Patient(1)
if xmlobj is not None:
    trajectories = II_parseTrajectories(xmlobj)

# call the 3rd function to parse the needles
III_parseTrajectory(trajectories)
    
