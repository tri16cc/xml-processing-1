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
        foundNeedles = list(filter(lambda l:
                                   l.distanceToNeedle(needlelocation) < DISTANCE_BETWEEN_NEEDLES, self.needles))
        if len(foundNeedles) == 0:
            return None
        elif len(foundNeedles) > 0:
            return foundNeedles[0]
        else:
            raise Exception('Something went wrong')


class SegmentationTumor:
    # TODO: add all needles that were validated regardless if they segmentations or not
    # TODO: add self.datetime_created = datetime_created
    # TODO: add self.author_segmentation = author
    # TODO: self.needle_information = (??)
    def __init__(self, needle, path, needle_type, ct_series, series_UID):
        # to do. init to none because not all needles have segmentations
        self.mask_path = path
        self.needle_type = needle_type
        self.ct_series = ct_series
        self.series_UID = series_UID
        self.needle = needle


    #
    # # not sure if segmentation info needs to be set outside init
    # def setSegmentationInfo(self, path, needle_type, ct_series, series_UID):
    #     self.mask_path = path
    #     self.needle_type = needle_type
    #     self.ct_series = ct_series
    #     self.series_UID = series_UID


    def to_dict(self):
        return {'PlannedEntryPoint': self.needle.planned.entrypoint,
                'PlannedTargetPoint': self.needle.planned.targetpoint,
                'ValidationEntryPoint': self.needle.validation.entrypoint,
                'ValidationTargetPoint': self.needle.validation.targetpoint,
                'ReferenceNeedle': self.needle.isreference,
                'AngularError': self.needle.tpeerorrs.angular,
                'LateralError': self.needle.tpeerorrs.lateral,
                'LongitudinalError': self.needle.tpeerorrs.longitudinal,
                'EuclideanError': self.needle.tpeerorrs.euclidean,
                'NeedleType': self.needle.needle_type,
                'TumorPath': self.mask_path,
                'CT_Series': self.ct_series,
                'Series_UID': self.series_UID
                }


class SegmentationAblation:
    # a tumor/ablation can have multiple segmentations done by several radiologists
    def __init__(self, needle, path, needle_type, ct_series, series_UID):
        self.mask_path = path
        self.needle_type = needle_type
        self.ct_series = ct_series
        self.series_UID = series_UID
        self.needle = needle


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
        self.needle_specifications = None
        self.ct_series = ct_series

    def setNeedleSpecifications(self):
        self.needle_specifications = NeedleSpecifications()
        return self.needle_specifications

    def distanceToNeedle(self, needlelocation):
        # compute euclidean distances for TPE to check whether the same lesion
        tp1 = needlelocation
        tp2 = self.planned.targetpoint
        dist = np.linalg.norm(tp1 - tp2)
        return dist
        pass

    def findSegmentation(self, series_UID, segmentation_type):
        # check if the series UID has already been added.
        if segmentation_type.lower() in {"lesion", "lession", "tumor", "tumour"}:
            segmentations = self.segmentations_tumor
        elif segmentation_type.lower() in {"ablation", "ablationzone", "necrosis"}:
            segmentations = self.segmentations_ablation
        idx_seg = list(filter(lambda l: l.series_UID == series_UID, segmentations))
        if len(idx_seg) > 0:
            print("comparison works")
            return 1
        else:
            print("Series UID not in list")
            return None

    def newSegmentation(self, path, needle_type, ct_series, series_UID, segmentation_type):
        if segmentation_type.lower() in {"lesion", "lession", "tumor", "tumour"}:
            # here self represents the needle
            segmentation = SegmentationTumor(self, path, needle_type, ct_series, series_UID)
            self.segmentations_tumor.append(segmentation)
        elif segmentation_type.lower() in {"ablation", "ablationzone", "necrosis"}:
            # here self represents the needle
            segmentation = SegmentationAblation(self, path, needle_type, ct_series, series_UID)
            self.segmentations_ablation.append(segmentation)

    def getAblationSegmentations(self):
        return self.segmentations_ablation

    def getTumorSegmentations(self):
        return self.segmentations_tumor

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


class NeedleToDictWriter:
    """ Extracts the needle information into dictionary format.
    Attributes:
        needle_data: an empty list to append to.
        patientID : str specifying patient id
        lesionIDX: int specifying the needle count
        needles: needles class object
    """
    # TODO: fix the function, missing self
    def needlesToDict(needle_data, patientID, lesionIdx, needles):
        for xIdx, needle in enumerate(needles):
            # a needle can have one or more segmentations
            segmentations_tumor = needle.getTumorSegmentations()
            # segmentations_ablation = needle.getAblationSegmentations()
            for sIdx, segmentation in enumerate(segmentations_tumor):
                needle_dict = segmentation.to_dict()
                needle_dict['PatientID'] = patientID
                needle_dict['LesionNr'] = lesionIdx
                needle_dict['NeedleNr'] = xIdx
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



