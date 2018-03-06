# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""
#from IPython import get_ipython
#get_ipython().magic('reset -sf')

import numpy as np
import pandas as pd
import untangle as ut
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
        xmlobj = ut.parse(filename)
        return xmlobj
    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None


def IV_parseNeedles(childrenTrajectories, lesion):
    ''' Parse Invidiual Needle Trajectories. Extract the TPE Errors
        INPUT: 1. xml tree structure for child trajectories 2. lesion object
        OUTPUT: doesn't return anything, just sets the TPEs
    '''
    for singleTrajectory in childrenTrajectories:

        epP = np.array([float(i) for i in singleTrajectory.EntryPoint.cdata.split()])
        tpP = np.array([float(i) for i in singleTrajectory.TargetPoint.cdata.split()])
        
        needle = lesion.findNeedle(tpP)
        
        if needle is None:
            needle = lesion.newNeedle(False) # False - the needle is not a reference trajectory
            tps = needle.setTPEs()
            validation = needle.setValidationTrajectory() 
            
        # add the entry and target points to the needle object
        planned = needle.setPlannedTrajectory()
        planned.setTrajectory(epP,tpP)

        
        if elementExists(singleTrajectory, 'Measurements') is False:
            print('No Measurement for this needle')  
           
        else:
            # find the right needle to replace the exact tpes
            # set the validation trajectory
            epV = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.EntryPoint.cdata.split()])
            tpV = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.TargetPoint.cdata.split()])
            validation = needle.setValidationTrajectory()
            validation.setTrajectory(epV,tpV)

            targetLateral,targetAngular,targetLongitudinal, targetEuclidean \
                = extractTPES(singleTrajectory.Measurements.Measurement)

            tps = needle.setTPEs()
            tps.setTPEErrors(targetLateral, targetAngular,targetLongitudinal, targetEuclidean)
    

def III_parseTrajectory(trajectories,patient):
    ''' Parse Trajectories at lesion level. For each lesion, a new Parent Trajectory is defined
        INPUT: list of Parent Trajectories
        OUTPUT: list of Needle Trajectories
    '''
    # lesion level
    for xmlTrajectory in trajectories:
        # check whether it's IRE trajectory
        ep = np.array([float(i) for i in xmlTrajectory.EntryPoint.cdata.split()])
        tp = np.array([float(i) for i in xmlTrajectory.TargetPoint.cdata.split()])
        
        if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:            
            
            # function to check if the lesion exists based on location returning true or false
            lesion = patient.findLesion(lesionlocation=tp, threshold=2) 
            
            if lesion is None:
                lesion = patient.addNewLesion(tp) # input parameter target point of reference trajectory
                needle = lesion.newNeedle(True) # true, this is the reference needle around which the trajectory is planned
            else:
                # lesion was already added to the repo
                needle = lesion.findNeedle(tp) # retrieve the reference trajectory
            
            planned = needle.setPlannedTrajectory()
            planned.setTrajectory(ep,tp)
            needle.setValidationTrajectory() # empty because the reference needle has no validation trajectory
            needle.setTPEs() # init empty TPEs because there are no TPEs for the reference needle
            childrenTrajectories = xmlTrajectory.Children.Trajectory
            
            IV_parseNeedles(childrenTrajectories, lesion)
            
        elif not(xmlTrajectory['type'] and 'EG_ATOMIC' in xmlTrajectory['type']):
            # CAS older version 2.5
            # the distance between needles shouldn't be more than 2.2 according to a paper
            lesion = patient.findLesion(lesionlocation=tp, threshold=22.5)
           
            if lesion is None:
                lesion = patient.addNewLesion(tp) #
                needle = lesion.newNeedle(False) # reference trajectory must be calculate afterwards
                # TO DO:  old version of cas, there is no reference trajectory (could be computed as average trajectory)
                # TO DO: can't tell the number of lesions, must calculate based on the distance between average trajectory if it's the same lesion
            else:
                # retrieve the needle if already exists
                needle = lesion.findNeedle(tp)
                if needle is None:
                    needle = lesion.newNeedle(False)

            planned = needle.setPlannedTrajectory()
            planned.setTrajectory(ep, tp)
            needle.setValidationTrajectory() # empty because the reference needle has no validation trajectory
            needle.setTPEs() # init empty TPEs because there are no TPEs for the reference needle
            childrenTrajectories = xmlTrajectory
            
            IV_parseNeedles(childrenTrajectories, lesion)
            
        else:
            print('MWA Needle') # and continue to loop through the parent trajectories
            continue
        

def II_parseTrajectories(xmlobj):
    ''' INPUT: xmlobj tree structured parsed by function
        OUTPUT: Trajectories (if exist) extracted from XML File
    '''
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        if trajectories is not None:
            return trajectories
        else:
            print('No trajectory was found in the XML file')
            return None
    except Exception:
        print('No trajectory was found in the XML file')
        return None

#%%   
'''code to parse single file for verification purposes'''
#xmlfilename = 'tpesIRE.xml'
#xmlobj = I_parseRecordingXML(xmlfilename,'1')
# 
#patientId = 1
#patientsRepo = ie.PatientRepo()
#
#
#if xmlobj is not None:
#    # parse trajectories
#    trajectories = II_parseTrajectories(xmlobj)
#    # check if patient exists first, if yes, instantiate new object, otherwise retrieve it from list
#    patients = patientsRepo.getPatients()
#    patient = [x for x in patients if x.patientId == patientId]
#    if not patient:
#        # create patient measurements
#        patient = patientsRepo.addNewPatient(patientId)
#        III_parseTrajectory(trajectories, patient)
#    else:
#        # update patient measurements
#        III_parseTrajectory(trajectories, patient)
#        
#
##%%
#IRE_data = []
#patients = patientsRepo.getPatients()
#
#for p in patients:
#    lesions = p.getLesions()
#    patientID = p.patientId
#    for lIdx, l in enumerate(lesions):
#        ie.NeedleToDictWriter.needlesToDict(IRE_data, patientID, lIdx+1, l.getNeedles())
#
#        
#IRE_df = pd.DataFrame(IRE_data)