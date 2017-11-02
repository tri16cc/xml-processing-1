
# coding: utf-8

# # Segmentation Evaluation In Python

# Raluca Sandu November 2017

# In[157]:

import SimpleITK as sitk
import numpy as np
from medpy import metric
from surface import Surface
from enum import Enum
import pandas as pd
from IPython.display import display, HTML 
import os
#import dicom
#import scipy
#import scipy.misc

import matplotlib.pyplot as plt
#get_ipython().magic('matplotlib inline')
#from ipywidgets import interact, fixed

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
#%%
''' Volume Overlap measures'''
''' Surface Distance Measures'''

# Use enumerations to represent the various evaluation measures
class OverlapMeasures(Enum):
     dice, jaccard, volume_similarity, volumetric_overlap_error, relative_vol_difference = range(5)

class SurfaceDistanceMeasures(Enum):
    max_surface_distance, hausdorff_distance, rmsd, assd,  mean_surface_distance, median_surface_distance = range(6)


#%% 
'''Read Segmentations and their Respective Ablation Zone'''

segmentation_data = []
df_metrics = pd.DataFrame()

#image = sitk.ReadImage("tumor", sitk.sitkUInt8)
#
#segmentation =  sitk.ReadImage("ablation",sitk.sitkUInt8)

rootdir = "C:/Users/Raluca Sandu/Documents/LiverInterventionsBern_Ablations/segm2/"

for subdir, dirs, files in os.walk(rootdir):
    tumorFilePath  = ''
    ablationSegm = ''
    for file in files:
        if file == "tumorSegm":
            FilePathName = os.path.join(subdir, file)
            tumorFilePath = os.path.normpath(FilePathName)
        elif file == "ablationSegm":
            FilePathName = os.path.join(subdir, file)
            ablationFilePath = os.path.normpath(FilePathName)
        else:
            print("")
        
    if (tumorFilePath) and (ablationFilePath):
        dir_name = os.path.dirname(ablationFilePath)
        dirname2 = os.path.split(dir_name)[1]
        data = {'PatientName' : dirname2,
                'TumorFile' : tumorFilePath,
                'AblationFile' : ablationFilePath
                }
        segmentation_data.append(data)  

df_patientdata = pd.DataFrame(segmentation_data)

#%%
ablations = df_patientdata['AblationFile'].tolist()
segmentations = df_patientdata['TumorFile'].tolist()

for idx, seg in enumerate(segmentations):
    image = sitk.ReadImage(seg, sitk.sitkUInt8)
    segmentation =  sitk.ReadImage(ablations[idx],sitk.sitkUInt8)

    #%%
    
    # Empty numpy arrays to hold the results 
    overlap_results = np.zeros((1,len(OverlapMeasures.__members__.items())))  
    surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasures.__members__.items())))  
    
    overlap_measures_filter = sitk.LabelOverlapMeasuresImageFilter()
    
    hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
    
    
    # In[166]:
    reference_segmentation = image
    reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False))
    label_intensity_statistics_filter = sitk.LabelIntensityStatisticsImageFilter()
    label = 255
    
    
    
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
    		volscores['msd'] = 0 ; volscores['rmsd'] = 0
    else:
        
    		evalsurf = Surface(seg,ref, physical_voxel_spacing = vxlspacing , mask_offset = [0.,0.,0.], reference_offset = [0.,0.,0.])
    		volscores['assd'] = evalsurf.get_average_symmetric_surface_distance(); volscores['rmsd'] = evalsurf.get_root_mean_square_symmetric_surface_distance()
    		volscores['msd'] = metric.hd(ref,seg,voxelspacing=vxlspacing)
        
    #%%
    # Volume Overlap Metrics
    overlap_measures_filter.Execute(reference_segmentation, segmentation)
    overlap_results[0,OverlapMeasures.jaccard.value] = overlap_measures_filter.GetJaccardCoefficient()
    overlap_results[0,OverlapMeasures.dice.value] = overlap_measures_filter.GetDiceCoefficient()
    overlap_results[0,OverlapMeasures.volume_similarity.value] = overlap_measures_filter.GetVolumeSimilarity()
    overlap_results[0,OverlapMeasures.volumetric_overlap_error.value] = volscores['voe']
    overlap_results[0,OverlapMeasures.relative_vol_difference.value] = volscores['rvd'] 
    # Hausdorff distance
    hausdorff_distance_filter.Execute(reference_segmentation, segmentation)
    surface_distance_results[0,SurfaceDistanceMeasures.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()
    # Surface distance measures
    segmented_surface = sitk.LabelContour(segmentation)
    label_intensity_statistics_filter.Execute(segmented_surface, reference_distance_map)
    surface_distance_results[0,SurfaceDistanceMeasures.mean_surface_distance.value] = label_intensity_statistics_filter.GetMean(label)
    surface_distance_results[0,SurfaceDistanceMeasures.median_surface_distance.value] = label_intensity_statistics_filter.GetMedian(label)
    surface_distance_results[0,SurfaceDistanceMeasures.rmsd.value] = volscores['rmsd']
    surface_distance_results[0,SurfaceDistanceMeasures.assd.value] = volscores['assd']
    surface_distance_results[0,SurfaceDistanceMeasures.max_surface_distance.value] = label_intensity_statistics_filter.GetMaximum(label)
    
    # In[169]:
    
#    np.set_printoptions(precision=3)
    #print(overlap_results)
    #print(surface_distance_results)
    
    # In[170]:
    
    
    # Graft our results matrix into pandas data frames 
    overlap_results_df = pd.DataFrame(data=overlap_results, index = list(range(1)), 
                                      columns=[name for name, _ in OverlapMeasures.__members__.items()])
     
    surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)), 
                                      columns=[name for name, _ in SurfaceDistanceMeasures.__members__.items()]) 
    
    metrics_all = pd.concat([overlap_results_df, surface_distance_results_df], axis=1)
    df_metrics = df_metrics.append(metrics_all)
    df_metrics.index = list(range(len(df_metrics)))

    #
    #seg_quality_results_df = pd.DataFrame(data=volscores, index = list(range(1)), 
    #                                  columns=[name for name, _ in volscores.items()]) 
    
    # Display the data as HTML tables and graphs
    display(HTML(overlap_results_df.to_html(float_format=lambda x: '%.3f' % x)))
    display(HTML(surface_distance_results_df.to_html(float_format=lambda x: '%.3f' % x)))
    overlap_results_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
    surface_distance_results_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
    
    
    #%% 
    '''edit axis limits & labels '''
    ''' save plots'''
    # TO DO
#%%
''' save to excel '''
df_final = pd.concat([df_patientdata, df_metrics], axis=1)
filename = 'SegmentationMetrics_4Subjects'  + '.xlsx' 
writer = pd.ExcelWriter(filename)
df_final.to_excel(writer, index=False, float_format='%.2f')

angle_value = float("{0:.2f}".format(angle_degrees))