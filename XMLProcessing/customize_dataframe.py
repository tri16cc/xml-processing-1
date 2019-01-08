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
    # %% boxplot for angle degrees planned vs validation
    fig, axes = plt.subplots(figsize=(18, 20))
    dfAngles.boxplot(column=['Planned Angle', 'Validation Angle'], patch_artist=False, fontsize=20)
    plt.ylabel('Angle [$^\circ$]', fontsize=20)
    # plt.show()
    savepath_png = os.path.join(rootdir, 'IRE_Angles.png')
    savepath_svg = os.path.join(rootdir, 'IRE_Angles.svg')
    plt.savefig(savepath_png, pad_inches=0)
    plt.savefig(savepath_svg, pad_inches=0)
    # %% convert to dataframe & make columns numerical so Excel operations are allowed
    dfAngles['A_dash'] = '-'
    dfAngles['Electrode Pair'] = dfAngles['NeedleA'].astype(str) + dfAngles['A_dash'] + dfAngles['NeedleB'].astype(str)
    dfAngles = dfAngles[['PatientID', 'LesionNr', 'Electrode Pair', 'Planned Angle', 'Validation Angle']]
    dfAngles.sort_values(by=['PatientID', 'LesionNr'], inplace=True)
    dfAngles.apply(pd.to_numeric, errors='ignore', downcast='float').info()
    # dfAngles_no_nans = dfAngles.dropna(subset=['Validation Angle'], inplace=True)

    # %%
    dfPatientsTrajectories.apply(pd.to_numeric, errors='ignore', downcast='float').info()

    dfPatientsTrajectories[['LateralError']] = dfPatientsTrajectories[['LateralError']].apply(pd.to_numeric,
                                                                                              downcast='float')
    dfPatientsTrajectories.LateralError = dfPatientsTrajectories.LateralError.round(decimals=2)

    dfPatientsTrajectories[['EntryLateral']] = dfPatientsTrajectories[['EntryLateral']].apply(pd.to_numeric,
                                                                                              downcast='float')
    dfPatientsTrajectories.EntryLateral = dfPatientsTrajectories.EntryLateral.round(decimals=2)

    dfPatientsTrajectories[['AngularError']] = dfPatientsTrajectories[['AngularError']].apply(pd.to_numeric,
                                                                                              downcast='float')
    dfPatientsTrajectories.AngularError = dfPatientsTrajectories.AngularError.round(decimals=2)

    dfPatientsTrajectories[['EuclideanError']] = dfPatientsTrajectories[['EuclideanError']].apply(pd.to_numeric,
                                                                                                  downcast='float')
    dfPatientsTrajectories.EuclideanError = dfPatientsTrajectories.EuclideanError.round(decimals=2)

    dfPatientsTrajectories[['LongitudinalError']] = dfPatientsTrajectories[['LongitudinalError']].apply(pd.to_numeric,
                                                                                                        downcast='float')
    dfPatientsTrajectories.LongitudinalError = dfPatientsTrajectories.LongitudinalError.round(decimals=2)

    dfPatientsTrajectories.sort_values(by=['PatientID', 'LesionNr', 'NeedleNr'], inplace=True)

    dfTPEs = dfPatientsTrajectories[['PatientID', 'PatientName', 'LesionNr', 'NeedleNr', 'NeedleType',
                                     'TimeIntervention', 'ReferenceNeedle', 'EntryLateral',
                                     'LongitudinalError', 'LateralError', 'EuclideanError', 'AngularError']]
    # drop NaNs if there are any and just count those (?)
    # todo: check how the excel looks like with and without dropping the NaNs
    dfTPEs.dropna(subset=['EuclideanError'],
                  inplace=True)  # Keep the DataFrame with valid entries in the same variable.
    # select only IRE Needles, drop the MWAs
    dfIREs = dfTPEs[dfTPEs.NeedleType == 'IRE']
    # select rows where the needle is not a reference, but part of child trajectories. drop the other rows
    df_IRE_TPEs_NoReference = dfIREs[~(dfIREs.ReferenceNeedle)]
    # %%
    patient_unique = df_IRE_TPEs_NoReference['PatientID'].unique()
    for PatientIdx, patient in enumerate(patient_unique):
        patient_data = df_IRE_TPEs_NoReference[df_IRE_TPEs_NoReference['PatientID'] == patient]
        lesion_unique = patient_data['LesionNr'].unique()
        list_lesion_count_new = []
        NeedleCount = patient_data['NeedleNr'].tolist()
        new_idx_lesion = 1

        # update needle nr count for older CAS versions where no reference needle was available
        for l_idx, lesion in enumerate(lesion_unique):
            lesion_data = patient_data[patient_data['LesionNr'] == lesion]
            needles_new = lesion_data['NeedleNr'] + 1
            # if df_IRE_only still has needles starting with 0 add 1 to all the columns
            if lesion_data.NeedleNr.iloc[0] == 0:
                df_IRE_TPEs_NoReference.loc[
                    (df_IRE_TPEs_NoReference['PatientID'] == patient) & (df_IRE_TPEs_NoReference['LesionNr'] == lesion),
                    ['NeedleNr']] = needles_new

        # update lesion count (per patient) after keeping only the IRE needles
        for needle_idx, needle in enumerate(NeedleCount):
            if needle_idx == 0:
                list_lesion_count_new.append(new_idx_lesion)
            else:
                if NeedleCount[needle_idx] <= NeedleCount[needle_idx - 1]:
                    new_idx_lesion += 1
                    list_lesion_count_new.append(new_idx_lesion)
                else:
                    list_lesion_count_new.append(new_idx_lesion)

        df_IRE_TPEs_NoReference.loc[
            (df_IRE_TPEs_NoReference['PatientID'] == patient), ['LesionNr']] = list_lesion_count_new
                # lesion_data['NeedleNr'] = patient_data['NeedleNr'].apply(lambda x: x + 1)
                # df_IRE_TPEs_NoReference['NeedleNr'].apply(lambda y: y + 1 if (
                #         df_IRE_TPEs_NoReference['PatientID'] == patient and df_IRE_TPEs_NoReference[
                #     'LesionNr'] == lesion) else print(''))
                # df_IRE_TPEs_NoReference.loc[df_IRE_TPEs_NoReference['PatientID']==patient, ['NeedleNr']]= 'aaa'
                # df_IRE_TPEs_NoReference[['PatientID']] = df_IRE_TPEs_NoReference['PatientID'].astype(str)
                # df_IRE_TPEs_NoReference[['LesionNr']] = df_IRE_TPEs_NoReference['LesionNr'].astype(str)
                # df_IRE_TPEs_NoReference.loc[(df_IRE_TPEs_NoReference['PatientID'] == str(patient)) & df_IRE_TPEs_NoReference['LesionNr'] == lesion].apply(lambda x: x+1)
                # df_IRE_TPEs_NoReference[df_IRE_TPEs_NoReference['PatientID'] == patient and df_IRE_TPEs_NoReference['LesionNr'] == lesion].NeedleNr.apply(lambda x: x+1)

    # %% Group statistics

    # grpd_needles = dfTPEs.groupby(['PatientID','NeedleNr']).size().to_frame('Needle Count')
    # df_count = df_IRE_only.groupby(['PatientID','LesionNr']).size().to_frame('NeedleCount')

    # question: how many needles (pairs) were used per lesion?
    dfNeedles = df_IRE_TPEs_NoReference.groupby(['PatientID', 'LesionNr']).NeedleNr.size().to_frame('TotalNeedles')
    dfNeedlesIndex = dfNeedles.add_suffix('_Count').reset_index()

    # question: what is the frequency of the needle configuration (3 paired, 4 paired) ?
    dfLesionsNeedlePairs = dfNeedlesIndex.groupby(['TotalNeedles_Count']).LesionNr.count()
    dfLesionsIndex = dfLesionsNeedlePairs.add_suffix('-Paired').reset_index()

    # how many patients & how many lesions ?
    dfLesionsTotal = df_IRE_TPEs_NoReference.groupby(['PatientID']).LesionNr.max().to_frame('Total Lesions')
    dfLesionsTotalIndex = dfLesionsTotal.add_suffix(' Count').reset_index()
    # %%  write to Excel File
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = 'IRE_Analysis_Statistics-' + timestr + '.xlsx'
    filepathExcel = os.path.join(rootdir, filename)
    writer = pd.ExcelWriter(filepathExcel)
    dfLesionsTotalIndex.to_excel(writer, sheet_name='LesionsTotal', index=False, na_rep='Nan')
    dfNeedlesIndex.to_excel(writer, sheet_name='NeedlesLesion', index=False, na_rep='Nan')
    dfLesionsIndex.to_excel(writer, sheet_name='NeedleFreq', index=False, na_rep='Nan')
    # if dfAngles_no_nans is not None:
    #     dfAngles_no_nans.to_excel(writer, sheet_name='Angles', index=False, na_rep='Nan')
    dfAngles.to_excel(writer, sheet_name='Angles', index=False, na_rep='NaN')
    df_IRE_TPEs_NoReference.to_excel(writer, sheet_name='TPE_IREs', index=False, na_rep='NaN')
    dfTPEs.to_excel(writer, sheet_name='TPEs', index=False, na_rep='NaN')
    dfPatientsTrajectories.to_excel(writer, sheet_name='Trajectories', index=False, na_rep='NaN')
    writer.save()
