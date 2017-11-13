# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 13:43:49 2017

@author: Raluca Sandu
"""
# libraries import

import numpy as np
from medpy import metric
import pandas as pd
import SimpleITK as sitk
from scipy import ndimage
from surface import Surface
from enum import Enum
import matplotlib.pyplot as plt
#plt.style.use('ggplot')
plt.style.use('seaborn')
#print(plt.style.available)
from IPython.display import display, HTML
from ipywidgets import interact, fixed
#%matplotlib inline
#%%
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
# read some files and display the Mauerer distance map in Jupyter Notebook as heat map

# image read as img[x,y,z]
reference_segmentation = sitk.ReadImage('tumorSegm', sitk.sitkUInt8)
segmentation = sitk.ReadImage('ablationSegm',sitk.sitkUInt8)
print(reference_segmentation.GetSpacing())
print(reference_segmentation.GetOrigin())
print(reference_segmentation.GetSize())
label = 255



class SurfaceDistanceMeasuresITK(Enum):
    hausdorff_distance, max_surface_distance, avg_surface_distance, median_surface_distance, std_surfance_distance = range(5)

# Computes the maximum symmetric surface distance = Hausdorff distance between the two objects surfaces.
class SurfaceDistanceMeasuresSurfacePy(Enum):
    hausdorff_distance, avg_symmetric_surface_distance, rms_symmetric_surface_distance = range(3)

class MedpyMetricDists(Enum):
    hausdorff_distance, avg_surface_distance, avg_symmetric_surface_distance = range(3)

surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasuresITK.__members__.items())))
surface_distance_SurfacePy = np.zeros((1,len(SurfaceDistanceMeasuresSurfacePy.__members__.items())))
surface_dists_Medpy = np.zeros((1,len(MedpyMetricDists.__members__.items())))

segmented_surface = sitk.LabelContour(segmentation)

# init signed mauerer distance as reference metrics
reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False, useImageSpacing=True))

# init label intensity statistics filter
label_intensity_statistics_filter = sitk.LabelIntensityStatisticsImageFilter()
label_intensity_statistics_filter.Execute(segmented_surface, reference_distance_map)

hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
hausdorff_distance_filter.Execute(reference_segmentation, segmentation)

surface_distance_results[0,SurfaceDistanceMeasuresITK.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()
surface_distance_results[0,SurfaceDistanceMeasuresITK.max_surface_distance.value] = label_intensity_statistics_filter.GetMaximum(label)
surface_distance_results[0,SurfaceDistanceMeasuresITK.avg_surface_distance.value] = label_intensity_statistics_filter.GetMean(label)
surface_distance_results[0,SurfaceDistanceMeasuresITK.median_surface_distance.value] = label_intensity_statistics_filter.GetMedian(label)
surface_distance_results[0,SurfaceDistanceMeasuresITK.std_surfance_distance.value] = label_intensity_statistics_filter.GetStandardDeviation(label)

surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)),
                              columns=[name for name, _ in SurfaceDistanceMeasuresITK.__members__.items()])


# mauerer distances from simple itk
fig, ax= plt.subplots()
plt.hist(reference_distance_map)
plt.title('Mauerer Distance Map')

#%%
# img read as img[z,y,x]
img_array = sitk.GetArrayFromImage(reference_segmentation)
seg_array = sitk.GetArrayFromImage(segmentation)
# reverse array in the order x, y, z
img_array_rev = np.flip(img_array,2)
seg_array_rev = np.flip(seg_array,2)
vxlspacing = segmentation.GetSpacing()

if np.count_nonzero(img_array)==0 or np.count_nonzero(seg_array)==0:
    surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.hausdorff_distance.value] = 0
    surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.avg_surface_distance.value] = 0
    surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.rms_surface_distance.value] = 0

else:
    evalsurf = Surface(seg_array_rev,img_array_rev, physical_voxel_spacing = vxlspacing , mask_offset = [0.,0.,0.], reference_offset = [0.,0.,0.])
    surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.hausdorff_distance.value] = evalsurf.get_maximum_symmetric_surface_distance()
    surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.avg_symmetric_surface_distance.value] = evalsurf.get_average_symmetric_surface_distance()
    surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.rms_symmetric_surface_distance.value]= evalsurf.get_root_mean_square_symmetric_surface_distance()

surface_distance_SurfacePY_df = pd.DataFrame(data=surface_distance_SurfacePy, index = list(range(1)),
                              columns=[name for name, _ in SurfaceDistanceMeasuresSurfacePy.__members__.items()])


# compute the hausdorff distances histogram
dists_refImgtoMask = evalsurf.get_reference_mask_nn()
fig1, ax= plt.subplots()
plt.hist(dists_refImgtoMask)
plt.title('18-Neighbourhood NN Euclidean Distances')
#%% use the MedPy metric library

#msd = metric.hd(ref,seg,voxelspacing=vxlspacing)
surface_dists_Medpy[0,MedpyMetricDists.hausdorff_distance.value] = metric.binary.hd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
surface_dists_Medpy[0,MedpyMetricDists.avg_surface_distance.value] = metric.binary.asd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
surface_dists_Medpy[0,MedpyMetricDists.avg_symmetric_surface_distance.value] = metric.binary.assd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)


#%%

# convert to DataFrame
surface_dists_Medpy_df = pd.DataFrame(data=surface_dists_Medpy, index = list(range(1)),
                              columns=[name for name, _ in MedpyMetricDists.__members__.items()])

np.set_printoptions(precision=3)

# Display the data as HTML tables and graphs
display(HTML(surface_distance_results_df.to_html(float_format=lambda x: '%.3f' % x)))
display(HTML(surface_distance_SurfacePY_df.to_html(float_format=lambda x: '%.3f' % x)))
display(HTML(surface_dists_Medpy_df.to_html(float_format=lambda x: '%.3f' % x)))
surface_distance_results_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
surface_distance_SurfacePY_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
surface_dists_Medpy_df.plot(kind='bar').legend(bbox_to_anchor=(1.6,0.9))
#%%
#interact(display_with_overlay,
#         slice_number = (0, reference_segmentation .GetSize()[1]-1), image = fixed(reference_segmentation),
#         segs = fixed(reference_distance_map), window_min = fixed(-1024), window_max=fixed(976));
#
