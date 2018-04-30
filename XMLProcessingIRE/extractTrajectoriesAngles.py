# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 11:28:21 2018

@author: Raluca Sandu
"""
import numpy as np
import AngleNeedles
from itertools import combinations


class ComputeAnglesTrajectories():
    
         
    def FromTrajectoriesToNeedles(patient_data, patientID, Angles):
        
        lesion_unique = patient_data['LesionNr'].unique()
    
        for i, lesion in enumerate(lesion_unique):
            lesion_data = patient_data[patient_data['LesionNr']==lesion]
            needles_lesion = lesion_data['NeedleNr'].tolist()
            PlannedEntryPoint = lesion_data['PlannedEntryPoint'].tolist()
            PlannedTargetPoint = lesion_data['PlannedTargetPoint'].tolist()
            ValidationEntryPoint = lesion_data['ValidationEntryPoint'].tolist()
            ValidationTargetPoint = lesion_data['ValidationTargetPoint'].tolist()
            ReferenceNeedle = lesion_data['ReferenceNeedle'].tolist()

            for combination_angles in combinations(needles_lesion,2):

                
                angle_planned = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[0]], \
                                                           PlannedTargetPoint[combination_angles[0]], \
                                                           PlannedEntryPoint[combination_angles[1]], \
                                                           PlannedTargetPoint[combination_angles[1]]) 
                
                try:
                    euclidean_distance_planned = np.linalg.norm(PlannedTargetPoint[combination_angles[0]]- PlannedTargetPoint[combination_angles[1]])
                except:
                    euclidean_distance_validation = np.nan
                
                if combination_angles[0] != 0 and combination_angles[1] != 0:
                    
                     angle_validation = AngleNeedles.angle_between(ValidationEntryPoint[combination_angles[0]], \
                                                                  ValidationTargetPoint[combination_angles[0]], \
                                                                  ValidationEntryPoint[combination_angles[1]], \
                                                                  ValidationTargetPoint[combination_angles[1]])
                     
                     try:
                         euclidean_distance_validation =  np.linalg.norm(ValidationTargetPoint[combination_angles[0]]-ValidationTargetPoint[combination_angles[1]])
                     except:
                            euclidean_distance_validation = np.nan
                         
                         
                if ReferenceNeedle[combination_angles[0]] == True:
                    
                    needleA = 'Reference'
                    needleB = combination_angles[1] 
                    angle_validation = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[0]], \
                                                           PlannedTargetPoint[combination_angles[0]], \
                                                           ValidationEntryPoint[combination_angles[1]], \
                                                           ValidationTargetPoint[combination_angles[1]])
                    try:
                        euclidean_distance_validation =  np.linalg.norm(PlannedTargetPoint[combination_angles[0]]-ValidationTargetPoint[combination_angles[1]])
                    except:
                            euclidean_distance_validation = np.nan
                            
                elif ReferenceNeedle[combination_angles[0]] is False and ReferenceNeedle[combination_angles[1]] is False:
                    needleA = combination_angles[0]
                    needleB = combination_angles[1] 
                    angle_validation = AngleNeedles.angle_between(ValidationEntryPoint[combination_angles[0]], \
                                                                  ValidationTargetPoint[combination_angles[0]], \
                                                                  ValidationEntryPoint[combination_angles[1]], \
                                                                  ValidationTargetPoint[combination_angles[1]])
                    try:
                        euclidean_distance_validation =  np.linalg.norm(ValidationTargetPoint[combination_angles[0]]-ValidationTargetPoint[combination_angles[1]])
                    except:
                        euclidean_distance_validation = np.nan
                         
                        
                else:
                    needleB = 'Reference'
                    needleA = combination_angles[0]
                    angle_validation = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[1]], \
                                                           PlannedTargetPoint[combination_angles[1]], \
                                                           ValidationEntryPoint[combination_angles[0]], \
                                                           ValidationTargetPoint[combination_angles[0]])
                    try:
                        euclidean_distance_validation =  np.linalg.norm(PlannedTargetPoint[combination_angles[1]]-ValidationTargetPoint[combination_angles[0]])
                    except:
                        euclidean_distance_validation = np.nan
                        
                needles_angles = {'PatientID': patientID,
                                  'LesionNr': lesion,
                                  'NeedleA': needleA,
                                  'NeedleB': needleB,
                                  'Planned Angle': float("{0:.2f}".format(angle_planned)),
                                  'Validation Angle': float("{0:.2f}".format(angle_validation)),
                                  'Distance Planned': float("{0:.2f}".format(euclidean_distance_planned)),
                                  'Distance Validation': float("{0:.2f}".format(euclidean_distance_validation))
                                  }
                
                Angles.append(needles_angles)
                
        return Angles


