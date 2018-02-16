# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:17:01 2018

@author: Raluca Sandu
"""
from elementExistsXml import elementExists


def extractTPES(tpes):
    '''function to extract the TPEs (target positioning errors) values
        INPUT: singleTrajectory.Measurements.Measurement.TPEErrors
        OUTPUT: target errors as tuple of 4 
    '''
    
    if elementExists(tpes, 'targetLateral'):
        targetLateral = tpes['targetLateral'][0:5]
        targetLongitudinal = tpes['targetLongitudinal'][0:5]
        targetAngular = tpes['targetAngular'][0:5]
        targetEuclidean = tpes['targetResidualError'][0:5]
    else:
        # the case where the TPE errors are 0 in the TPE<0>. instead they are attributes of the measurement   
        targetLateral = tpes['targetLateral'][0:5]
        targetLongitudinal = tpes['targetLongitudinal'][0:5]
        targetAngular = tpes['targetAngular'][0:5]
        targetEuclidean = tpes['targetResidualError'][0:5]
        
    return targetLateral, targetAngular, targetLongitudinal, targetEuclidean