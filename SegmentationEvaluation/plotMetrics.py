# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 16:15:51 2017

@author: Raluca Sandu
"""
import os
import numpy as np
import graphing as gh
import matplotlib.pyplot as plt
from collections import OrderedDict

#%%    
    
def plotBarMetrics(pat_name, pat_idx, rootdir, overlap_results_df, surface_distance_results_df):
    
    # PLOT VOLUME OVERLAP METRICS BAR PLOTS
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
    
    # PLOT SURFACE DISTANCE METRICS BAR PLOTS
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
    
def plotHistDistances(pat_name, pat_idx, rootdir, distanceMap, num_voxels , title):

    ''' PLOT THE HISTOGRAM FOR THE MAUERER DISTANCES'''
#        
    figName_hist = pat_name + 'histogramDistances' + title
    figpathHist = os.path.join(rootdir, figName_hist)
    
    # This is  the colormap I'd like to use.
#    cm = plt.cm.get_cmap('RdYlGn')
#    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    # scale values to interval [0,1]
#    col = bin_centers - min(bin_centers)
#    col /= max(col)
#        plt.setp(p, 'facecolor', cm(c))

    min_val = int(np.floor(min(distanceMap)))
    max_val = int(np.ceil(max(distanceMap)))
    
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(distanceMap, ec='darkgrey', bins=range(min_val,max_val))
    
    
    for c, p in zip(bins, patches):
        if c < 0:
            plt.setp(p, 'facecolor', 'red', label='Non-ablated surface')
        elif c >=0 and c < 5 :
            plt.setp(p, 'facecolor', 'orange', label='Insufficient Margin')
        elif c>=5:
            plt.setp(p, 'facecolor', 'green', label='Sufficient Margin')


    plt.xlabel('[mm]', fontsize=16)
    plt.tick_params(labelsize=16)
    
    yticks, locs = plt.yticks()
    percent = yticks/num_voxels * 100
    percent_2decimals = np.round(percent, 2)
    yticks_percent = [str(x) + '%' for x in percent_2decimals]
    plt.yticks(yticks,yticks_percent)
    plt.ylabel('Percetange of surface voxels', fontsize=16)
    
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), fontsize=16)
    
    
    plt.title('Surface to Surface - Euclidean Distances. Patient ' + str(pat_idx+1), fontsize=18)
    
#    ax.set_yticklabels(percent_format)
    
#    plt.show()
    gh.save(figpathHist, width=12, height=10)
