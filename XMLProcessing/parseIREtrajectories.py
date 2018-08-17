# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:04:29 2018

@author: Raluca Sandu
"""
import os
import re
import collections
import numpy as np
import untangle as ut

import xml.etree.ElementTree as ET
from extractTPEsXml import extractTPES
from elementExistsXml import elementExists
from splitAllPaths import splitall
# %%

def extract_patient_id(filename, patient_id_xml, patient_name_flag=True):
    """ Extract patient id & patient name from folder name.
    Assumes root folder name is of the type: Pat_John Smith_0013768450_2017-08-04_08-19-25
    The patient_id will be in this  case = 0013768450
    The patient_id is assumed to be an unique instance
    Note: Only for log files missing patient_id in the attributes
    :param filename: a norm path of the xml log file.
    :param patient_id_xml: string representing numerical id or None
    :param patient_name_flag: bool whether patient name should be written or not.
    :return: patient_id_xml (numerical patient id)
    """
    all_paths = splitall(filename)
    ix_patient_folder_name = [i for i, s in enumerate(all_paths) if "Pat_" in s]
    patient_folder_name = all_paths[ix_patient_folder_name[0]]
    patient_id = re.search("\d", patient_folder_name)  # numerical id
    ix_patient_id = int(patient_id.start())
    underscore = re.search("_", patient_folder_name[ix_patient_id:])
    if underscore is None:
        ix_underscore = len(patient_folder_name)-1
    else:
        ix_underscore = int(underscore.start())

    if patient_id_xml is None:
        patient_id_xml = patient_folder_name[ix_patient_id:ix_underscore + ix_patient_id]
    if patient_name_flag:
        patient_name = patient_folder_name[0:ix_patient_id]
    else:
        patient_name = None

    return patient_id_xml, patient_name


def I_parseRecordingXML(filename):
    # try to open and parse the xml filename if error, return message
    xml_tree = collections.namedtuple('xml_tree',
                                      ['trajectories', 'patient_id_xml', 'patient_name'])
    try:
        xmlobj = ut.parse(filename)
        patient_id_xml = xmlobj.Eagles.PatientData["patientID"]
        patient_id_xml, patient_name = extract_patient_id(filename, patient_id_xml, patient_name_flag=True)
        result = xml_tree(xmlobj, patient_id_xml, patient_name)
        return result
    except Exception:
        try:
            # attempt to remove weird characters by rewriting the files
            xmlobj = ET.parse(filename, parser=ET.XMLParser(encoding='ISO-8859-1'))
            root = xmlobj.getroot()
            root[0].attrib.pop('seriesPath', None)
            xmlobj.write(filename)
            return 1
        except Exception:
            print("This file could not be parse:", filename)
            return None


def parse_segmentation(singleTrajectory, needle, needle_type, ct_series, xml_filepath):
    """ Parse segmentation information.
    :param singleTrajectory: XML Tree Element.
    :param needle: Class Object Needle
    :param needle_type: MWA, IRE, RF, etc.
    :param ct_series: CT_Series number. Not unique.
    :param xml_filepath:  absolute filepath of the XML Log file currently parsed.
    :return: segmentation information
    """
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
        idx_cas_recordings = [i for i, s in enumerate(all_paths) if "CAS-One Recordings" in s]
        segmentation_datetime = all_paths[idx_cas_recordings[0] + 1]
        segmentation_filepath = os.path.join(*all_paths[0:len(all_paths)-1], singleTrajectory.Segmentation.Path.cdata[1:])

        # segmentation_filepath = os.path.join(all_paths[idx_segmentations[0]],
        #                                      all_paths[idx_segmentations[0] + 1],
        #                                      all_paths[idx_cas_recordings[0]],
        #                                      segmentation_datetime,
        #                                      singleTrajectory.Segmentation.Path.cdata[1:])
        idx_pat = [i for i, s in enumerate(all_paths) if "Pat" in s]
        source_filepath = os.path.join(all_paths[idx_pat[1]],
                                       all_paths[idx_pat[1] + 1],
                                       all_paths[idx_pat[1] + 2])
    # TODO: add the time at which segmentations were done in the folder name (new version).
    # check if folder empty. if true don't add the segmentation to the needles.
    if os.listdir(segmentation_filepath):
        #  check if the series UID has already been added.
        segmentation = needle.findSegmentation(series_UID, segmentation_type)
        if segmentation is None:
            # append to the list of segmentations based on time of the intervention
            segmentation = needle.newSegmentation(segmentation_datetime,
                                                  segmentation_type,
                                                  source_filepath,
                                                  segmentation_filepath,
                                                  needle_type,
                                                  ct_series,
                                                  series_UID,
                                                  sphere_radius)

            if elementExists(singleTrajectory, 'Ablator'):
                needle_params = segmentation.setNeedleSpecifications()
                needle_params.setNeedleSpecifications(singleTrajectory.Ablator["id"],
                                                      singleTrajectory.Ablator["ablationSystem"],
                                                      singleTrajectory.Ablator["ablationSystemVersion"],
                                                      singleTrajectory.Ablator["ablatorType"],
                                                      singleTrajectory.Ablator.Ablation["ablationShapeIndex"])
        else:
            # pass
            print("segmentation series already exists")
    else:
        print("Segmentation Folder Empty")




def IV_parseNeedles(children_trajectories, lesion, needle_type, ct_series, xml_filepath, time_intervention, cas_version):
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
            # TODO: modify the distance between the IRE needles accordingly
            needle = lesion.findNeedle(needlelocation=tp_planning, DISTANCE_BETWEEN_NEEDLES=3)
        elif needle_type is "MWA":
            needle = lesion.findNeedle(needlelocation=tp_planning, DISTANCE_BETWEEN_NEEDLES=3)
        # case for new needle not currently saved in database
        if needle is None:
            # add the needle to lesion class and init its parameters
            needle = lesion.newNeedle(False, needle_type, ct_series)  # False - the needle is not a reference trajectory
            tps = needle.setTPEs()
            validation = needle.setValidationTrajectory()
        # add the entry and target points to the needle object
        planned = needle.setPlannedTrajectory()
        planned.setTrajectory(ep_planning, tp_planning)
        planned.setLenghtNeedle()
        # add the TPEs if they exist in the Measurements field
        if elementExists(singleTrajectory, 'Measurements') is False:
            # print('No Measurement for this needle')
            pass
        else:
            # find the right needle to replace the exact TPEs
            # set the validation trajectory
            # set the time of intervention from XML
            ep_validation = np.array(
                [float(i) for i in singleTrajectory.Measurements.Measurement.EntryPoint.cdata.split()])
            tp_validation = np.array(
                [float(i) for i in singleTrajectory.Measurements.Measurement.TargetPoint.cdata.split()])
            validation = needle.setValidationTrajectory()
            validation.setTrajectory(ep_validation, tp_validation)

            entry_lateral, target_lateral, target_angular, target_longitudinal, target_euclidean \
                = extractTPES(singleTrajectory.Measurements.Measurement)

            tps = needle.setTPEs()
            needle.setTimeIntervention(time_intervention)
            needle.setCASversion(cas_version)
            # set TPE errors
            tps.setTPEErrors(entry_lateral, target_lateral, target_angular, target_longitudinal, target_euclidean)

        # add the segmentation path if it exists
        if elementExists(singleTrajectory, 'Segmentation'):
            parse_segmentation(singleTrajectory, needle, needle_type, ct_series, xml_filepath)


def III_parseTrajectory(trajectories, patient, ct_series, xml_filepath, time_intervention, cas_version):
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
                needle = lesion.newNeedle(True, needle_type, ct_series)
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
            IV_parseNeedles(children_trajectories, lesion, needle_type,
                            ct_series, xml_filepath, time_intervention, cas_version)
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
                            ct_series, xml_filepath, time_intervention, cas_version)


def II_parseTrajectories(xmlobj):
    """ Parse upper-level trajectories structure.
    :param:  xmlobj tree structured parsed by library such as untangle, XMLTree etc.
    :return: Trajectories (if they exist) extracted from XML File
    :return: CT SeriesNumber
    :return: time_intervention
    :return: cas_version
    """
    tuple_results = collections.namedtuple('tuples_results',
                                           ['trajectories',
                                            'series',
                                            'time_intervention',
                                            'cas_version'])
    try:
        trajectories = xmlobj.Eagles.Trajectories.Trajectory
        series = xmlobj.Eagles.PatientData["seriesNumber"]  # CT series number

        time_intervention = xmlobj.Eagles["time"]
        cas_version = xmlobj.Eagles["version"]
        if trajectories is not None:
            result = tuple_results(trajectories, series, time_intervention, cas_version)
            return result
        else:
            # TODO: better error message
            # print('No trajectory was found in the XML file')
            result = tuple_results(None, None, None, None)
            return result
    except Exception:
        # TODO: better error message
        # print('No trajectory was found in the XML file')
        result = tuple_results(None, None, None, None)
        return result
