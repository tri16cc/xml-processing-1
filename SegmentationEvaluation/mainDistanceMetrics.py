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
import plotDistancesHist as pm
import distances_boxplots as bp
#%%
#plt.style.use('ggplot')
#plt.style.use('classic')
#print(plt.style.available)

segmentation_data = [] # list of dictionaries containing the filepaths of the segmentations
#rootdir = "Z:/Public/Raluca&Radek/studyPatientsMasks/GroundTruthDB_ROI/"
rootdir = "C:/Users/Raluca Sandu/Documents/LiverInterventionsBern_Ablations/studyPatientsMasks/"

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
pos_bins = [[] for x in range(25)]
neg_bins = [[] for x in range(25)]

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
    # lame attempt of plotting boxplots
    min_val = int(np.floor(min(distanceMap_seg2ref)))
    max_val = int(np.ceil(max(distanceMap_seg2ref)))
    fig, ax = plt.subplots()
    cols_val, bins, patches = ax.hist(distanceMap_seg2ref, ec='darkgrey', bins=range(min_val,max_val))
    percent_cols = cols_val/n2 * 100
    plt.close()
    #%% 
    # define dictionary of range values
    # do it with lists
    # 1.iterate through bins. 2for each item in bins add it to new_list[item]+=cols_val
    # careful with negative and positive list

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
'''plot boxplots per range of mm versus percentage of surface covered - all patients'''
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


labels_neg = ['(-'+ str(x-1)+':-'+str(x)+')' for x in range(24,0,-1)]
labels_neg[23] = '(-1:0)'
labels_pos = ['('+ str(x-1)+':'+str(x)+')' for x in range(1,26)]
xticklabels = labels_neg+labels_pos
#xticklabels[0] = ''
xtickNames = plt.setp(axes, xticklabels=xticklabels)
plt.setp(xtickNames, rotation=45, fontsize=10)
axes.set_xlim([1, 40])
axes.set_ylim([-1, 20])
plt.xlabel('Range of Distances [mm]')
plt.ylabel('Tumor Surface covered')
#%% Write to excel

#''' save to excel '''
df_metrics_all.index = list(range(len(df_metrics_all)))
df_final = pd.concat([df_patientdata, df_metrics_all], axis=1)
timestr = time.strftime("%H%M%S-%Y%m%d")
filename = 'DistanceVolumeMetrics_Pooled_' + timestr +'.xlsx'
filepathExcel = os.path.join(rootdir, filename )
writer = pd.ExcelWriter(filepathExcel)
df_final.to_excel(writer, index=False, float_format='%.2f')
