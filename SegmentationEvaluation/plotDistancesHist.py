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
    
    
def plotHistDistances(pat_name, pat_idx, rootdir, distanceMap, num_voxels , title):

    ''' PLOT THE HISTOGRAM FOR THE MAUERER DISTANCES'''
#        
    figName_hist = pat_name + 'histogramDistances' + title
    figpathHist = os.path.join(rootdir, figName_hist)
    

    min_val = int(np.floor(min(distanceMap)))
    max_val = int(np.ceil(max(distanceMap)))
    
    fig, ax = plt.subplots()
#    n, bins, patches = ax.hist(distanceMap, ec='darkgrey')
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
    
    plt.title('Surface to Surface - Euclidean Distances. Patient ' + str(pat_idx), fontsize=18)
    
    gh.save(figpathHist, width=12, height=10)
