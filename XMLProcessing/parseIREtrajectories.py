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


def I_parseRecordingXML(filename):
    # try to open and parse the xml filename if error, return message
    try:
        xmlobj = ut.parse(filename)
        return xmlobj
    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None


def IV_parseNeedles(children_trajectories, lesion, needle_type):
    """ Parse Individual Needle Trajectories per Lesion.
    Extract planning coordinates and  validation needle coordinate.
    Extract the TPE Errors from the validation coordinates.
    To find the needles assume the distance between the same needle could be up to 35[mm].DISTANCE_BETWEEN_NEEDLES=35
    INPUT:
    1. xml tree structure for child trajectories
    2. lesion class object
    3. needle_type (string) MWA or IRE
    OUTPUT: doesn't return anything, just sets the TPEs
    """
    for singleTrajectory in children_trajectories:

        ep_planning = np.array([float(i) for i in singleTrajectory.EntryPoint.cdata.split()])
        tp_planning = np.array([float(i) for i in singleTrajectory.TargetPoint.cdata.split()])
        # find if the needle exists already in the patient repository
        # for IRE needles the distance shouldn't be larger than 3 (in theory)
        if needle_type is "IRE":
            needle = lesion.findNeedle(needlelocation=tp_planning, DISTANCE_BETWEEN_NEEDLES=3)
        elif needle_type  is "MWA":
            needle = lesion.findNeedle(needlelocation=tp_planning, DISTANCE_BETWEEN_NEEDLES=30)
        # case for new needle not currently saved in database
        if needle is None:
            needle = lesion.newNeedle(False, needle_type)  # False - the needle is not a reference trajectory
            tps = needle.setTPEs()
            validation = needle.setValidationTrajectory()

            # add the entry and target points to the needle object
        planned = needle.setPlannedTrajectory()
        planned.setTrajectory(ep_planning, tp_planning)

        if elementExists(singleTrajectory, 'Measurements') is False:
            print('No Measurement for this needle')
        else:
            # find the right needle to replace the exact TPEs
            # set the validation trajectory
            ep_validation = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.EntryPoint.cdata.split()])
            tp_validation = np.array([float(i) for i in singleTrajectory.Measurements.Measurement.TargetPoint.cdata.split()])
            validation = needle.setValidationTrajectory()
            validation.setTrajectory(ep_validation, tp_validation)
            target_lateral, target_angular, target_longitudinal, target_euclidean \
                = extractTPES(singleTrajectory.Measurements.Measurement)
            tps = needle.setTPEs()
            tps.setTPEErrors(target_lateral, target_angular, target_longitudinal, target_euclidean)



def III_parseTrajectory(trajectories, patient):
    """ Parse Trajectories at lesion level.
    For each lesion, a new Parent Trajectory is defined.
    A lesion is defined when the distance between needles is minimum 35 mm.
    A patient can have both MWA and IREs
    INPUT:
    - trajectories which is object with Parent Trajectories
    - patient id
    OUTPUT: list of Needle Trajectories passed to Needle Trajectories function
    """
    for xmlTrajectory in trajectories:
        # check whether it's IRE trajectory
        ep_planning = np.array([float(i) for i in xmlTrajectory.EntryPoint.cdata.split()])
        tp_planning = np.array([float(i) for i in xmlTrajectory.TargetPoint.cdata.split()])

        if (xmlTrajectory['type']) and 'IRE' in xmlTrajectory['type']:
            needle_type = 'IRE'
            # function to check if the lesion exists based on location returning true or false
            lesion = patient.findLesion(lesionlocation=tp_planning, DISTANCE_BETWEEN_LESIONS=23)
            if lesion is None:
                lesion = patient.addNewLesion(tp_planning)  # input parameter target point of reference trajectory
                needle = lesion.newNeedle(True, needle_type)
                # true, this is the reference needle around which the trajectory is planned
            else:
                # lesion was already added to the repository
                needle = lesion.findNeedle(tp_planning, DISTANCE_BETWEEN_NEEDLES=3)  # retrieve the reference trajectory

            planned = needle.setPlannedTrajectory()
            planned.setTrajectory(ep_planning, tp_planning)
            needle.setValidationTrajectory()  # empty because the reference needle has no validation trajectory
            needle.setTPEs()  # init empty TPEs because there are no TPEs for the reference needle
            children_trajectories = xmlTrajectory.Children.Trajectory
            IV_parseNeedles(children_trajectories, lesion, needle_type)

        elif not (xmlTrajectory['type'] and 'EG_ATOMIC' in xmlTrajectory['type']):
            # the case when CAS XML Log is older version 2.5
            # the distance between needles shouldn't be more than 22 mm according to a paper
            # DISTANCE_BETWEEN_LESIONS [mm]
            lesion = patient.findLesion(lesionlocation=tp_planning, DISTANCE_BETWEEN_LESIONS=23)
            if lesion is None:
                lesion = patient.addNewLesion(tp_planning)
            children_trajectories = xmlTrajectory
            IV_parseNeedles(children_trajectories, lesion, needle_type)
        else:
           # MWA type of needle
            needle_type = "MWA"
            lesion = patient.findLesion(lesionlocation=tp_planning, DISTANCE_BETWEEN_LESIONS=35)
            if lesion is None:
                lesion = patient.addNewLesion(tp_planning)
            children_trajectories = xmlTrajectory
            IV_parseNeedles(children_trajectories, lesion, needle_type)


def II_parseTrajectories(xmlobj):
    """ Parse upper-level trajectories structure.
    INPUT: xmlobj tree structured parsed by function
    OUTPUT: Trajectories (if exist) extracted from XML File
    """
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

