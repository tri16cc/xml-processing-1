# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 10:36:31 2017

@author: Raluca Sandu
"""
import numpy as np
from matplotlib import pyplot as plt
#from IPython import display
#plt.set_cmap('gray')
#%matplotlib inline

import scipy
import scipy.misc
IMG_DTYPE = np.float
SEG_DTYPE = np.uint8

import dicom
import SimpleITK as sitk
import natsort
import glob, os
import re

#%%
image = dicom.read_file("lesion_mask")

image_itk = sitk.ReadImage("lesion_mask", sitk.sitkUInt8)

ConstPixelDims = (int(image.Rows), int(image.Columns), int(image.NumberOfFrames))
ArrayDicom = np.zeros(ConstPixelDims, dtype=image.pixel_array.dtype)

interact(display_with_overlay, segmentation_number=(0,len(segmentation)-1), 
         slice_number = (0, image.GetSize()[1]-1), image = fixed(image),
         segs = fixed(segmentation), window_min = fixed(-1024), window_max=fixed(976));