# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 15:45:28 2018
customize the dataframe before writing to Excel
for IRE Angles
@author: Raluca Sandu
"""
import os
import time 
import pandas as pd
import matplotlib.pyplot as plt 

def customize_dataframe(dfAngles, dfPatientsTrajectories, rootdir):
    
    #%% boxplot for angle degrees planned vs validation
    fig, axes = plt.subplots(figsize=(12, 16))
    dfAngles.boxplot(column=['Planned Angle','Validation Angle'], patch_artist=False)
    plt.ylabel('Angle [$^\circ$]')
    #%% convert to dataframe & make columns numerical so Excel operations are allowed
    dfAngles['A_dash'] = '-'
    dfAngles['Electrode Pair'] = dfAngles['NeedleA'].astype(str) + dfAngles['A_dash'] + dfAngles['NeedleB'].astype(str)
    dfAngles = dfAngles[['PatientID', 'LesionNr','Electrode Pair', 'Planned Angle', 'Validation Angle','Distance Planned','Distance Validation']] 
    dfAngles.sort_values(by=['PatientID','Electrode Pair'], inplace=True) 
    dfAngles.apply(pd.to_numeric, errors='ignore', downcast='float').info()
    
    dfPatientsTrajectories.apply(pd.to_numeric, errors='ignore', downcast='float').info()
    
    dfPatientsTrajectories[['LateralError']] = dfPatientsTrajectories[['LateralError']].apply(pd.to_numeric, downcast='float')
    
    dfPatientsTrajectories[['AngularError']] = dfPatientsTrajectories[['AngularError']].apply(pd.to_numeric, downcast='float')
    
    dfPatientsTrajectories[['EuclideanError']] = dfPatientsTrajectories[['EuclideanError']].apply(pd.to_numeric, downcast='float')
    
    dfPatientsTrajectories[['LongitudinalError']] = dfPatientsTrajectories[['LongitudinalError']].apply(pd.to_numeric, downcast='float')
    
    dfPatientsTrajectories.sort_values(by=['PatientID','LesionNr','NeedleNr'],inplace=True)
    
    dfTPEs = dfPatientsTrajectories[['PatientID','LesionNr','NeedleNr','ReferenceNeedle','LongitudinalError',\
                                     'LateralError','EuclideanError','AngularError']]
    
    # select rows where the needle is not a reference, but part of child trajectories
    dfTPEsNoReference = dfTPEs[~(dfTPEs.ReferenceNeedle)]
    
    #%% number of needles
    # question: how many needles (pairs) were used per lesion?
    # grpd_needles = dfTPEs.groupby(['PatientID','NeedleNr']).size().to_frame('Needle Count')
    df_count = dfTPEsNoReference.groupby(['PatientID','LesionNr']).size().to_frame('NeedleCount')
    dfNeedles = dfTPEsNoReference.groupby(['PatientID','LesionNr']).NeedleNr.max().to_frame('TotalNeedles')
    dfNeedlesIndex = dfNeedles.add_suffix('_Count').reset_index()
    
    # question: what is the frequency of the needle configuration (3 paired, 4 paired)
    dfLesionsNeedlePairs = dfNeedlesIndex.groupby(['TotalNeedles_Count']).LesionNr.count()
    dfLesionsIndex = dfLesionsNeedlePairs.add_suffix('_Count').reset_index()
    
    # how many patients & how many lesions
    dfLesionsTotal = dfTPEsNoReference.groupby(['PatientID']).LesionNr.max().to_frame('TotalLesions')
    dfLesionsTotalIndex = dfLesionsTotal.add_suffix('_Count').reset_index()
    #%%  write to Excel File
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = 'IRE_AllPatients-' + timestr + '.xlsx' 
    filepathExcel = os.path.join(rootdir, filename)
    writer = pd.ExcelWriter(filepathExcel)
    dfAngles.to_excel(writer, sheet_name='Angles', index=False, na_rep='NaN')
    dfTPEs.to_excel(writer,sheet_name='TPEs', index=False, na_rep='NaN')
    dfPatientsTrajectories.to_excel(writer,sheet_name='Trajectories', index=False, na_rep='NaN')
    
    # CAS- version: 3) database of needles (extract the type of needle from the plan), check if need to account for offset
    
    