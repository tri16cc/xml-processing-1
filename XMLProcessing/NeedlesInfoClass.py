# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:20:31 2018

@author: Raluca Sandu
"""
import numpy as np
from collections import defaultdict

class PatientRepo:

    def __init__(self):
        self.patients = []

    def addNewPatient(self, patient_id_xml, patient_name):
        patient = Patient(patient_id_xml, patient_name)
        self.patients.append(patient)
        return patient

    def getPatients(self):
        return self.patients


class Patient:

    def __init__(self, patient_id_xml, patient_name):
        self.lesions = []
        self.patient_id_xml = patient_id_xml
        self.patient_name = patient_name

    def addLesion(self, lesion):
        self.lesions.append(lesion)

    def addNewLesion(self, location):
        lesion = Lesion(location)
        self.addLesion(lesion)
        return lesion

    def getLesions(self):
        return self.lesions

    def findLesion(self, lesionlocation, DISTANCE_BETWEEN_LESIONS):
        foundLesions = list(filter(lambda l:
                                   l.distanceTo(lesionlocation) < DISTANCE_BETWEEN_LESIONS, self.lesions))
        if len(foundLesions) == 0:
            return None
        elif len(foundLesions) > 0:
            return foundLesions[0]
        else:
            raise Exception('Something went wrong')


class Lesion:
    # location is a numpy array
    def __init__(self, location):
        self.needles = []
        if location is not None and len(location) is 3:
            self.location = location
        else:
            raise Exception('Lesion Location not given')

    def distanceTo(self, lesionlocation):
        # compute euclidean distances for TPE to check whether the same lesion
        tp1 = lesionlocation
        tp2 = self.location
        dist = np.linalg.norm(tp1 - tp2)
        return dist
        pass

    def getNeedles(self):
        return self.needles

    def newNeedle(self, isreference, needle_type, ct_series):
        # here self represents the lesion
        needle = Needle(self, isreference, needle_type, ct_series)
        self.needles.append(needle)
        return needle

    def findNeedle(self, needlelocation, DISTANCE_BETWEEN_NEEDLES):
        """ Find and return the needles. Based on euclidean distance.
            Might not work because there is no clear and constant agreement
            to tell if it's a new needle or the same one which was moved with 50mm.
        """
        foundNeedles = list(filter(lambda l:
                                   l.distanceToNeedle(needlelocation) < DISTANCE_BETWEEN_NEEDLES, self.needles))
        if len(foundNeedles) == 0:
            return None
        elif len(foundNeedles) > 0:
            return foundNeedles[0]
        else:
            raise Exception('Something went wrong')


class Segmentation:

    def __init__(self, needle, source_path, path, needle_type, ct_series, series_UID, sphere_radius, segmentation_type, segmentation_datetime):
        self.source_path = source_path
        self.mask_path = path
        self.needle_type = needle_type
        self.ct_series = ct_series
        self.series_UID = series_UID
        self.sphere_radius = sphere_radius
        self.needle = needle
        self.segmentation_type = segmentation_type  # ablation, tumor, vessel (etc)
        self.segmentation_datetime = segmentation_datetime
        self.needle_specifications = None
        self.ellipsoid_info = None # TODO: is this instantiated?

    def setNeedleSpecifications(self):
        self.needle_specifications = NeedleSpecifications()
        return self.needle_specifications


class NeedleSpecifications:

    def __init__(self):
        self.ablator_id = None
        self.ablationSystem = None
        self.ablationSystemVersion = None
        self.ablatorType = None
        self.ablationShapeIndex = None  # id field which connects with the MWA Needle Database

    def setNeedleSpecifications(self, ablator_id, ablationSystem,
                                ablationSystemVersion, ablatorType,
                                ablationShapeIndex):
        self.ablator_id = ablator_id
        self.ablationSystem = ablationSystem
        self.ablationSystemVersion = ablationSystemVersion
        self.ablatorType = ablatorType
        self.ablationShapeIndex = ablationShapeIndex  # id field which connects with the MWA Needle Database


class Needle:

    def __init__(self, lesion, isreference, needle_type, ct_series):
        self.segmentations_tumor = []
        self.segmentations_ablation = []
        self.isreference = isreference
        self.planned = None
        self.validation = None
        self.tpeerorrs = None
        self.time_intervention = None
        self.cas_version = None
        self.lesion = lesion
        self.needle_type = needle_type
        self.ct_series = ct_series

    def distanceToNeedle(self, needlelocation):
        # compute euclidean distances for TPE to check whether the same lesion
        tp1 = needlelocation
        tp2 = self.planned.targetpoint
        dist = np.linalg.norm(tp1 - tp2)
        return dist
        pass

    def setCASversion(self, cas_version):
        self.cas_version = cas_version

    def setTimeIntervention(self, time_intervention):
        self.time_intervention = time_intervention

    def setPlannedTrajectory(self):
        self.planned = Trajectory()
        return self.planned

    def setValidationTrajectory(self):
        self.validation = Trajectory()
        return self.validation

    def setTPEs(self):
        self.tpeerorrs = TPEErrors()
        return self.tpeerorrs

    def getTPEs(self):
        return self.tpeerorrs

    def getPlannedTrajectory(self):
        return self.planned

    def getValidationTrajectory(self):
        return self.validation

    def getIsNeedleReference(self):
        return self.isreference

    def findSegmentation(self, series_UID, segmentation_type):
        """ Retrieve Segmentation based on unique SeriesUID (metatag).
            To use in case the segmentation info appears multiple locations in
            the folder. In case information needs to be updated with latest path.
        """
        if segmentation_type.lower() in {"lesion", "lession", "tumor", "tumour"}:
            segmentations = self.segmentations_tumor
        elif segmentation_type.lower() in {"ablation", "ablationzone", "necrosis"}:
            segmentations = self.segmentations_ablation
        seg_found = list(filter(lambda l: l.series_UID == series_UID, segmentations))
        if len(seg_found) > 0:
            return seg_found[0]
        else:
            print("Series UID not in list")
            return None

    def newSegmentation(self, segmentation_datetime, segmentation_type, source_path, mask_path, needle_type,
                        ct_series, series_UID,
                        sphere_radius):
        """ Instantiate Segmentation Class object.
            append segmentation object to the correct needle object list.
            to solve: multiple type of segmentations (eg.vessel) might appear in the future
        """
        if segmentation_type.lower() in {"lesion", "lession", "tumor", "tumour"}:
            segmentation = Segmentation(self, source_path, mask_path, needle_type, ct_series, series_UID, sphere_radius,
                                        segmentation_type,segmentation_datetime)
            self.segmentations_tumor.append(segmentation)
            return segmentation
        elif segmentation_type.lower() in {"ablation", "ablationzone", "necrosis"}:
            segmentation = Segmentation(self, source_path, mask_path, needle_type, ct_series, series_UID, sphere_radius,
                                        segmentation_type,segmentation_datetime)
            self.segmentations_ablation.append(segmentation)
            return segmentation

    def getAblationSegmentations(self):
        return self.segmentations_ablation

    def getTumorSegmentations(self):
        return self.segmentations_tumor

    def to_dict(self, patientID, patient_name, lesionIdx, needle_idx):
        """ Unpack Needle Object class to dict.
            Return needle information.
            If one needle has several segmentations, iterate and return all.
            If no segmentation, return empty fields for the segmentation.
        """
        segmentations_tumor = self.segmentations_tumor
        segmentations_ablation = self.segmentations_ablation
        # TODO: the number of tumor and ablation segmentations is not always the same.
        dict_one_needle = defaultdict(list)
        max_no_segmentations = max(len(segmentations_ablation), len(segmentations_tumor))
        if max_no_segmentations > 0:
            for idx_s in range(0, max_no_segmentations):
                    # dict_one_needle['PatientID'] = [patientID]
                    # dict_one_needle['PatientName'] = [ patient_name]
                dict_one_needle['PatientID'].append(patientID)
                dict_one_needle['PatientName'].append(patient_name)
                dict_one_needle['LesionNr'].append(lesionIdx)
                dict_one_needle['NeedleNr'].append(needle_idx)
                dict_one_needle['CAS_Version'].append(self.cas_version)
                dict_one_needle['TimeIntervention'].append(self.time_intervention)
                dict_one_needle['PlannedEntryPoint'].append(self.planned.entrypoint)
                dict_one_needle['PlannedTargetPoint'].append(self.planned.targetpoint)
                dict_one_needle['PlannedNeedleLength'].append(self.planned.length_needle)
                dict_one_needle['ValidationEntryPoint'].append(self.validation.entrypoint)
                dict_one_needle['ValidationTargetPoint'].append(self.validation.targetpoint)
                dict_one_needle['ReferenceNeedle'].append(self.isreference)
                dict_one_needle['EntryLateral'].append(self.tpeerorrs.entry_lateral)
                dict_one_needle['AngularError'].append(self.tpeerorrs.angular)
                dict_one_needle['LateralError'].append(self.tpeerorrs.lateral)
                dict_one_needle['LongitudinalError'].append(self.tpeerorrs.longitudinal)
                dict_one_needle['EuclideanError'].append(self.tpeerorrs.euclidean)
                try:
                    # try catch block if there is no tumor segmentation at the respective index
                    dict_one_needle['NeedleType'].append(segmentations_tumor[idx_s].needle_type)
                    dict_one_needle['TumorPath'].append(segmentations_tumor[idx_s].mask_path)
                    dict_one_needle['PlanTumorPath'].append(segmentations_tumor[idx_s].source_path)
                    dict_one_needle['Tumor_CT_Series'].append(segmentations_tumor[idx_s].ct_series)
                    dict_one_needle['Tumor_Series_UID'].append(segmentations_tumor[idx_s].series_UID)
                    dict_one_needle["Tumor_Segmentation_Datetime"].append(segmentations_tumor[idx_s].segmentation_datetime)
                except Exception:
                    dict_one_needle['NeedleType'].append(None)
                    dict_one_needle['TumorPath'].append(None)
                    dict_one_needle['PlanTumorPath'].append(None)
                    dict_one_needle['Tumor_CT_Series'].append(None)
                    dict_one_needle['Tumor_Series_UID'].append(None)
                    dict_one_needle["Tumor_Segmentation_Datetime"].append(None)
                try:
                    # try catch block if there is no ablation segmentation at the respective index
                    dict_one_needle['AblationPath'].append(segmentations_ablation[idx_s].mask_path)
                    dict_one_needle['ValidationAblationPath'].append(segmentations_ablation[idx_s].source_path)
                    dict_one_needle['Ablation_CT_Series'].append(segmentations_ablation[idx_s].ct_series)
                    dict_one_needle['Ablation_Series_UID'].append(segmentations_ablation[idx_s].series_UID)
                    dict_one_needle['AblationSystem'].append(segmentations_tumor[idx_s].needle_specifications.ablationSystem)
                    dict_one_needle['AblatorID'].append(segmentations_ablation[idx_s].needle_specifications.ablator_id)
                    dict_one_needle['AblationSystemVersion'].append(segmentations_ablation[idx_s].needle_specifications.ablationSystemVersion)
                    dict_one_needle['AblationShapeIndex'].append(segmentations_ablation[idx_s].needle_specifications.ablationShapeIndex)
                    dict_one_needle['AblatorType'].append(segmentations_ablation[idx_s].needle_specifications.ablatorType)
                    dict_one_needle["Ablation_Segmentation_Datetime"].append(segmentations_ablation[idx_s].segmentation_datetime)
                except Exception:
                    dict_one_needle['AblationPath'].append(None)
                    dict_one_needle['ValidationAblationPath'].append(None)
                    dict_one_needle['Ablation_CT_Series'].append(None)
                    dict_one_needle['Ablation_Series_UID'].append(None)
                    dict_one_needle['AblationSystem'].append(None)
                    dict_one_needle['AblatorID'].append(None)
                    dict_one_needle['AblationSystemVersion'].append(None)
                    dict_one_needle['AblationShapeIndex'].append(None)
                    dict_one_needle['AblatorType'].append(None)
                    dict_one_needle['Ablation_Segmentation_Datetime'].append(None)

            return dict_one_needle
        else:
            # no segmentations have been found for this needle
            dict_one_needle['PatientID'] = [patientID]
            dict_one_needle['PatientName']= [patient_name]
            dict_one_needle['LesionNr'] = [lesionIdx]
            dict_one_needle['NeedleNr'] = [needle_idx]
            dict_one_needle['CAS_Version'] = [self.cas_version]
            dict_one_needle['TimeIntervention'] = [self.time_intervention]
            dict_one_needle['PlannedEntryPoint'] = [self.planned.entrypoint]
            dict_one_needle['PlannedTargetPoint'] = [self.planned.targetpoint]
            dict_one_needle['PlannedNeedleLength'] = [self.planned.length_needle]
            dict_one_needle['ValidationEntryPoint'] = [self.validation.entrypoint]
            dict_one_needle['ValidationTargetPoint'] = [self.validation.targetpoint]
            dict_one_needle['ReferenceNeedle'] = [self.isreference]
            dict_one_needle['EntryLateral'] = [self.tpeerorrs.entry_lateral]
            dict_one_needle['AngularError'] = [self.tpeerorrs.angular]
            dict_one_needle['LateralError'] = [self.tpeerorrs.lateral]
            dict_one_needle['LongitudinalError'] = [self.tpeerorrs.longitudinal]
            dict_one_needle['EuclideanError'] = [self.tpeerorrs.euclidean]
            dict_one_needle['NeedleType'] = None
            dict_one_needle['TumorPath'] = None
            dict_one_needle['PlanTumorPath'] = None
            dict_one_needle['Tumor_CT_Series'] = None
            dict_one_needle['Tumor_Series_UID'] = None
            dict_one_needle['Tumor_Segmentation_Datetime'] = None
            dict_one_needle['AblationPath'] = None
            dict_one_needle['ValidationAblationPath'] = None
            dict_one_needle['Ablation_CT_Series'] = None
            dict_one_needle['Ablation_Series_UID'] = None
            dict_one_needle['AblationSystem'] = None
            dict_one_needle['AblatorID'] = None
            dict_one_needle['AblationSystemVersion'] = None
            dict_one_needle['AblationShapeIndex'] = None
            dict_one_needle['AblatorType'] = None
            return dict_one_needle


class NeedleToDictWriter:
    """ Extracts the needle information into dictionary format.
    Attributes:
        needle_data: an empty list to append to.
        patientID : str specifying patient id
        lesionIDX: int specifying the needle count
        needles: needles class object
    """

    def needlesToDict(needle_data, patientID, patient_name, lesionIdx, needles):
        if len(needles)>0:
            for needle_idx, needle in enumerate(needles):
                needle_dict = needle.to_dict(patientID, patient_name, lesionIdx, needle_idx)  # needle_dict is a list type
                # TODO: unpack before appending if multiple segmentations are available for a needle
                # TODO: iterate through each value of the dictionary - but how??
                needle_data.append(needle_dict)
        else:
            print(patientID)


class TPEErrors:

    def __init__(self):
        self.entry_lateral = None
        self.angular = None
        self.longitudinal = None
        self.lateral = None
        self.euclidean = None

    def setTPEErrors(self, entry_lateral, lateral, angular, longitudinal, euclidean):
        self.entry_lateral = entry_lateral
        self.angular = angular
        self.longitudinal = longitudinal
        self.lateral = lateral
        self.euclidean = euclidean

    def calculateTPEErrors(self, plannedTrajectory, validationTrajectory, offset):
        # TO DO: in case of offset that wasn't accounted for in the old versions of cascination
        pass


class Trajectory:

    def __init__(self):
        self.entrypoint = None
        self.targetpoint = None
        self.length_needle = None

    def setTrajectory(self, entrypoint, targetpoint):
        self.entrypoint = entrypoint
        self.targetpoint = targetpoint

    def setLenghtNeedle(self):
        self.length_needle = np.linalg.norm(self.targetpoint - self.entrypoint)
