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
            lesion_data = patient_data[patient_data['LesionNr'] == lesion]
            needles_lesion = lesion_data['NeedleNr'].tolist()
            PlannedEntryPoint = lesion_data['PlannedEntryPoint'].tolist()
            PlannedTargetPoint = lesion_data['PlannedTargetPoint'].tolist()
            ValidationEntryPoint = lesion_data['ValidationEntryPoint'].tolist()
            ValidationTargetPoint = lesion_data['ValidationTargetPoint'].tolist()
            NeedleType = lesion_data['NeedleType'].tolist()
            ReferenceNeedle = lesion_data['ReferenceNeedle'].tolist()

            if True in ReferenceNeedle:
                k = 0
            else:
                # if there is no reference needle for this trajectories, then start needle naming at 1
                k = 1

            for combination_angles in combinations(needles_lesion, 2):

                try:
                    if NeedleType[combination_angles[0]] == 'MWA' or NeedleType[combination_angles[1]] == 'MWA':
                        continue  # go back to the begining of the loop, else option not needed
                except Exception as e:
                    print(repr(e))

                if ReferenceNeedle[combination_angles[0]] is False and ReferenceNeedle[combination_angles[1]] is False:
                    # no reference needle available, older version of XML CAS Logs
                    needleA = needles_lesion[combination_angles[0]] + k
                    needleB = needles_lesion[combination_angles[1]] + k


                    if PlannedTargetPoint[combination_angles[0]].all() and PlannedTargetPoint[
                        combination_angles[0]].all():
                        angle_planned = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[0]],
                                                                   PlannedTargetPoint[combination_angles[0]],
                                                                   PlannedEntryPoint[combination_angles[1]],
                                                                   PlannedTargetPoint[combination_angles[1]])
                    else:
                        angle_planned = np.nan

                    if ValidationTargetPoint[combination_angles[0]] is not None \
                            and ValidationTargetPoint[combination_angles[1]] is not None:
                        # if values exist for the validation then compute the validation angle
                        angle_validation = AngleNeedles.angle_between(ValidationEntryPoint[combination_angles[0]],
                                                                      ValidationTargetPoint[combination_angles[0]],
                                                                      ValidationEntryPoint[combination_angles[1]],
                                                                      ValidationTargetPoint[combination_angles[1]])
                    else:
                        # this angle pair hasn't been validated so assign NaN to the angle validation
                        angle_validation = np.nan

                elif ReferenceNeedle[combination_angles[0]] is True:
                    # ReferenceNeedle is never validated, only plan trajectories are available
                    needleA = 'Reference'
                    needleB = needles_lesion[combination_angles[1]]

                    if (PlannedTargetPoint[combination_angles[0]]) is not None \
                            and (PlannedTargetPoint[combination_angles[0]]) is not None:

                        angle_planned = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[0]],
                                                                   PlannedTargetPoint[combination_angles[0]],
                                                                   PlannedEntryPoint[combination_angles[1]],
                                                                   PlannedTargetPoint[combination_angles[1]])

                    else:
                        angle_planned = np.nan

                    if ValidationTargetPoint[combination_angles[1]] is not None:
                        # if values exist for the validation then compute the validation angle
                        angle_validation = AngleNeedles.angle_between(PlannedEntryPoint[combination_angles[0]],
                                                                      PlannedTargetPoint[combination_angles[0]],
                                                                      ValidationEntryPoint[combination_angles[1]],
                                                                      ValidationTargetPoint[combination_angles[1]])
                    else:
                        angle_validation = np.nan

                needles_angles = {'PatientID': patientID,
                                  'LesionNr': lesion,
                                  'NeedleA': needleA,
                                  'NeedleB': needleB,
                                  'Planned Angle': float("{0:.2f}".format(angle_planned)),
                                  'Validation Angle': float("{0:.2f}".format(angle_validation)),
                                  'Distance Planned': float("{0:.2f}".format(np.nan)),
                                  'Distance Validation': float("{0:.2f}".format(np.nan))
                                  }

                Angles.append(needles_angles)

        return Angles
