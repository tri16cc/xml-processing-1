# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 11:28:21 2018

@author: Raluca Sandu
"""

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
                
                
                if combination_angles[0] != 0 and combination_angles[1] != 0:
                    
                    angle_validation = AngleNeedles.angle_between(ValidationEntryPoint[combination_angles[0]], \
                                                                  ValidationTargetPoint[combination_angles[0]], \
                                                                  ValidationEntryPoint[combination_angles[1]], \
                                                                  ValidationTargetPoint[combination_angles[1]])
                
                
                if ReferenceNeedle[combination_angles[0]] == True:
                    
                    needleA = 'Reference'
                    needleB = combination_angles[1] 
                    angle_validation = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[0]], \
                                                           PlannedTargetPoint[combination_angles[0]], \
                                                           ValidationEntryPoint[combination_angles[1]], \
                                                           ValidationTargetPoint[combination_angles[1]])
                    
                elif ReferenceNeedle[combination_angles[0]] is False and ReferenceNeedle[combination_angles[1]] is False:
                    needleA = combination_angles[0]
                    needleB = combination_angles[1] 
                    angle_validation = AngleNeedles.angle_between(ValidationEntryPoint[combination_angles[0]], \
                                                                  ValidationTargetPoint[combination_angles[0]], \
                                                                  ValidationEntryPoint[combination_angles[1]], \
                                                                  ValidationTargetPoint[combination_angles[1]])
                else:
                    needleB = 'Reference'
                    needleA = combination_angles[0]
                    angle_validation = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[1]], \
                                                           PlannedTargetPoint[combination_angles[1]], \
                                                           ValidationEntryPoint[combination_angles[0]], \
                                                           ValidationTargetPoint[combination_angles[0]])
                    
                        
                needles_angles = {'PatientID': patientID,
                                  'LesionNr': lesion,
                                  'NeedleA': needleA,
                                  'NeedleB': needleB,
                                  'AngleDegrees_planned': float("{0:.2f}".format(angle_planned)),
                                  'AngleDegrees_validation': float("{0:.2f}".format(angle_validation))
                                  }
                
                Angles.append(needles_angles)
        
        return AngleNeedles


