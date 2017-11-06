
# coding: utf-8

# # Segmentation Evaluation In Python - metrics for volume overlap

# Raluca Sandu November 2017

#%% Libraries Import
import os
import numpy as np
import pandas as pd
from enum import Enum
from medpy import metric
import SimpleITK as sitk
from surface import Surface
import graphing as gh
import matplotlib.pyplot as plt
from IPython.display import display, HTML 
# %%
def display_with_overlay(slice_number, image, segs, window_min, window_max):
    
    """
    Display a CT slice with segmented contours overlaid onto it. The contours are the edges of 
    the labeled regions. Only works in Jupyter Notebook
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
def plot_v1(data):
    # Create the figure and axis objects I'll be plotting on
    fig, ax = plt.subplots()

    # Plot the bars
    ax.bar(np.arange(len(data)), data, align='center')
    
    # Show the 50% mark, which would indicate an equal
    # number of tasks being completed by the robot and the
    # human. There are 39 tasks total, so 50% is 19.5
    ax.hlines(19.5, -0.5, 5.5, linestyle='--', linewidth=1)
    
    # Set a reasonable y-axis limit
    ax.set_ylim(0, 40)
    
    # Apply labels to the bars so you know which is which
    ax.set_xticks(np.arange(len(data)))
    ax.set_xticklabels(["\n".join(x) for x in data.index])
    
    return fig, ax



#%%
''' Volume Overlap measures:
    - Dice (itk)
    - Jaccard (itk)
    - Volumetric Similarity (itk)
    - Volumetric Overlap Error (voe) - @package medpy.metric.surface by Oskar Maier. calls function "surface.py"
    - Relative Volume Difference (rvd) - Volumetric Overlap Error (voe) - @package medpy.metric.surface by Oskar Maier. calls function "surface.py"

'''
''' Surface Distance Measures:
     - Maximum Surface Distance (which might be hausdorff need to check) - itk
     - Hausdorff Distance - itk
     - Mean Surface Distance - itk
     - Median Surface Distance - itk
     - rmsd : root mean square symmetric surface distance [mm] -  @package medpy.metric.surface by Oskar Maier. calls function "surface.py"
     - assd:  average symmetric surface distance [mm] - -  @package medpy.metric.surface by Oskar Maier. calls function "surface.py"
'''
# Use enumerations to represent the various evaluation measures
# very stupid way to do it atm, change it later
class OverlapMeasures(Enum):
     dice, jaccard, volume_similarity, volumetric_overlap_error, relative_vol_difference = range(5)

class SurfaceDistanceMeasures(Enum):
    max_surface_distance, hausdorff_distance, rmsd, assd, median_surface_distance = range(5)

#%% 
'''Read Segmentations and their Respective Ablation Zone
    Assumes both maks are isotropic (have the same number of slices).
    Foreground value label = 255 [white] and is considered to be the object of interest.
    Background object = 0
    
    --- This function requieres a root directory filepath that contains segmnations of ablations and tumors.
        it assumes the parent directory is named after the patient name/id
        Input : rootdirectory filepath
        Output: dataframe containing filepaths of segmentations and ablations for a specific patient.    
'''

segmentation_data = [] # list of dictionaries containing the filepaths of the segmentations

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

# convert to data frame 
df_patientdata = pd.DataFrame(segmentation_data)
df_metrics = pd.DataFrame() # emtpy dataframe to append the segmentation metrics calculated

ablations = df_patientdata['AblationFile'].tolist()
segmentations = df_patientdata['TumorFile'].tolist()
pats = df_patientdata['PatientName']
#%%

for idx, seg in enumerate(segmentations):
    image = sitk.ReadImage(seg, sitk.sitkUInt8)
    segmentation =  sitk.ReadImage(ablations[idx],sitk.sitkUInt8)

    '''init vectors (size) that will contain the volume and distance metrics'''
    '''init the OverlapMeasures Image Filter and the HausdorffDistance Image Filter from Simple ITK'''

    overlap_results = np.zeros((1,len(OverlapMeasures.__members__.items())))  
    surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasures.__members__.items())))  
    
    overlap_measures_filter = sitk.LabelOverlapMeasuresImageFilter()
    hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
    
    reference_segmentation = image # the refenrence image in this case is the tumor mask
    label = 255
    # init signed mauerer distance as reference metrics
    reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False))
    label_intensity_statistics_filter = sitk.LabelIntensityStatisticsImageFilter()
 
    ''' Calculate Overlap Metrics'''
    volscores = {}
    ref = sitk.GetArrayFromImage(image) # convert the sitk image to numpy array 
    seg = sitk.GetArrayFromImage(segmentation)
    volscores['rvd'] = metric.ravd(seg, ref)
    volscores['dice'] = metric.dc(seg,ref)
    volscores['jaccard'] = metric.binary.jc(seg,ref)
    volscores['voe'] = 1. - volscores['jaccard']
   
    ''' Calculate Surface Distance Metrics'''
    if segmentation.GetSpacing() != image.GetSpacing():
        print('The Spacing between slices is different between the segmentation and reference image')
    else:
        vxlspacing = np.asarray(segmentation.GetSpacing()) # assuming both segmentation and image have the same spacing
    
    if np.count_nonzero(seg)==0 or np.count_nonzero(ref)==0:
    		volscores['assd'] = 0
    		volscores['msd'] = 0 ; volscores['rmsd'] = 0
    else:
    		evalsurf = Surface(seg,ref, physical_voxel_spacing = vxlspacing , mask_offset = [0.,0.,0.], reference_offset = [0.,0.,0.])
    		volscores['assd'] = evalsurf.get_average_symmetric_surface_distance(); volscores['rmsd'] = evalsurf.get_root_mean_square_symmetric_surface_distance()
    		volscores['msd'] = metric.hd(ref,seg,voxelspacing=vxlspacing)
        

    ''' Add the Volume Overlap Metrics in the Enum vector '''
    overlap_measures_filter.Execute(reference_segmentation, segmentation)
    overlap_results[0,OverlapMeasures.jaccard.value] = overlap_measures_filter.GetJaccardCoefficient()
    overlap_results[0,OverlapMeasures.dice.value] = overlap_measures_filter.GetDiceCoefficient()
    overlap_results[0,OverlapMeasures.volume_similarity.value] = overlap_measures_filter.GetVolumeSimilarity()
    overlap_results[0,OverlapMeasures.volumetric_overlap_error.value] = volscores['voe']
    overlap_results[0,OverlapMeasures.relative_vol_difference.value] = volscores['rvd'] 
    ''' Add the Surface Distance Metrics in the Enum vector '''
    # Hausdorff distance
    hausdorff_distance_filter.Execute(reference_segmentation, segmentation)
    surface_distance_results[0,SurfaceDistanceMeasures.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()
    # Surface distance measures
    segmented_surface = sitk.LabelContour(segmentation)
    label_intensity_statistics_filter.Execute(segmented_surface, reference_distance_map)
#    surface_distance_results[0,SurfaceDistanceMeasures.mean_surface_distance.value] = label_intensity_statistics_filter.GetMean(label)
    surface_distance_results[0,SurfaceDistanceMeasures.median_surface_distance.value] = label_intensity_statistics_filter.GetMedian(label)
    surface_distance_results[0,SurfaceDistanceMeasures.rmsd.value] = volscores['rmsd']
    surface_distance_results[0,SurfaceDistanceMeasures.assd.value] = volscores['assd']
    surface_distance_results[0,SurfaceDistanceMeasures.max_surface_distance.value] = label_intensity_statistics_filter.GetMaximum(label)

    ''' Graft our results matrix into pandas data frames '''
    overlap_results_df = pd.DataFrame(data=overlap_results, index = list(range(1)), 
                                      columns=[name for name, _ in OverlapMeasures.__members__.items()])
     
    surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)), 
                                      columns=[name for name, _ in SurfaceDistanceMeasures.__members__.items()]) 
    
    metrics_all = pd.concat([overlap_results_df, surface_distance_results_df], axis=1)
    df_metrics = df_metrics.append(metrics_all)
    df_metrics.index = list(range(len(df_metrics)))

    # Display the data as HTML tables and graphs - why?? probably not necessary 
#    display(HTML(overlap_results_df.to_html(float_format=lambda x: '%.3f' % x)))
#    display(HTML(surface_distance_results_df.to_html(float_format=lambda x: '%.3f' % x)))

    overlap_results_df.columns = ['Dice', 'Jaccard', 'Volume Similarity', 'Volumetric Overlap Error', 'Relative Volume Difference']
    overlap_results_df.plot(kind='bar')
    plt.axhline(0, color='k')
    plt.ylim((-1.0,1.0))
    #%% 
    '''edit axis limits & labels '''
    ''' save plots'''
 
    figName_vol = pats[idx] + 'volumeMetrics'
    figpath1 = os.path.join(rootdir, figName_vol)
    plt.title('Volumetric Overlap Metrics Tumor vs. Ablation. Patient ' + str(idx+1))
    gh.save(figpath1,width=12, height=10)
    
    
    figName_distance = pats[idx] + 'distanceMetrics'
    figpath2 = os.path.join(rootdir, figName_distance)
    surface_distance_results_df.columns = ['Maximum Surface Distance', 'Hausdorff Distance', 'Root Mean Square Symmetric Distance ', 'Average Symmetric Distance', 'Median Surface Distance']
    surface_distance_results_df.plot(kind='bar')
    plt.ylabel('[mm]')
    plt.axhline(0, color='k')
    plt.ylim((0,40))
    plt.title('Surface Distance Metrics Tumor vs. Ablation. Patient ' + str(idx+1))
    gh.save(figpath2,width=12, height=10)
#%%
''' save to excel '''
df_final = pd.concat([df_patientdata, df_metrics], axis=1)
filename = 'SegmentationMetrics_4Subjects'  + '.xlsx' 
writer = pd.ExcelWriter(filename)
df_final.to_excel(writer, index=False, float_format='%.2f')

