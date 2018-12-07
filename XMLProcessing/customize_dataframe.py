# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 15:45:28 2018
customize the dataframe before writing to Excel
for IRE Angles
@author: Raluca Sandu
"""
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.options.display.float_format = '{:.2f}'.format

def customize_dataframe(dfAngles, dfPatientsTrajectories, rootdir):
    
    #%% boxplot for angle degrees planned vs validation
    fig, axes = plt.subplots(figsize=(18, 20))
    dfAngles.boxplot(column=['Planned Angle', 'Validation Angle'], patch_artist=False, fontsize=20)
    plt.ylabel('Angle [$^\circ$]', fontsize=20)
    # plt.show()
    savepath_png = os.path.join(rootdir, 'IRE_Angles.png')
    savepath_svg = os.path.join(rootdir, 'IRE_Angles.svg')
    plt.savefig(savepath_png, pad_inches=0)
    plt.savefig(savepath_svg, pad_inches=0)
    #%% convert to dataframe & make columns numerical so Excel operations are allowed
    dfAngles['A_dash'] = '-'
    dfAngles['Electrode Pair'] = dfAngles['NeedleA'].astype(str) + dfAngles['A_dash'] + dfAngles['NeedleB'].astype(str)
    dfAngles = dfAngles[['PatientID', 'LesionNr','Electrode Pair', 'Planned Angle', 'Validation Angle']]
    dfAngles.sort_values(by=['PatientID','LesionNr'], inplace=True)
    dfAngles.apply(pd.to_numeric, errors='ignore', downcast='float').info()
    
    dfPatientsTrajectories.apply(pd.to_numeric, errors='ignore', downcast='float').info()
    # df.value1 = df.value1.round()

    dfPatientsTrajectories[['LateralError']] = dfPatientsTrajectories[['LateralError']].apply(pd.to_numeric, downcast='float')
    dfPatientsTrajectories.LateralError = dfPatientsTrajectories.LateralError.round(decimals=2)

    dfPatientsTrajectories[['EntryLateral']] = dfPatientsTrajectories[['EntryLateral']].apply(pd.to_numeric, downcast='float')
    dfPatientsTrajectories.EntryLateral = dfPatientsTrajectories.EntryLateral.round(decimals=2)
    
    dfPatientsTrajectories[['AngularError']] = dfPatientsTrajectories[['AngularError']].apply(pd.to_numeric, downcast='float')
    dfPatientsTrajectories.AngularError = dfPatientsTrajectories.AngularError.round(decimals=2)
    
    dfPatientsTrajectories[['EuclideanError']] = dfPatientsTrajectories[['EuclideanError']].apply(pd.to_numeric, downcast='float')
    dfPatientsTrajectories.EuclideanError = dfPatientsTrajectories.EuclideanError.round(decimals=2)
    
    dfPatientsTrajectories[['LongitudinalError']] = dfPatientsTrajectories[['LongitudinalError']].apply(pd.to_numeric, downcast='float')
    dfPatientsTrajectories.LongitudinalError = dfPatientsTrajectories.LongitudinalError.round(decimals=2)

    # dfPatientsTrajectories[['PlannedNeedleLength']] = dfPatientsTrajectories[['PlannedNeedleLength']].apply(pd.to_numeric, downcast='float')
    # dfPatientsTrajectories.PlannedNeedleLength = dfPatientsTrajectories.round(decimals=2)

    dfPatientsTrajectories.sort_values(by=['PatientID','LesionNr','NeedleNr'],inplace=True)

    dfTPEs = dfPatientsTrajectories[['PatientID','PatientName', 'LesionNr','NeedleNr', 'NeedleType',
                                     'TimeIntervention', 'ReferenceNeedle','EntryLateral',
                                     'LongitudinalError', 'LateralError','EuclideanError','AngularError']]

    dfTPEs.dropna(subset=['EuclideanError'], inplace=True) # Keep the DataFrame with valid entries in the same variable.

    dfTPEs = dfTPEs[dfTPEs.NeedleType == 'IRE']

    # select rows where the needle is not a reference, but part of child trajectories
    dfTPEsNoReference = dfTPEs[~(dfTPEs.ReferenceNeedle)]
    # select IRE rows, drop the MWAs
    df_IRE_only = dfTPEsNoReference[dfTPEsNoReference.NeedleType == 'IRE']

    #%% Group statistics

    # grpd_needles = dfTPEs.groupby(['PatientID','NeedleNr']).size().to_frame('Needle Count')
    # df_count = df_IRE_only.groupby(['PatientID','LesionNr']).size().to_frame('NeedleCount')

    # question: how many needles (pairs) were used per lesion?
    dfNeedles = df_IRE_only.groupby(['PatientID','LesionNr']).NeedleNr.size().to_frame('TotalNeedles')
    dfNeedlesIndex = dfNeedles.add_suffix('_Count').reset_index()
    
    # question: what is the frequency of the needle configuration (3 paired, 4 paired) ?
    dfLesionsNeedlePairs = dfNeedlesIndex.groupby(['TotalNeedles_Count']).LesionNr.count()
    dfLesionsIndex = dfLesionsNeedlePairs.add_suffix('-Paired').reset_index()
    
    # how many patients & how many lesions ?
    dfLesionsTotal = df_IRE_only.groupby(['PatientID']).LesionNr.max().to_frame('Total Lesions')
    dfLesionsTotalIndex = dfLesionsTotal.add_suffix(' Count').reset_index()
    #%%  write to Excel File
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = 'IRE_Analysis_Statistics-' + timestr + '.xlsx'
    filepathExcel = os.path.join(rootdir, filename)
    writer = pd.ExcelWriter(filepathExcel)
    dfLesionsTotalIndex.to_excel(writer, sheet_name='LesionsTotal', index=False, na_rep='Nan')
    dfNeedlesIndex.to_excel(writer, sheet_name='NeedlesLesion', index=False, na_rep='Nan')
    dfLesionsIndex.to_excel(writer, sheet_name='NeedleFreq', index=False, na_rep='Nan')
    dfAngles.to_excel(writer, sheet_name='Angles', index=False, na_rep='NaN')
    dfTPEs.to_excel(writer, sheet_name='TPEs', index=False, na_rep='NaN')
    dfPatientsTrajectories.to_excel(writer,sheet_name='Trajectories', index=False, na_rep='NaN')
    writer.save()
    

    
    