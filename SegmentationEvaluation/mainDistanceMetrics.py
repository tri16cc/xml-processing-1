# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 11:43:36 2017

@author: Raluca Sandu
"""
import os
import re
import time
import pandas as pd
import plotHistDistances as pm
import plotBoxplotSurface as bp
from distancesv2 import DistanceMetrics 
from volumemetrics import VolumeMetrics
import distances_boxplots_all_lesions as bpLesions

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
pat_ids = []
#%%
'''define empty structures for storing the data into'''
df_metrics_all = pd.DataFrame()
# define 2 list for positive and negative ranges of distances [in mm] to plot later in boxplots 
pos_bins = [[] for x in range(22)]
neg_bins = [[] for x in range(22)]
# define 4.lists for the following intervals 0:(<-10mm),1:(-10:-5),1:(-5:0),2:(0-5mm),3:(5-10mm),4:(greater than 10 mm) 
bins_4intervals = [[] for x in range(6)]
distanceMaps_allPatients =[]
#%%
'''iterate through the lesions&ablations segmentations; plot the histogram of distance'''
    # set-up the flags wether one wants symmetrics distances or from Ablation2Tumor/Tumor2Ablation
    # default value: distance Ablation2Tumor surface contour (flag_mask2reference=True)
    
for idx, seg in enumerate(reference):
    
    evalmetrics = DistanceMetrics(ablations[idx],reference[idx], flag_symmetric=False, flag_mask2reference=True, flag_reference2mask=False)
    evaloverlap = VolumeMetrics(ablations[idx],reference[idx])
    df_distances_1set = evalmetrics.get_Distances()
    df_volumes_1set = evaloverlap.get_VolumeMetrics()
    df_metrics = pd.concat([df_volumes_1set, df_distances_1set], axis=1)
    df_metrics_all = df_metrics_all.append(df_metrics)

    distanceMap_seg2ref = evalmetrics.get_seg2ref_distances()
    distanceMaps_allPatients.append(distanceMap_seg2ref)
    n2 = evalmetrics.num_reference_surface_pixels
    title = 'ablation2tumor'

    
    #%%
    '''extract the patient id from the folder/file path'''
    # where pats[idx] contains the name of the folder
    # and pat_id is extrated from the folder path, find the numeric index written in the folder/file path, assume that is the "true" patient ID
    try:
        pat_id_str = re.findall('\\d+', pats[idx])
        pat_id = int(pat_id_str[0])
        pat_ids.append(pat_id)
    except ValueError:
        print('numeric data not found in the file name')
        
    cols_val, bins = pm.plotHistDistances(pats[idx], pat_id, rootdir,  distanceMap_seg2ref, n2, title)
    #%% 
    '''count the percentage of the bins between ranges; plot them wrt surface covered [%]'''
    # 1.iterate through bins. 2for each item in bins add it to new_list[item]+=cols_val
    # careful with negative and positive list
    percent_cols = cols_val/n2 * 100 # change to percentage by dividing each columb by the numbers of voxels on the contour (and in the DistanceMap) 
    
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
    bins_smallerthan_minus10 = 0
    bins_minus10_minus5 = 0
    bins_minus5_0 = 0
    bins_0_5 = 0
    bins_5_10 = 0
    bins_greaterthan10 = 0
         
    for idx, item in enumerate(bins[:-1]):
        
        if item < -10:
            bins_smallerthan_minus10 += percent_cols[idx]
        
        if item >= -10 and item <= -5:
            bins_minus10_minus5 += percent_cols[idx]
            
        if item > -5 and item <= 0:
            bins_minus5_0 += percent_cols[idx]
  
        if item > 0 and item < 5 :
            bins_0_5 += percent_cols[idx]
            
        if item >= 5 and item <= 10:
            bins_5_10 += percent_cols[idx]
   
        elif item > 10:
            bins_greaterthan10 += percent_cols[idx]

    bins_4intervals[0].append(bins_smallerthan_minus10)  
    bins_4intervals[1].append(bins_minus10_minus5)    
    bins_4intervals[2].append(bins_minus5_0)  
    bins_4intervals[3].append(bins_0_5)
    bins_4intervals[4].append(bins_5_10)
    bins_4intervals[5].append(bins_greaterthan10)

bp.plotBinsSurfacePercentage(bins_4intervals, rootdir, flag_all_ranges=False)
bp.plotBinsSurfacePercentage(posneg_bins, rootdir, flag_all_ranges=True)

#%%
'''plot boxplots of the distanceMaps for each lesion'''
# sort rows ascending based on pat_id
df_patientdata['PatientID']  = pat_ids
df_patientdata['DistanceMaps'] = distanceMaps_allPatients
df_patients_sorted = df_patientdata.sort_values(['PatientID'], ascending=True)
data_toplot = df_patients_sorted['DistanceMaps'].tolist()
bpLesions.plotBoxplots(data_toplot, rootdir)
#%% 
''' save to excel the average of the distance metrics '''
df_metrics_all.index = list(range(len(df_metrics_all)))
df_final = pd.concat([df_patientdata, df_metrics_all], axis=1)
timestr = time.strftime("%H%M%S-%Y%m%d")
filename = 'DistanceVolumeMetrics_Pooled_' + timestr +'.xlsx'
filepathExcel = os.path.join(rootdir, filename )
writer = pd.ExcelWriter(filepathExcel)
df_final.to_excel(writer, index=False, float_format='%.2f')
