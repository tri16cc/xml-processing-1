# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""
from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
import untangle as ut
#from datetime import datetime
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
    for singleTrajectory in childrenTrajectories:

        epP = np.array([float(i) for i in singleTrajectory.EntryPoint.cdata.split()])
        tpP = np.array([float(i) for i in singleTrajectory.TargetPoint.cdata.split()])
        needle = lesion.findNeedle(tpP)
        if needle is None:
            needle = lesion.newNeedle(False) # False - the needle is not a reference trajectory
            tps = needle.setTPEs()
        # add the entry and target points to the needle object
        needle.setPlannedTrajectory(ie.Trajectory(epP,tpP))
        
        if elementExists(singleTrajectory, 'Measurements') is False:
            print('No Measurement for this needle')  
        else:
            # find the right needle to replace the exact tpes
            # set the validation trajectory
            epV = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.EntryPoint.cdata.split()])
            tpV = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.TargetPoint.cdata.split()])
            needle.setValidationTrajectory(ie.Trajectory(epV,tpV))
            targetLateral,targetAngular,targetLongitudinal, targetEuclidean \
                = extractTPES(singleTrajectory.Measurements.Measurement.TPEErrors)
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
        if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:            
            
            ep = np.array([float(i) for i in xmlTrajectory.EntryPoint.cdata.split()])
            tp = np.array([float(i) for i in xmlTrajectory.TargetPoint.cdata.split()])
            # function to check if the lesion exists based on location returning true or false
            lesion = patient.findLesion(tp) 
            
            if lesion is None:
                lesion = patient.addNewLesion(tp) # input parameter target point of reference trajectory
                needle = lesion.newNeedle(True) # true, this is the refernce needle around which the trajectory is planned
            else:
                # retrieve the needle if already exists
                needle = lesion.findNeedle(tp)
            
            needle.setPlannedTrajectory(ie.Trajectory(ep,tp))
            childrenTrajectories = xmlTrajectory.Children.Trajectory
            
            IV_parseNeedles(childrenTrajectories, lesion)
            
        elif not(xmlTrajectory['type'] and 'EG_ATOMIC' in xmlTrajectory['type']):
            # TO DO: no reference trajectory defined - CAS old version
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
        return trajectories
    except Exception:
        print('No trajectory was found in the excel file')
        return None

##%%   
xmlfilename = 'multipleLesionsIRE.xml'
xmlobj = I_parseRecordingXML(xmlfilename,'1')
 
patientId = 1
patientsRepo = ie.PatientRepo()


if xmlobj is not None:
    # parse trajectories
    trajectories = II_parseTrajectories(xmlobj)
    # check if patient exists first, if yes, instantiate new object, otherwise retrieve it from list
    patients = patientsRepo.getPatients()
    patient = [x for x in patients if x.patientId == patientId]
    if not patient:
        # create patient measuerements
        patient = patientsRepo.addNewPatient(patientId)
        III_parseTrajectory(trajectories, patient)
    else:
        # update patient measurements
        III_parseTrajectory(trajectories, patient)

#%%
#patients_list = []
#patients_list.append(patient)
# a = [x for x in patients_list if x.patientId ==1]
# a[0].getLesions()
# call the 3rd function to parse the needles
