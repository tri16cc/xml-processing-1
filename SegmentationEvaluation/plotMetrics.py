# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 16:15:51 2017

@author: Raluca Sandu
"""
import os
import numpy as np
import pandas as pd
import graphing as gh
import matplotlib.pyplot as plt


    #%% 
class PlotSegmentationMetrics(object):
    
    def __init__(self, pat_name, pat_idx, overlap_results_df, surface_distance_results_df, rootdir):
        
        '''edit axis limits & labels '''
        ''' save plots'''
        figName_vol = pat_name + 'volumeMetrics'
        figpath1 = os.path.join(rootdir, figName_vol)
        fig, ax = plt.subplots()
        dfVolT = overlap_results_df.T

        dfVolT.plot(kind='bar', rot=15, legend=False, ax=ax, grid=True, color='coral')
        plt.axhline(0, color='k')
        plt.ylim((-2.5,2.5))
        plt.tick_params(labelsize=12)
        plt.title('Volumetric Overlap Metrics. Ablation GT vs. Ablation Estimated. Patient ' + str(pat_idx))
        plt.rc('figure', titlesize=25) 
        gh.save(figpath1,width=12, height=10)
        
        # PLOT SURFACE DISTANCE METRICS
        figName_distance = pat_name + 'distanceMetrics'
        figpath2 = os.path.join(rootdir, figName_distance)
        dfDistT = surface_distance_results_df.T

        fig1, ax1 = plt.subplots()
        dfDistT.plot(kind='bar',rot=15, legend=False, ax=ax1, grid=True)
        plt.ylabel('[mm]')
        plt.axhline(0, color='k')
        plt.ylim((0,30))
        plt.title('Surface Distance Metrics. Ablation GT vs. Ablation Estimated. Patient ' + str(pat_idx))
        plt.rc('figure', titlesize=25) 
        plt.tick_params(labelsize=12)
        gh.save(figpath2,width=12, height=10)
        
        #%%
        # PLOT THE HISTOGRAM FOR THE MAUERER DISTANCES
#
#        segmented_surface_float = sitk.GetArrayFromImage(segmented_surface)
#        reference_distance_map_float = sitk.GetArrayFromImage(reference_distance_map)
#        dists_to_plot = segmented_surface_float * reference_distance_map_float
        #        figName_slice = pat_name + 'Slice'
#        figpathSlice = os.path.join(rootdir, figName_slice)
    #    fig2, ax2= plt.subplots()
    #    z = int(np.floor(np.shape(dists_to_plot)[0]/2))
    #    plt.imshow(dists_to_plot[z,:,:]/255)
    #    plt.title(' Distance Map. 1 Slice Visualization. Patient ' + str(idx+1))
    #    plt.rc('figure', titlesize=25) 
    #    gh.save(figpathSlice, width=12, height=10)
    #    
#        figName_hist = pat_name + 'histogramDistances'
#        figpathHist = os.path.join(rootdir, figName_hist)
#        ix = dists_to_plot.nonzero()
#        dists_nonzero = dists_to_plot[ix]
#        fig3, ax3 = plt.subplots()
#        plt.hist(dists_nonzero/255, ec='darkgrey')
#        plt.title('Histogram Mauerer Distances. Patient ' + str(idx+1))
#        plt.rc('figure', titlesize=25) 
#        gh.save(figpathHist, width=12, height=10)
