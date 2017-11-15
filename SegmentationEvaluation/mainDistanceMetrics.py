# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 11:43:36 2017

@author: Raluca Sandu
"""
import os
import time
import pandas as pd
from distances import DistanceMetrics 
from volumemetrics import VolumeMetrics

#plt.style.use('ggplot')
#plt.style.use('classic')
#print(plt.style.available)

segmentation_data = [] # list of dictionaries containing the filepaths of the segmentations

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
segmentations = df_patientdata['TumorFile'].tolist()
pats = df_patientdata['PatientName']
#%%
df_metrics_all = pd.DataFrame()

for idx, seg in enumerate(segmentations):
    evalmetrics = DistanceMetrics(ablations[idx],seg)
    evaloverlap = VolumeMetrics(ablations[idx],seg)
    df_distances_1set = evalmetrics.get_Distances()
    df_volumes_1set = evaloverlap.get_VolumeMetrics()
    df_metrics = pd.concat([df_volumes_1set, df_distances_1set], axis=1)
    df_metrics_all = df_metrics_all.append(df_metrics)
    

#%% Write to excel

''' save to excel '''
df_metrics_all.index = list(range(len(df_metrics_all)))
df_final = pd.concat([df_patientdata, df_metrics], axis=1)
timestr = time.strftime("%Y%m%d-%H%M%S")
filename = 'DistanceVolumeMetrics_Pooled' + timestr +'.xlsx'
filepathExcel = os.path.join(rootdir, filename )
writer = pd.ExcelWriter(filepathExcel)
df_final.to_excel(writer, index=False, float_format='%.2f')
