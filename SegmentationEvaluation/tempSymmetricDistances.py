# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 11:40:06 2017

@author: Raluca Sandu
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 10:00:32 2017

@author: Raluca Sandu
"""

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

# image read as img[x,y,z]
reference_segmentation = sitk.ReadImage('tumorSegm', sitk.sitkUInt8)
segmentation = sitk.ReadImage('ablationSegm',sitk.sitkUInt8)

 
class SurfaceDistanceMeasuresITK(Enum):
    hausdorff_distance, mean_surface_distance, median_surface_distance, std_surface_distance, rms_surface_distance = range(5)


class MedpyMetricDists(Enum):
    hausdorff_distanceMedPy, avg_surface_distanceMedPy, avg_symmetric_surface_distanceMedPy = range(3)

surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasuresITK.__members__.items())))
surface_dists_Medpy = np.zeros((1,len(MedpyMetricDists.__members__.items())))

#%%
reference_surface = sitk.LabelContour(reference_segmentation)
statistics_image_filter = sitk.StatisticsImageFilter()
# Get the number of pixels in the reference surface by counting all pixels that are 1.
statistics_image_filter.Execute(reference_surface)
num_reference_surface_pixels = int(statistics_image_filter.GetSum()) 

# init signed mauerer distance as reference metrics
reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False, useImageSpacing=True))

hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
hausdorff_distance_filter.Execute(reference_segmentation, segmentation)

surface_distance_results[0,SurfaceDistanceMeasuresITK.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()

#%%
segmented_surface_mask = sitk.LabelContour(segmentation)
mask_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(segmentation, squaredDistance=False, useImageSpacing=True))

# Multiply the binary surface segmentations with the distance maps. The resulting distance
# maps contain non-zero values only on the surface (they can also contain zero on the surface)
seg2ref_distance_map = reference_distance_map*sitk.Cast(segmented_surface_mask, sitk.sitkFloat32)
ref2seg_distance_map = mask_distance_map*sitk.Cast(reference_surface, sitk.sitkFloat32)
    
    # Get the number of pixels in the reference surface by counting all pixels that are 1.
statistics_image_filter.Execute(segmented_surface_mask)
num_segmented_surface_pixels = int(statistics_image_filter.GetSum())

#%%
    # Get all non-zero distances and then add zero distances if required.
seg2ref_distance_map_arr = sitk.GetArrayFromImage(seg2ref_distance_map)
seg2ref_distances = list(seg2ref_distance_map_arr[seg2ref_distance_map_arr!=0]/255) 
#seg2ref_distances = seg2ref_distances + \
#                    list(np.zeros(num_segmented_surface_pixels - len(seg2ref_distances)))
ref2seg_distance_map_arr = sitk.GetArrayFromImage(ref2seg_distance_map)
ref2seg_distances = list(ref2seg_distance_map_arr[ref2seg_distance_map_arr!=0]/255) 
#ref2seg_distances = ref2seg_distances + \
#                    (np.zeros(num_reference_surface_pixels - len(ref2seg_distances)))
                    

#%% Compute the average symmetric distance
all_surface_distances = seg2ref_distances + ref2seg_distances

surface_distance_results[0,SurfaceDistanceMeasuresITK.mean_surface_distance.value] = np.mean(all_surface_distances)
surface_distance_results[0,SurfaceDistanceMeasuresITK.median_surface_distance.value] = np.median(all_surface_distances)
surface_distance_results[0,SurfaceDistanceMeasuresITK.std_surface_distance.value] = np.std(all_surface_distances)

ref2seg_distances_squared = np.asarray(ref2seg_distances) ** 2
seg2ref_distances_squared = np.asarray(seg2ref_distances) ** 2

rms = np.sqrt(1. / (num_reference_surface_pixels + num_segmented_surface_pixels)) * np.sqrt(seg2ref_distances_squared.sum()  + ref2seg_distances_squared.sum())
surface_distance_results[0,SurfaceDistanceMeasuresITK.rms_surface_distance.value] = rms

surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)),
                              columns=[name for name, _ in SurfaceDistanceMeasuresITK.__members__.items()])


surface_distance_results_df.columns = ['Maximum Symmetric Distance', 'Average Symmetric Distance', 'Median Symmetric Distance', 'Standard Deviation', 'RMS Symmetric Distance']
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
surface_dists_Medpy_df = pd.DataFrame(data=surface_dists_Medpy, index = list(range(1)),
                              columns=[name for name, _ in MedpyMetricDists.__members__.items()])

#%%
