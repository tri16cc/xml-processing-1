# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 10:32:48 2018

@author: Raluca Sandu
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 19:15:03 2017

@author: Raluca Sandu
"""
import os
import numpy as np
import pandas as pd
import graphing as gh
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from collections import OrderedDict


#plt.style.use('classic')
#plt.style.use('seaborn')
#%%
def plotBoxplots(data, rootdir):

    
    ax1 = plt.subplot(211)
    
    # Horizontal box plot
    bplot = plt.boxplot(data,
                         vert=True,   # vertical box aligmnent
                         patch_artist=False,
                         showmeans=False)   # fill with color
                         
    for element in ['medians','boxes', 'fliers', 'whiskers', 'caps']:
        plt.setp(bplot[element], color='black',linewidth=1.5)
    
    plt.setp(bplot['whiskers'], linestyle='--')
    plt.setp(bplot['fliers'], markersize=5)
                         
    xlim = np.array(plt.gca().get_xlim())
    ylim = np.array(plt.gca().get_ylim())
    plt.fill_between(xlim, y1=([ylim[0],ylim[0]]) , y2=([0, 0]) ,
                     color="#EC7063", zorder=0)
    plt.fill_between(xlim, y1=([0, 0]), y2=([5, 5]) ,
                     color="#FAD7A0", zorder=0)
    plt.fill_between(xlim, y1=([5, 5]), y2=(ylim[1], ylim[1]), 
                     color="#ABEBC6", zorder=0 )
    plt.margins(0)
    
    plt.title('Surface Distance Distribution and Tumor Volume Coverage Ratio. 10 Cases.', fontsize=16)
#    plt.xlabel('Lesion', fontsize=16,color='black')
    plt.tick_params(labelsize=16, color='black')
    plt.ylabel('[mm]', fontsize=16, color='black')
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax1.get_yticklabels(), color='k')
    #%%
    '''plot the second subplot with the volumes'''
    
    ax2 = plt.subplot(212, sharex=ax1)
    # at the moment import the volumes from the excel file
    volumes_df = pd.read_excel('volumetricResults.xlsx')
    ys = 1-volumes_df[' Tumor residual volume to tumor volume  ratio']
    xs = np.arange(1,len(ys)+1,1)
    ax2.scatter(xs, ys, s=200, marker='o',c='steelblue',edgecolors='darkblue')
    plt.setp(ax2.get_xticklabels(), fontsize=16, color='black')
    plt.setp(ax2.get_yticklabels(), fontsize=16, color='black')
    ax2.set_ylim([0, 1.04])
    ax2.set_xlim([0.5,len(ys)+0.5])
    plt.ylabel('Tumour Volume Coverage Ratio', fontsize=16, color='black')
    plt.setp(ax2.get_yticklabels(), color='k')
    plt.xlabel('Case', fontsize=16,color='black')
#    plt.subplots_adjust(wspace=0, hspace=0)
#    figpath = os.path.join(rootdir,'DistanceMapsBoxplots_plus_ScatterPlotVolume.png')
#    plt.show()     
#    gh.save(figpath)                
