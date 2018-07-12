# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""
# from IPython import get_ipython
# get_ipython().magic('reset -sf')
import os
import collections
import numpy as np
import untangle as ut
from extractTPEsXml import extractTPES
from elementExistsXml import elementExists
from splitAllPaths import splitall
# %%

def I_parseRecordingXML(filename):
    # try to open and parse the xml filename if error, return message
    xml_tree = collections.namedtuple('xml_tree',
                                      ['trajectories', 'patient_id_xml'])
    try:
        xmlobj = ut.parse(filename)
        patient_id_xml = xmlobj.Eagles.PatientData["patientID"]
        result = xml_tree(xmlobj, patient_id_xml)
        return result
    except Exception:
        print('XML file structure is broken, cannot read XML')
        return None


def parse_segmentation(singleTrajectory, needle, needle_type, ct_series, xml_filepath):
    segmentation_type = singleTrajectory.Segmentation["StructureType"]
    if singleTrajectory.Segmentation["TypeOfSegmentation"].lower() in {"sphere"}:
        series_UID = singleTrajectory.Segmentation["SphereRadius"]  # add the radius for search purposes
        sphere_radius = singleTrajectory.Segmentation["SphereRadius"]
        segmentation_filepath = ''
    else:
        series_UID = singleTrajectory.Segmentation.SeriesUID.cdata
        sphere_radius = ''
        all_paths = splitall(xml_filepath)
        idx_segmentations = [i for i, s in enumerate(all_paths) if "Study" in s]
        segmentation_filepath = os.path.join(all_paths[idx_segmentations[0]],
                                             all_paths[idx_segmentations[0] + 1],
                                             singleTrajectory.Segmentation.Path.cdata[1:])
        idx_pat = [i for i, s in enumerate(all_paths) if "Pat" in s]
        source_filepath = os.path.join(all_paths[idx_pat[1]],
                                       all_paths[idx_pat[1] + 1],
                                       all_paths[idx_pat[1] + 2])
    # TODO: add the time at which segmentations were done in the folder name (new version). 
    #  check if the series UID has already been added.]
    segmentation = needle.findSegmentation(series_UID, segmentation_type)
    if segmentation is None:
        # add it to the needle list, otherwise update it.
        segmentation = needle.newSegmentation(segmentation_type,
                                              source_filepath,
                                              segmentation_filepath,
                                              needle_type,
                                              ct_series,
                                              series_UID,
                                              sphere_radius)
    else:
        print("segmentation series already exists")

    if elementExists(singleTrajectory, 'Ablator'):
        needle_params = segmentation.setNeedleSpecifications()
        # TODO: add singleTrajectory.Ablator["readableName"],
        needle_params.setNeedleSpecifications(singleTrajectory.Ablator["id"],
                                              singleTrajectory.Ablator["ablationSystem"],
                                              singleTrajectory.Ablator["ablationSystemVersion"],
                                              singleTrajectory.Ablator["ablatorType"],
                                              singleTrajectory.Ablator.Ablation["ablationShapeIndex"])


def IV_parseNeedles(children_trajectories, lesion, needle_type, ct_series, xml_filepath, time_intervention):
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
            # TODO: modify the distance between the needles accordingly
            needle = lesion.findNeedle(needlelocation=tp_planning, DISTANCE_BETWEEN_NEEDLES=3)
        elif needle_type is "MWA":
            needle = lesion.findNeedle(needlelocation=tp_planning, DISTANCE_BETWEEN_NEEDLES=3)
        # case for new needle not currently saved in database
        if needle is None:
            # add the needle to lesion class and init its parameters
            needle = lesion.newNeedle(False, needle_type, ct_series,time_intervention)  # False - the needle is not a reference trajectory
            tps = needle.setTPEs()
            validation = needle.setValidationTrajectory()
        # add the entry and target points to the needle object
        planned = needle.setPlannedTrajectory()
        planned.setTrajectory(ep_planning, tp_planning)
        # add the TPEs if they exist in the Measurements field
        if elementExists(singleTrajectory, 'Measurements') is False:
            print('No Measurement for this needle')
        else:
            # find the right needle to replace the exact TPEs
            # set the validation trajectory
            ep_validation = np.array(
                [float(i) for i in singleTrajectory.Measurements.Measurement.EntryPoint.cdata.split()])
            tp_validation = np.array(
                [float(i) for i in singleTrajectory.Measurements.Measurement.TargetPoint.cdata.split()])
            validation = needle.setValidationTrajectory()
            validation.setTrajectory(ep_validation, tp_validation)
            target_lateral, target_angular, target_longitudinal, target_euclidean \
                = extractTPES(singleTrajectory.Measurements.Measurement)
            tps = needle.setTPEs()
            tps.setTPEErrors(target_lateral, target_angular, target_longitudinal, target_euclidean)
        # add the segmentation path if it exists
        if elementExists(singleTrajectory, 'Segmentation'):
            parse_segmentation(singleTrajectory, needle, needle_type, ct_series, xml_filepath)


def III_parseTrajectory(trajectories, patient, ct_series, xml_filepath, time_intervention):
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
                needle = lesion.newNeedle(True, needle_type, ct_series, time_intervention)
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
            # drop the lesion identification for MWA. multiple needles might be 
            # no clear consensus for minimal distance between lesions
            lesion = patient.findLesion(lesionlocation=tp_planning, DISTANCE_BETWEEN_LESIONS=100)
            if lesion is None:
                lesion = patient.addNewLesion(tp_planning)
            children_trajectories = xmlTrajectory
            IV_parseNeedles(children_trajectories, lesion, needle_type,
                            ct_series, xml_filepath, time_intervention)


def II_parseTrajectories(xmlobj):
    """ Parse upper-level trajectories structure.
    INPUT: xmlobj tree structured parsed by function
    OUTPUT: Trajectories (if exist) extracted from XML File
    """
    tuple_results = collections.namedtuple('tuples_results',
                                           ['trajectories', 'series',
                                            'time_intervention', 'patient_id_xml'])
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        series = xmlobj.Eagles.PatientData["seriesNumber"]  # CT series number
        patient_id_xml = xmlobj.Eagles.PatientData["patientID"]
        time_intervention = xmlobj.Eagles["time"]
        # TODO: add version : xmlobj.Eagles['version']
        if trajectories is not None:
            result = tuple_results(trajectories, series, time_intervention,
                                   patient_id_xml)
            return result
        else:
            print('No trajectory was found in the XML file')
            result = tuple_results(None, None, None, None)
            return result
    except Exception:
        print('No trajectory was found in the XML file')
        result = tuple_results(None, None, None, None)
        return result
