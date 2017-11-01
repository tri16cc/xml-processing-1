
# coding: utf-8

# # Segmentation Evaluation In Python

# Raluca Sandu November 2017

# In[157]:

import SimpleITK as sitk
import numpy as np
from medpy import metric
from surface import Surface
#import dicom
#import scipy
#import scipy.misc

import matplotlib.pyplot as plt
#get_ipython().magic('matplotlib inline')

from ipywidgets import interact, fixed

# Utility Display for Segmentation Visualization

# In[158]:

def display_with_overlay(slice_number, image, segs, window_min, window_max):
    
    """
    Display a CT slice with segmented contours overlaid onto it. The contours are the edges of 
    the labeled regions.
    """
    img = image[:,:,slice_number]
    msk = segs[:,:,slice_number]
    overlay_img = sitk.LabelMapContourOverlay(sitk.Cast(msk, sitk.sitkLabelUInt8), 
                                              sitk.Cast(sitk.IntensityWindowing(img,
                                                                                windowMinimum=window_min, 
                                                                                windowMaximum=window_max), 
                                                        sitk.sitkUInt8), 
                                             opacity = 1, 
                                             contourThickness=[2,2])
    #We assume the original slice is isotropic, otherwise the display would be distorted 
    plt.imshow(sitk.GetArrayViewFromImage(overlay_img))
    plt.axis('off')
    plt.show()


# In[160]:

image = sitk.ReadImage("tumor", sitk.sitkUInt8)

segmentation =  sitk.ReadImage("ablation",sitk.sitkUInt8)

segmentation_file_names = ["tumor", "ablation"]

segmentations = [sitk.ReadImage((file_name), sitk.sitkUInt8) for file_name in segmentation_file_names]


# In[162]:

interact(display_with_overlay, 
         slice_number = (0, image.GetSize()[1]-1), image = fixed(image),
         segs = fixed(segmentation), window_min = fixed(-1024), window_max=fixed(976));


# Evaluate with overlap metrics and surface distance metrics

# In[163]:

from enum import Enum

# Use enumerations to represent the various evaluation measures
class OverlapMeasures(Enum):
    jaccard, dice, volume_similarity, false_negative, false_positive = range(5)

class SurfaceDistanceMeasures(Enum):
    hausdorff_distance, mean_surface_distance, median_surface_distance, std_surface_distance, max_surface_distance = range(5)


# In[164]:

# Empty numpy arrays to hold the results 
overlap_results = np.zeros((1,len(OverlapMeasures.__members__.items())))  
surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasures.__members__.items())))  

overlap_measures_filter = sitk.LabelOverlapMeasuresImageFilter()

hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()


# Use the absolute values of the distance map to compute the surface distances (distance map sign, outside or inside 
#  relationship, is irrelevant)
#%%

reference_segmentation = image
# In[166]:

reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False))
label_intensity_statistics_filter = sitk.LabelIntensityStatisticsImageFilter()
label = 255


#%%
overlap_measures_filter.Execute(reference_segmentation, segmentation)
overlap_results[0,OverlapMeasures.jaccard.value] = overlap_measures_filter.GetJaccardCoefficient()
overlap_results[0,OverlapMeasures.dice.value] = overlap_measures_filter.GetDiceCoefficient()
overlap_results[0,OverlapMeasures.volume_similarity.value] = overlap_measures_filter.GetVolumeSimilarity()
overlap_results[0,OverlapMeasures.false_negative.value] = overlap_measures_filter.GetFalseNegativeError()
overlap_results[0,OverlapMeasures.false_positive.value] = overlap_measures_filter.GetFalsePositiveError()

#%% 
''' More Overlap Metrics'''
'''Relative Volume Difference'''
volscores = {}
ref = sitk.GetArrayFromImage(image)
seg = sitk.GetArrayFromImage(segmentation)
volscores['rvd'] = metric.ravd(seg, ref)
volscores['dice'] = metric.dc(seg,ref)
volscores['jaccard'] = metric.binary.jc(seg,ref)
volscores['voe'] = 1. - volscores['jaccard']

vxlspacing = np.asarray(segmentation.GetSpacing()) # assuming both segmentation and image have the same spacing
#[1.0,0.845703125,0.845703125]

if np.count_nonzero(seg) ==0 or np.count_nonzero(ref)==0:
		volscores['assd'] = 0
		volscores['msd'] = 0
else:
    
		evalsurf = Surface(seg,ref, physical_voxel_spacing = vxlspacing , mask_offset = [0.,0.,0.], reference_offset = [0.,0.,0.])
		volscores['assd'] = evalsurf.get_average_symmetric_surface_distance()
		volscores['msd'] = metric.hd(ref,seg,voxelspacing=vxlspacing)
# In[168]:

# Hausdorff distance
hausdorff_distance_filter.Execute(reference_segmentation, segmentation)
surface_distance_results[0,SurfaceDistanceMeasures.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()
# Surface distance measures
segmented_surface = sitk.LabelContour(segmentation)
label_intensity_statistics_filter.Execute(segmented_surface, reference_distance_map)
surface_distance_results[0,SurfaceDistanceMeasures.mean_surface_distance.value] = label_intensity_statistics_filter.GetMean(label)
surface_distance_results[0,SurfaceDistanceMeasures.median_surface_distance.value] = label_intensity_statistics_filter.GetMedian(label)
surface_distance_results[0,SurfaceDistanceMeasures.std_surface_distance.value] = label_intensity_statistics_filter.GetStandardDeviation(label)
surface_distance_results[0,SurfaceDistanceMeasures.max_surface_distance.value] = label_intensity_statistics_filter.GetMaximum(label)


# Print the matrices for overlap metrics and surface distance

# In[169]:

np.set_printoptions(precision=3)
print(overlap_results)
print(surface_distance_results)


# In[170]:

import pandas as pd
from IPython.display import display, HTML 

# Graft our results matrix into pandas data frames 
overlap_results_df = pd.DataFrame(data=overlap_results, index = list(range(1)), 
                                  columns=[name for name, _ in OverlapMeasures.__members__.items()])
 
surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)), 
                                  columns=[name for name, _ in SurfaceDistanceMeasures.__members__.items()]) 

seg_quality_results_df = pd.DataFrame(data=volscores, index = list(range(1)), 
                                  columns=[name for name, _ in volscores.items()]) 

# Display the data as HTML tables and graphs
display(HTML(overlap_results_df.to_html(float_format=lambda x: '%.3f' % x)))
display(HTML(surface_distance_results_df.to_html(float_format=lambda x: '%.3f' % x)))
display(HTML(seg_quality_results_df.to_html(float_format=lambda x: '%.3f' % x)))
overlap_results_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
surface_distance_results_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
seg_quality_results_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))

#%%
