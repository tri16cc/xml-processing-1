# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:20:31 2018

@author: Raluca Sandu
"""
import numpy as np

class Patient():
        
    def __init__(self,patientId):
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
    
#    def findPatient(self,patientId):
        
    def findLesion(self,lesion):
        threshold = 2
        foundLesions = list(filter(lambda l: 
            l.distanceTo(lesion) < threshold, self.lesions))
        if len(foundLesions) == 0:
            return None
        elif len(foundLesions) == 1:
            return foundLesions[0]
        else:
            raise Exception('Something went wrong')

    
class Lesion():
    # location is a numpy array
    def __init__(self, location):
        self.needles = []
        if location is not None and len(location) is 3:
            self.location = location
        else:
            raise Exception('Lesion Location not given')
    
    def distanceTo(self, otherLesion):
        # compute euclidean distances for TPE to check whether the same lesion
        tp1 = otherLesion.location
        tp2 = self.lesion.location
        dist = np.linalg.norm(tp1-tp2)
        return dist
        pass
    
    def getNeedles(self):
        return self.needles
    
    def newNeedle(self, isreference):
        needle = Needle(isreference,self)
        self.needles.append(needle)
        return needle
    
    
class Needle():
    
    def __init__(self, isreference, lesion):
        self.isreference = isreference
        self.planned = None
        self.validation = None
        self.tpeerorrs = None
        self.lesion = lesion
    
    def setPlannedTrajectory(self, trajectory):
       self.planned = trajectory
    
    def setValidationTrajectory(self,trajectory):
        self.validation = trajectory
    
    def setTPEs(self):
        self.tpeerorrs = TPEErrors()
        return self.tpeerorrs

    def getTPEs(self):
        return self.tpeerorrs
    
    def getPlannedTrajectory(self):
        return self.planned
    
    def getValidationTrajectory(self):
        return self.validation
        

class TPEErrors():
    
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
      
        
    def calculateTPEErrors(self,plannedTrajectory, validationTrajectory,offset):
        # in case of offset that wasn't accounted for in the old versions of cascination
        pass


class Trajectory():
    
    def __init__(self,entrypoint,targetpoint):
        self.entrypoint = entrypoint
        self.targetpoint = targetpoint

    