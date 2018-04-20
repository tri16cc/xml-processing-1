# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 16:36:00 2018

@author: Raluca Sandu
"""

# to do: extract parameters from MWA log files
# output: text file, one lesion per line
# data to be extracted:
'''
    - origin of the tumor mask (x,y,z)
    - spacing of the tumor mask (x,y,z)
    - origin of the ablation (x,y,z)
    - spacing of the ablation mask(x,y,z)
    - needle Target & Entry Point
    - needle TPEs
     ABLATION PARAMETERS :
         - power
         - time
         - predicted ellipse (axes, registration matrix, radius, output: DICOM MASK with same spacing and origin)
    
'''