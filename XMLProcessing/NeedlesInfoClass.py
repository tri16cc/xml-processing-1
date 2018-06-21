# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:20:31 2018

@author: Raluca Sandu
"""
import numpy as np


class PatientRepo:

    def __init__(self):
        self.patients = []
        
    def addNewPatient(self, patientId):
        patient = Patient(patientId)
        self.patients.append(patient)
        return patient
    
    def getPatients(self):
        return self.patients
    

class Patient:
        
    def __init__(self, patientId):
        self.lesions = []
        self.patientId = patientId
        
    def addLesion(self, lesion):
        self.lesions.append(lesion)
        
    def addNewLesion(self,location):
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
        dist = np.linalg.norm(tp1-tp2)
        return dist
        pass
    
    def getNeedles(self):
        return self.needles
    
    def newNeedle(self, isreference, needle_type):
        needle = Needle(isreference, needle_type, self)
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
            
    
class Needle:
    
    def __init__(self, isreference, needle_type, lesion,):
        self.isreference = isreference
        self.planned = None
        self.validation = None
        self.tpeerorrs = None
        self.lesion = lesion
        self.needle_type = needle_type
    
    def distanceToNeedle(self, needlelocation):
        # compute euclidean distances for TPE to check whether the same lesion
        tp1 = needlelocation
        tp2 = self.planned.targetpoint
        dist = np.linalg.norm(tp1-tp2)
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
        
    def to_dict(self):
         # print('classTPES:', self.tpeerorrs.lateral)
         return {'PlannedEntryPoint': self.planned.entrypoint,
                'PlannedTargetPoint' : self.planned.targetpoint,
                'ValidationEntryPoint' : self.validation.entrypoint,
                'ValidationTargetPoint' : self.validation.targetpoint,
                'ReferenceNeedle': self.isreference,
                'AngularError': self.tpeerorrs.angular,
                'LateralError': self.tpeerorrs.lateral,
                'LongitudinalError': self.tpeerorrs.longitudinal,
                'EuclideanError': self.tpeerorrs.euclidean,
                'NeedleType': self.needle_type}
         

class NeedleToDictWriter:
    """ Extracts the needle information into dictionary format.
    Attributes:
        needle_data: an empty list to append to.
        patientID : str specifying patient id
        lesionIDX: int specifying the needle count
        needles: needles class object

    """
    def needlesToDict(needle_data, patientID, lesionIdx, needles):
        for xIdx, x in enumerate(needles):
            needle_dict = x.to_dict()
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
