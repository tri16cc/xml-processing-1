# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 14:17:41 2017

@author: Raluca Sandu
"""

import numpy as np
import pandas as pd
from enum import Enum
from medpy import metric
import SimpleITK as sitk
#%%
class VolumeMetrics(object):
    
    def __init__(self,mask, reference):
        
        reference_segmentation = sitk.ReadImage(reference, sitk.sitkUInt8)
        segmentation = sitk.ReadImage(mask,sitk.sitkUInt8)
        
        ref_array = sitk.GetArrayFromImage(reference_segmentation) # convert the sitk image to numpy array 
        seg_array = sitk.GetArrayFromImage(segmentation)
        
        class OverlapMeasures(Enum):
            dice, jaccard, volume_similarity, volumetric_overlap_error, relative_vol_difference = range(5)
        
        overlap_results = np.zeros((1,len(OverlapMeasures.__members__.items())))  
        overlap_measures_filter = sitk.LabelOverlapMeasuresImageFilter()
        
        overlap_measures_filter.Execute(reference_segmentation, segmentation)
        overlap_results[0,OverlapMeasures.jaccard.value] = overlap_measures_filter.GetJaccardCoefficient()
        overlap_results[0,OverlapMeasures.dice.value] = overlap_measures_filter.GetDiceCoefficient()
        overlap_results[0,OverlapMeasures.volume_similarity.value] = overlap_measures_filter.GetVolumeSimilarity()
        overlap_results[0,OverlapMeasures.volumetric_overlap_error.value] = 1. - overlap_measures_filter.GetJaccardCoefficient()
        overlap_results[0,OverlapMeasures.relative_vol_difference.value] = metric.ravd(seg_array, ref_array)
        
        self.overlap_results_df = pd.DataFrame(data=overlap_results, index = list(range(1)), 
                                  columns=[name for name, _ in OverlapMeasures.__members__.items()])
        self.overlap_results_df.columns = ['Dice', 'Jaccard', 'Volume Similarity', 'Volume Overlap Error', 'Relative Volume Difference']
        
    def get_VolumeMetrics(self):
        return self.overlap_results_df