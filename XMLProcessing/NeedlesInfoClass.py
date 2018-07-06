# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:20:31 2018

@author: Raluca Sandu
"""
import numpy as np


class PatientRepo:

    def __init__(self):
        self.patients = []

    def addNewPatient(self, patientId, patient_id_xml, time_intervention):
        patient = Patient(patientId, patient_id_xml, time_intervention)
        self.patients.append(patient)
        return patient

    def getPatients(self):
        return self.patients


class Patient:

    def __init__(self, patientId, patient_id_xml, time_intervention):
        self.lesions = []
        self.patientId = patientId
        self.patient_id_xml = patient_id_xml
        self.time_intervention = time_intervention

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
        needle = Needle(self, isreference, needle_type, ct_series)  # here self represents the lesion
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
    
    def __init__(self, needle, path, needle_type, ct_series, series_UID, sphere_radius, segmentation_type):
        self.mask_path = path
        self.needle_type = needle_type
        self.ct_series = ct_series
        self.series_UID = series_UID
        self.sphere_radius = sphere_radius
        self.needle = needle
        self.segmentation_type = segmentation_type  # ablation, tumor, vessel (etc)
        self.needle_specifications = None
        # TODO: add self.datetime_created = datetime_created
        
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

    def newSegmentation(self, segmentation_type, path, needle_type, ct_series, series_UID, sphere_radius):
        """ Instantiate Segmentation Class object.
            append segmentation object to the correct needle object list.
            to solve: multiple type of segmentations (eg.vessel) might appear in the future
        """
        if segmentation_type.lower() in {"lesion", "lession", "tumor", "tumour"}:
            segmentation = Segmentation(self, path, needle_type, ct_series, series_UID, sphere_radius,
                                        segmentation_type)
            self.segmentations_tumor.append(segmentation)
            return segmentation
        elif segmentation_type.lower() in {"ablation", "ablationzone", "necrosis"}:
            segmentation = Segmentation(self, path, needle_type, ct_series, series_UID, sphere_radius,
                                        segmentation_type)
            self.segmentations_ablation.append(segmentation)
            return segmentation

    def getAblationSegmentations(self):
        return self.segmentations_ablation

    def getTumorSegmentations(self):
        return self.segmentations_tumor

    def to_dict(self, patientID, lesionIdx, needle_idx):
        """ Unpack Needle Object class to dict.
            Return needle inforation.
            If one needle has several segmentations, iterate and return all.
            If no segmentation, return empty fields for the segmentation.
        """
        segmentation_tumor = self.segmentations_tumor
        segmentation_ablation = self.segmentations_ablation
        dict_one_needle = []
        # if this needle has segmentation associated with it then output its info
        if segmentation_tumor:
            for idx_s, seg in enumerate(segmentation_tumor):
                one_seg = {'PatientID': patientID,
                           'LesionNr': lesionIdx,
                           'NeedleNr': needle_idx,
                           'PlannedEntryPoint': self.planned.entrypoint,
                           'PlannedTargetPoint': self.planned.targetpoint,
                           'ValidationEntryPoint': self.validation.entrypoint,
                           'ValidationTargetPoint': self.validation.targetpoint,
                           'ReferenceNeedle': self.isreference,
                           'AngularError': self.tpeerorrs.angular,
                           'LateralError': self.tpeerorrs.lateral,
                           'LongitudinalError': self.tpeerorrs.longitudinal,
                           'EuclideanError': self.tpeerorrs.euclidean,
                           'NeedleType': segmentation_tumor[idx_s].needle_type,
                           'TumorPath': segmentation_tumor[idx_s].mask_path,
                           'Tumor_CT_Series': segmentation_tumor[idx_s].ct_series,
                           'Tumor_Series_UID': segmentation_tumor[idx_s].series_UID,
                           'AblationPath': segmentation_ablation[idx_s].mask_path,
                           'Ablation_CT_Series': segmentation_ablation[idx_s].ct_series,
                           'Ablation_Series_UID': segmentation_ablation[idx_s].series_UID
                           }
                dict_one_needle.append(one_seg)
            return dict_one_needle
        else:
            # output just the needle and empty segmentation info
            one_seg = {'PatientID': patientID,
                       'LesionNr': lesionIdx,
                       'NeedleNr': needle_idx,
                       'PlannedEntryPoint': self.planned.entrypoint,
                       'PlannedTargetPoint': self.planned.targetpoint,
                       'ValidationEntryPoint': self.validation.entrypoint,
                       'ValidationTargetPoint': self.validation.targetpoint,
                       'ReferenceNeedle': self.isreference,
                       'AngularError': self.tpeerorrs.angular,
                       'LateralError': self.tpeerorrs.lateral,
                       'LongitudinalError': self.tpeerorrs.longitudinal,
                       'EuclideanError': self.tpeerorrs.euclidean,
                       'NeedleType': self.needle_type,
                       'TumorPath': '',
                       'Tumor_CT_Series': '',
                       'Tumor_Series_UID': '',
                       'AblationPath': '',
                       'Ablation_CT_Series': '',
                       'Ablation_Series_UID': ''
                       }
            dict_one_needle.append(one_seg)
            return dict_one_needle


class NeedleToDictWriter:
    """ Extracts the needle information into dictionary format.
    Attributes:
        needle_data: an empty list to append to.
        patientID : str specifying patient id
        lesionIDX: int specifying the needle count
        needles: needles class object
    """
    def needlesToDict(needle_data, patientID, lesionIdx, needles):
        for needle_idx, needle in enumerate(needles):
            needle_dict = needle.to_dict(patientID, lesionIdx, needle_idx)  # needle_dict is a list type
            needle_data.append(needle_dict)


class TPEErrors:

    def __init__(self):
        self.angular = None
        self.longitudinal = None
        self.lateral = None
        self.euclidean = None

    def setTPEErrors(self, lateral, angular, longitudinal, euclidean):
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

    def setTrajectory(self, entrypoint, targetpoint):
        self.entrypoint = entrypoint
        self.targetpoint = targetpoint
