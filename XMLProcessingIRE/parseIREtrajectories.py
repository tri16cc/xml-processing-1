# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""
# from IPython import get_ipython
# get_ipython().magic('reset -sf')

import numpy as np
import untangle as ut
from extractTPEsXml import extractTPES
from elementExistsXml import elementExists


# %%

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

        needle = lesion.findNeedle(needlelocation=tpP, DISTANCE_BETWEEN_NEEDLES=2)

        # case for new needle not currently saved in database
        if needle is None:
            needle = lesion.newNeedle(False)  # False - the needle is not a reference trajectory
            tps = needle.setTPEs()
            validation = needle.setValidationTrajectory()

            # add the entry and target points to the needle object
        planned = needle.setPlannedTrajectory()
        planned.setTrajectory(epP, tpP)

        if elementExists(singleTrajectory, 'Measurements') is False:
            print('No Measurement for this needle')

        else:
            # find the right needle to replace the exact tpes
            # set the validation trajectory
            epV = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.EntryPoint.cdata.split()])
            tpV = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.TargetPoint.cdata.split()])
            validation = needle.setValidationTrajectory()
            validation.setTrajectory(epV, tpV)
            #            print(epV, tpV)

            targetLateral, targetAngular, targetLongitudinal, targetEuclidean \
                = extractTPES(singleTrajectory.Measurements.Measurement)
            print("target lateral error after function extraction:", targetLateral)

            tps = needle.setTPEs()
            tps.setTPEErrors(targetLateral, targetAngular, targetLongitudinal, targetEuclidean)


def III_parseTrajectory(trajectories, patient):
    ''' Parse Trajectories at lesion level. For each lesion, a new Parent Trajectory is defined
        INPUT: list of Parent Trajectories
        OUTPUT: list of Needle Trajectories
    '''
    for xmlTrajectory in trajectories:
        # check whether it's IRE trajectory
        ep = np.array([float(i) for i in xmlTrajectory.EntryPoint.cdata.split()])
        tp = np.array([float(i) for i in xmlTrajectory.TargetPoint.cdata.split()])

        if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:
            print('CAS Version 2.9')
            # function to check if the lesion exists based on location returning true or false
            lesion = patient.findLesion(lesionlocation=tp, DISTANCE_BETWEEN_LESIONS=2)

            if lesion is None:
                lesion = patient.addNewLesion(tp)  # input parameter target point of reference trajectory
                needle = lesion.newNeedle(
                    True)  # true, this is the reference needle around which the trajectory is planned
            else:
                # lesion was already added to the repo
                needle = lesion.findNeedle(tp, DISTANCE_BETWEEN_NEEDLES=2)  # retrieve the reference trajectory

            planned = needle.setPlannedTrajectory()
            planned.setTrajectory(ep, tp)
            needle.setValidationTrajectory()  # empty because the reference needle has no validation trajectory
            needle.setTPEs()  # init empty TPEs because there are no TPEs for the reference needle
            childrenTrajectories = xmlTrajectory.Children.Trajectory
            IV_parseNeedles(childrenTrajectories, lesion)

        elif not (xmlTrajectory['type'] and 'EG_ATOMIC' in xmlTrajectory['type']):
            #            continue
            # the case when CAS XML Log is older version 2.5
            # the distance between needles shouldn't be more than 22 mm according to a paper
            # DISTANCE_BETWEEN_LESIONS [mm]
            lesion = patient.findLesion(lesionlocation=tp, DISTANCE_BETWEEN_LESIONS=23)

            if lesion is None:
                lesion = patient.addNewLesion(tp)  #

            childrenTrajectories = xmlTrajectory
            IV_parseNeedles(childrenTrajectories, lesion)

        else:
            print('MWA Needle')  # and continue to loop through the parent trajectories
            continue


def II_parseTrajectories(xmlobj):
    ''' INPUT: xmlobj tree structured parsed by function
        OUTPUT: Trajectories (if exist) extracted from XML File
    '''
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        # TO DO: add version
        #        version = xmlobj.Eagles['version']
        if trajectories is not None:
            return trajectories
        else:
            print('No trajectory was found in the XML file')
            return None
    except Exception:
        print('No trajectory was found in the XML file')
        return None

# %%
