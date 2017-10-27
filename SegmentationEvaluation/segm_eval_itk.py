# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 11:11:31 2017

@author: Raluca Sandu
"""

import SimpleITK as sitk

import numpy as np

#%run update_path_to_download_script
#from downloaddata import fetch_data as fdata
import matplotlib.pyplot as plt
#%matplotlib inline
from ipywidgets import interact, fixed

#%%

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

image = sitk.ReadImage("tumor", sitk.sitkUInt8)
segmentation =  sitk.ReadImage("ablation",sitk.sitkUInt8)
                          
#segmentations = [sitk.ReadImage(fdata(file_name), sitk.sitkUInt8) for file_name in segmentation_file_names]
segmentation_number=(0,len(segmentation)-1)   

interact(display_with_overlay, 
         slice_number = (0, image.GetSize()[1]-1), image = fixed(image),
         segs = fixed(segmentation), window_min = fixed(-1024), window_max=fixed(976));