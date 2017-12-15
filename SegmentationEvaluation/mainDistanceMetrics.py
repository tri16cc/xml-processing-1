# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 11:43:36 2017

@author: Raluca Sandu
"""
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from distancesv2 import DistanceMetrics 
from volumemetrics import VolumeMetrics
from collections import OrderedDict
import plotDistancesHist as pm
#import distances_boxplots as bp
#%%
#plt.style.use('ggplot')
#plt.style.use('classic')
#print(plt.style.available)

segmentation_data = [] # list of dictionaries containing the filepaths of the segmentations
rootdir = "Z:/Public/Raluca&Radek/studyPatientsMasks/GroundTruthDB_ROI/"
#rootdir = "C:/Users/Raluca Sandu/Documents/LiverInterventionsBern_Ablations/studyPatientsMasks/"

for subdir, dirs, files in os.walk(rootdir):
    tumorFilePath  = ''
    ablationSegm = ''
    for file in files:
        if file == "tumorSegm":
            FilePathName = os.path.join(subdir, file)
            tumorFilePath = os.path.normpath(FilePathName)
        elif file == "ablationSegm":
            FilePathName = os.path.join(subdir, file)
            ablationFilePath = os.path.normpath(FilePathName)
        else:
            print("")
        
    if (tumorFilePath) and (ablationFilePath):
        dir_name = os.path.dirname(ablationFilePath)
        dirname2 = os.path.split(dir_name)[1]
        data = {'PatientName' : dirname2,
                'TumorFile' : tumorFilePath,
                'AblationFile' : ablationFilePath
                }
        segmentation_data.append(data)  

# convert to data frame 
df_patientdata = pd.DataFrame(segmentation_data)
df_metrics = pd.DataFrame() # emtpy dataframe to append the segmentation metrics calculated

ablations = df_patientdata['AblationFile'].tolist()
reference = df_patientdata['TumorFile'].tolist()
pats = df_patientdata['PatientName']
#%%
df_metrics_all = pd.DataFrame()
distaceMaps_all = []
# define 2 list for positive and negative ranges of distances [in mm] to plot later in boxplots 
pos_bins = [[] for x in range(22)]
neg_bins = [[] for x in range(22)]
# define 4.lists for the following intervals 0:(<-5mm),1:(-5:0),2:(0-5mm),3:(5-10mm),4:(greater than 10 mm) 
bins_4intervals = [[] for x in range(5)]

for idx, seg in enumerate(reference):
    # set-up the flags wether one wants symmetrics distances or from Ablation2Tumor/Tumor2Ablation
    # default value: distance Ablation2Tumor surface contour
    evalmetrics = DistanceMetrics(ablations[idx],reference[idx], flag_symmetric=False, flag_mask2reference=False, flag_reference2mask=True)
    evaloverlap = VolumeMetrics(ablations[idx],reference[idx])
    df_distances_1set = evalmetrics.get_Distances()
    df_volumes_1set = evaloverlap.get_VolumeMetrics()
    df_metrics = pd.concat([df_volumes_1set, df_distances_1set], axis=1)
    df_metrics_all = df_metrics_all.append(df_metrics)

    distanceMap_seg2ref = evalmetrics.get_seg2ref_distances()
    distaceMaps_all.append(distanceMap_seg2ref)
    n2 = evalmetrics.num_reference_surface_pixels
    title = 'ablation2tumor'
    
    pm.plotHistDistances(pats[idx], idx, rootdir,  distanceMap_seg2ref, n2, title)
  
    #%% 
    '''plot the histograms in order to save the bins and plot them wrt surface covered [%]'''
    # 1.iterate through bins. 2for each item in bins add it to new_list[item]+=cols_val
    # careful with negative and positive list

    min_val = int(np.floor(min(distanceMap_seg2ref)))
    max_val = int(np.ceil(max(distanceMap_seg2ref)))
    fig, ax = plt.subplots()
    cols_val, bins, patches = ax.hist(distanceMap_seg2ref, ec='darkgrey', bins=range(min_val,max_val))
    percent_cols = cols_val/n2 * 100
    plt.close()
    
    for idx, item in enumerate(bins[:-1]):
        #use the idx to relate to the values of the columns
        if item>=0:
            pos_bins[item].append(percent_cols[idx])
        elif item<0:
            neg_bins[abs(item)].append(percent_cols[idx])
        # append to lists
    neg_bins.reverse()
    posneg_bins =  neg_bins[:-1]+ pos_bins 
#%%
    '''sum the bins for specific intervals (eg.0-5,5-10) of each patient then add them to a list for ranges'''   
    bins_smallerthan5 = 0
    bins_5_0 = 0
    bins_1_5 = 0
    bins_5_10 = 0
    bins_greaterthan10 = 0
         
    for idx, item in enumerate(bins[:-1]):
        if item < -5:
            bins_smallerthan5 += percent_cols[idx]
            
        if item >=-5 and item <0:
            bins_5_0 += percent_cols[idx]
  
        if item>=0 and item <=5:
            bins_1_5 += percent_cols[idx]
            
        elif item > 5 and item <= 10:
            bins_5_10 += percent_cols[idx]
   
        elif item > 10:
            bins_greaterthan10 += percent_cols[idx]

    bins_4intervals[0].append(bins_smallerthan5)  
    bins_4intervals[1].append(bins_5_0)    
    bins_4intervals[2].append(bins_1_5)   
    bins_4intervals[3].append(bins_5_10)  
    bins_4intervals[4].append(bins_greaterthan10)

#%% 
'''plot boxplots per range of mm versus percentage of surface covered - all patients'''
 # lame attempt of plotting boxplots
 # 1. plot boxplot for each discrete range (0-1), (1-0)
 # 2. plot boxplot for category (greater than -5) (-5-0mm)  (0-5mm) (5-10mm) (greater than 10mm)
fig, axes = plt.subplots(figsize=(12, 16))    
# Horizontal box plot
bplot = plt.boxplot(posneg_bins,
                     vert=True,   # vertical box aligmnent
                     patch_artist=False,
                     showmeans=True)   # fill with color
                    
# set the axes ranges and the names

plt.setp(bplot['whiskers'], linestyle='--')
plt.setp(bplot['fliers'], markersize=5)
plt.setp(bplot['means'], marker='D', markeredgecolor='black',
                  markerfacecolor='blue', label='Mean')

axes.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)

axes.set_axisbelow(True)
ax.set_aspect(0.1) 
labels_neg = ['(-'+ str(x-1)+':-'+str(x)+')' for x in range(21,0,-1)]
labels_neg[20] = '(-1:0)'
labels_pos = ['('+ str(x-1)+':'+str(x)+')' for x in range(1,22)]
xticklabels = labels_neg+labels_pos
xtickNames = plt.setp(axes, xticklabels=xticklabels)
plt.setp(xtickNames, rotation=45, fontsize=10)
#axes.set_xlim([1, 40])
#axes.set_ylim([-1, 15])
plt.xlabel('Range of Distances [mm]', fontsize=14)
plt.ylabel('Percentage of Tumor surface covered by Ablation [%]', fontsize=14)

#%%
'''plot boxplots 4intervals'''
fig, ax = plt.subplots(figsize=(12, 16))    
bplot = plt.boxplot( bins_4intervals,
                     vert=True,   # vertical box aligmnent
                     patch_artist=True,# fill with color
                     showmeans=True)   # show the means
    

plt.setp(bplot['medians'], color='black',linewidth=1.5)                        
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)
plt.setp(bplot['means'], marker='D', markeredgecolor='darkred',
                  markerfacecolor='darkred', label='Mean')
ax.set_axisbelow(True)
#ax.set_aspect(0.1) 
#set the xTickLabels
#0:(<-5mm),1:(-5:0),2:(0-5mm),3:(5-10mm),4:(greater than 10 mm) 
labels = [ r"$(\infty< x < -5$)",r"$(-5 \leqslant x < 0$)", r"$(0  \leqslant x   \leqslant 5$)",r"$(5< x  \leqslant 10)$",r"$(10 < )$"]
xtickNames = plt.setp(ax, xticklabels=labels)
plt.setp(xtickNames, fontsize=12)

plt.xlabel('Range of Distances [mm]', fontsize=12)
plt.ylabel('Percentage of Tumor surface covered by Ablation [%]', fontsize=12)

handles, labels = plt.gca().get_legend_handles_labels()
by_label = OrderedDict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), fontsize=12)
#ax.set_ylim([-1, 20])

#%% 
''' save to excel the average of the distance metrics '''
df_metrics_all.index = list(range(len(df_metrics_all)))
df_final = pd.concat([df_patientdata, df_metrics_all], axis=1)
timestr = time.strftime("%H%M%S-%Y%m%d")
filename = 'DistanceVolumeMetrics_Pooled_' + timestr +'.xlsx'
filepathExcel = os.path.join(rootdir, filename )
writer = pd.ExcelWriter(filepathExcel)
df_final.to_excel(writer, index=False, float_format='%.2f')
