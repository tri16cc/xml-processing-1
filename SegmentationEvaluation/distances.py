# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 13:43:49 2017

@author: Raluca Sandu
"""
# libraries import

import numpy as np
import pandas as pd
from enum import Enum
from medpy import metric
import SimpleITK as sitk

#plt.style.use('ggplot')
#plt.style.use('classic')
#print(plt.style.available)

#%%
class DistanceMetrics(object):

    
    def __init__(self,mask, reference):

        # image read as img[x,y,z]
        reference_segmentation = sitk.ReadImage(reference, sitk.sitkUInt8)
        segmentation = sitk.ReadImage(mask,sitk.sitkUInt8)
        label_1 = 255
         
        class SurfaceDistanceMeasuresITK(Enum):
            hausdorff_distance, symmetric_avg,  std_surfance_distance = range(3)
        
        
        class MedpyMetricDists(Enum):
            hausdorff_distanceMedPy, avg_surface_distanceMedPy, avg_symmetric_surface_distanceMedPy = range(3)
        
        surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasuresITK.__members__.items())))
        surface_dists_Medpy = np.zeros((1,len(MedpyMetricDists.__members__.items())))
        
        #%%
        segmented_surface_mask = sitk.LabelContour(segmentation)
        segmented_surface_ref = sitk.LabelContour(reference_segmentation)
        
        # init signed mauerer distance as reference metrics
        self.reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False, useImageSpacing=True))
        self.mask_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(segmentation, squaredDistance=False, useImageSpacing=True))
        
        # init label_1 intensity statistics filter
        label_intensity_statistics_filter = sitk.LabelIntensityStatisticsImageFilter()
        label_intensity_statistics_filter.Execute(segmented_surface_mask, self.reference_distance_map)
        
        hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
        hausdorff_distance_filter.Execute(reference_segmentation, segmentation)

        surface_distance_results[0,SurfaceDistanceMeasuresITK.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()
            
        
        #%% Compute the average symmetric distance
        self.n1 = label_intensity_statistics_filter.GetNumberOfPixels(label_1)
        self.avg_ref = label_intensity_statistics_filter.GetMean(label_1)
        self.max_ref = label_intensity_statistics_filter.GetMaximum(label_1)
        self.std_ref = label_intensity_statistics_filter.GetStandardDeviation(label_1)
        
        # execute the filter from the segmented reference mask to the Mauerer distances map calculated for the mask
        label_intensity_statistics_filter.Execute(segmented_surface_ref, self.mask_distance_map)
        self.avg_seg =  label_intensity_statistics_filter.GetMean(label_1)
        self.max_seg = label_intensity_statistics_filter.GetMaximum(label_1)
        self.std_mask = label_intensity_statistics_filter.GetStandardDeviation(label_1)
        self.n2 = label_intensity_statistics_filter.GetNumberOfPixels(label_1)
        
        symmetric_avg = (self.n1*self.avg_ref + self.n2*self.avg_seg)/(self.n1+self.n2)
        
        self.symmetric_std = np.sqrt((self.n1*(self.std_ref**2+(self.avg_ref-symmetric_avg)**2) + self.n2*(self.std_mask**2+(self.avg_seg-symmetric_avg )**2))/(self.n1+self.n2))
        
        surface_distance_results[0,SurfaceDistanceMeasuresITK.symmetric_avg.value] = symmetric_avg
        surface_distance_results[0,SurfaceDistanceMeasuresITK.std_surfance_distance.value] = self.symmetric_std

        self.surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)),
                                      columns=[name for name, _ in SurfaceDistanceMeasuresITK.__members__.items()])
        
        
        self.surface_distance_results_df.columns = ['Maximum Symmetric Distance', 'Average Symmetric Distance', 'Standard Deviation']
        #%%
        # img read as img[z,y,x]
        img_array = sitk.GetArrayFromImage(reference_segmentation)
        seg_array = sitk.GetArrayFromImage(segmentation)
        # reverse array in the order x, y, z
        img_array_rev = np.flip(img_array,2)
        seg_array_rev = np.flip(seg_array,2)
        vxlspacing = segmentation.GetSpacing()
        
        # use the MedPy metric library
        surface_dists_Medpy[0,MedpyMetricDists.hausdorff_distanceMedPy.value] = metric.binary.hd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
        surface_dists_Medpy[0,MedpyMetricDists.avg_surface_distanceMedPy.value] = metric.binary.asd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
        surface_dists_Medpy[0,MedpyMetricDists.avg_symmetric_surface_distanceMedPy.value] = metric.binary.assd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
        self.surface_dists_Medpy_df = pd.DataFrame(data=surface_dists_Medpy, index = list(range(1)),
                                      columns=[name for name, _ in MedpyMetricDists.__members__.items()])

    #%%
    
    def get_Distances(self):
        # convert to DataFrame
        metrics_all = pd.concat([self.surface_dists_Medpy_df, self.surface_distance_results_df], axis=1)
        return(metrics_all)
    
    def get_SitkDistances(self):
        return self.surface_distance_results_df
    
    def get_MedPyDistances(self):
        return self.surface_dists_Medpy_df
    
    def get_avg_symmetric_dist(self):
        return (self.n1*self.avg_ref + self.n2*self.avg_seg)/(self.n1+self.n2)
    
    def get_std_symmetric_dist(self):
        return self.symmetric_std
    
    def get_max_symmetric_dist(self):
        return max(self.max_ref,self.max_seg)
    
    # to check the accuracy
    def get_rms_symmetric_dist(self):      
        '''compute the root mean square distance'''
        # currently not working as it should
        # square the Mauerer distances distances
        self.mask_distance_map_float = sitk.GetArrayFromImage(self.mask_distance_map)
        self.mask_distance_map_float = np.flip(self.mask_distance_map_float, 2)
        mask_distance_map_squared =  self.mask_distance_map_float ** 2
        
        self.reference_distance_map_float = sitk.GetArrayFromImage(self.reference_distance_map)
        self.reference_distance_map_float = np.flip(self.reference_distance_map_float,2)
        reference_distance_map_squared = self.reference_distance_map_float ** 2
        
        # sum the distances
        mask_distance_map_sum = mask_distance_map_squared.sum()
        reference_distance_map_sum = reference_distance_map_squared.sum()
        
        return np.sqrt(1. / (self.n1 + self.n2)) * np.sqrt(mask_distance_map_sum  + reference_distance_map_sum)
    
    def get_mask_dist_map(self):
        return self.mask_distance_map_float
    
    def get_reference_dist_map(self):
        return self.reference_distance_map_float