# -*- coding: utf-8 -*-imp
"""
Created on Mon Aug 28 10:08:30 2017

@author: Raluca Sandu
"""

from skimage import io
import nibabel as nib
import numpy as np
import sys

print(sys.argv)

infile = sys.argv[1] # 'LW_0009935045_0000010.tif'
outfile = sys.argv[2] #'test.nii'

img = io.imread(infile)
print('read file')
imgfile = nib.Nifti1Image(img, np.eye(4))
print('saving file')
imgfile.to_filename(outfile)
print('finished')