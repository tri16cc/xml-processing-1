# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 17:11:54 2017

@author: Raluca Sandu
"""

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
#%%



def plotNeedles3D(epNeedle1,tpNeedle1):

#        vector1 = TargetPoint-EntryPoint
#        vector2 = TargetPoint-EntryPoint

    epNeedle1_xyz = np.array([float(i) for i in epNeedle1.split()])
    tpNeedle1_xyz = np.array([float(i) for i in tpNeedle1.split()])
    
#    epNeedle2_xyz = np.array([float(i) for i in epNeedle2.split()])
#    tpNeedle2_xyz = np.array([float(i) for i in tpNeedle2.split()])
    x,y,z = zip(epNeedle1_xyz)
    u,v,w = zip(tpNeedle1_xyz)
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True)
    
    plt.show()