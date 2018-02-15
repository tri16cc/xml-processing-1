# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:17:01 2018

@author: Raluca Sandu
"""


def extractTPES(tpes):
    '''function to extract the TPEs values
        INPUT: singleTrajectory.Measurements.Measurement.TPEErrors
        OUTPUT: target errors as tuple of 4 
    '''
    
    if elementExists(tpes,'tpes', 'targetLateral'):
        targetLateral = tpes['targetLateral'][0:5]
        targetLongitudinal = tpes['targetLongitudinal'][0:5]
        targetAngular = tpes['targetAngular'][0:5]
        targetResidual = tpes['targetResidualError'][0:5]
    else:
        # the case where the TPE errors are 0 in the TPE<0>. instead they are attributes of the measurement   
        targetLateral = tpes['targetLateral'][0:5]
        targetLongitudinal = tpes['targetLongitudinal'][0:5]
        targetAngular = tpes['targetAngular'][0:5]
        targetResidual = tpes['targetResidualError'][0:5]
        
    return targetLateral, targetLongitudinal, targetAngular, targetResidual