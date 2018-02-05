# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:20:31 2018

@author: Raluca Sandu
"""

class Patient():
        
    def __init__(self):
        self.lesion = []
        self.patientId
        
    def addLesion(self, lesion):
        self.lesion.append(lesion)
    
    def getLesions(self):
        return self.lesion

    
class Lesion():
    
    def __init__(self):
        self.needles = []
    
    def getNeedles(self):
        return self.needles
    
    def addNeedle(self, needle):
        self.needles.append(needle)
        
    def newNeedle(self):
        needle = Needle(False, self)
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
    
    def setTPE(self, tpe):
        self.tpeerrors = tpe
        

class TPEErrors():
    
    def __init__(self):
        self.lateral = None
        self.angular = None
        self.longitudinal = None
        self.euclidean = None
        
    def setTPEErrors(self, lateral, angular, longitudinal, euclidean):
        self.lateral = lateral
        self.angular = angular
        self.longitudinal = longitudinal
        self.euclidean = euclidean
        
    def calculateTPEErrors(self,plannedTrajectory, validationTrajectory,offset):
        pass

class Trajectory():
    
    def __init__(self,entrypoint,targetpoint):
        self.entrypoint = entrypoint
        self.targetpoint = targetpoint

    