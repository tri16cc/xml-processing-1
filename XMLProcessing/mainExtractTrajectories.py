# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:49:22 2018

@author: Raluca Sandu
"""
import os
from time import strftime
import pandas as pd
import NeedlesInfoClass
import parseIREtrajectories
import extractTrajectoriesAngles as eta
from customize_dataframe import customize_dataframe
# %%
rootdir = r"C:\PatientDatasets_GroundTruth_Database\Stockholm\3d_segmentation_maverric\maveric"
# rootdir = r"C:\Patients_Cochlea\Datsets_Fabrice_processed"
#rootdir = r"C:\PatientDatasets_GroundTruth_Database\Stockholm\3d_segmentation_maverric\maveric"

patientsRepo = NeedlesInfoClass.PatientRepo()
pat_ids = []
pat_id = 0

for subdir, dirs, files in os.walk(rootdir):

    for file in files:
        fileName, fileExtension = os.path.splitext(file)

        if fileExtension.lower().endswith('.xml') and (
                'validation' in fileName.lower() or 'plan' in fileName.lower()):
            xmlFilePathName = os.path.join(subdir, file)
            xmlfilename = os.path.normpath(xmlFilePathName)

            xmlobj = parseIREtrajectories.I_parseRecordingXML(xmlfilename)

            if xmlobj is 1:
                # file was re-written of weird characters so we need to re-open it.
                xmlobj = parseIREtrajectories.I_parseRecordingXML(xmlfilename)
            if xmlobj is not None and xmlobj!=1:
                pat_id = xmlobj.patient_id_xml
                pat_ids.append(pat_id)
                # parse trajectories and other patient specific info
                trajectories_info = parseIREtrajectories.II_parseTrajectories(xmlobj.trajectories)
                if trajectories_info.trajectories is None:
                    continue # no trajectories found in this xml, go on to the next file.
                else:
                    # check if patient exists first, if yes, instantiate new object, otherwise retrieve it from list
                    patients = patientsRepo.getPatients()
                    patient = [x for x in patients if x.patient_id_xml == pat_id]
                    if not patient:
                        # create patient measurements if patient is not already in the PatientsRepository
                        patient = patientsRepo.addNewPatient(pat_id,
                                                             xmlobj.patient_name)
                        parseIREtrajectories.III_parseTrajectory(trajectories_info.trajectories, patient,
                                                                 trajectories_info.series, xmlfilename,
                                                                 trajectories_info.time_intervention,
                                                                 trajectories_info.cas_version)
                    else:
                        # update patient measurements in the PatientsRepository if the patient (id) already exists
                        # patient[0] because the returned result is a list with one element.
                        parseIREtrajectories.III_parseTrajectory(trajectories_info.trajectories, patient[0],
                                                                 trajectories_info.series, xmlfilename,
                                                                 trajectories_info.time_intervention,
                                                                 trajectories_info.cas_version)

# %% extract information from the object classes into pandas dataframe
needle_data = []
patients = patientsRepo.getPatients()
if not patients :
    print('No CAS Recordings found. Check if the files are there and in the correct folder structure.')
else:
    for p in patients:
        lesions = p.getLesions()
        patientID = p.patient_id_xml
        patientName = p.patient_name
        for l_idx, lesion in enumerate(lesions):
            needles = lesion.getNeedles()
            # for each needle get the segmentations associated with it
            try:
                NeedlesInfoClass.NeedleToDictWriter.needlesToDict(needle_data,  patientID,  patientName, l_idx, lesion.getNeedles())
            except Exception:
                print('Class Extraction Error', patientName)
    # unwrap class object and write to dictionary.
    needle_list = []
    for needles in needle_data:
        for l in needles:
            needle_list.append(l)
    df_patients_trajectories = pd.DataFrame(needle_list)
    # %% read MWA Needle Database Excel.
    df_mwa_database = pd.read_excel("CAS_IR_MWA_NeedleDatabase.xlsx")

    ellipse_data = []
    for index, row in df_patients_trajectories.iterrows():
        ablation_index = row["AblationShapeIndex"]
        ablation_system = row["AblationSystem"]
        if ablation_index:
            rows_to_append = df_mwa_database[(df_mwa_database["AblationShapeIndex"] == int(ablation_index)) & (
                        df_mwa_database["AblationSystem"] == ablation_system)]
            dict_mwa = rows_to_append.iloc[:, 2:].to_dict('list')
            ellipse_data.append(dict_mwa)
        else:
            dict_mwa = {'NeedleID': '',
                        'NeedleName': '',
                        'Power': '',
                        'Radii': '',
                        'Rotation': '',
                        'Time_seconds': '',
                        'Translation': '',
                        'Type': ''
                        }
            ellipse_data.append(dict_mwa)
    # concatenate to df_patients_trajectories
    df_ellipse = pd.DataFrame(ellipse_data)
    df_final = pd.concat([df_patients_trajectories, df_ellipse], axis=1, join_axes=[df_ellipse.index])

    #%%  write to excel final list.
    timestr = strftime("%Y%m%d-%H%M%S")
    filename = 'Patients_MWA_Interventions-' + timestr + '.xlsx'
    filepathExcel = os.path.join(rootdir, filename)
    writer = pd.ExcelWriter(filepathExcel)
    # df_final.sort_values(by=['PatientID'], inplace=True)
    df_final.apply(pd.to_numeric, errors='ignore', downcast='float').info()
    df_final[['LateralError']] = df_final[['LateralError']].apply(pd.to_numeric, downcast='float')
    df_final[['AngularError']] = df_final[['AngularError']].apply(pd.to_numeric, downcast='float')
    df_final[['EuclideanError']] = df_final[['EuclideanError']].apply(pd.to_numeric, downcast='float')
    df_final[['LongitudinalError']] = df_final[['LongitudinalError']].apply(pd.to_numeric, downcast='float')
    df_final[["Ablation_Series_UID"]] = df_final[["Ablation_Series_UID"]].astype(str)
    df_final[["Tumor_Series_UID"]] = df_final[["Tumor_Series_UID"]].astype(str)
    df_final[["PatientID"]] = df_final[["PatientID"]].astype(str)
    df_final[["TimeIntervention"]] = df_final[["TimeIntervention"]].astype(str)
    df_final.to_excel(writer, sheet_name='Paths', index=False, na_rep='NaN')
    writer.save()
    print("success")
# %% dataframes for Angles
# Angles = []
# patient_unique = dfPatientsTrajectories['PatientID'].unique()
# TODO: flag to cancel Angles if Dataset is MWA
# for PatientIdx, patient in enumerate(patient_unique):
#    patient_data = dfPatientsTrajectories[dfPatientsTrajectories['PatientID'] == patient]
#    eta.ComputeAnglesTrajectories.FromTrajectoriesToNeedles(patient_data, patient, Angles)
# dfAngles = pd.DataFrame(Angles)
# call the customize_dataframe to make columns numerical, write with 2 decimals
# customize_dataframe(dfAngles, dfPatientsTrajectories, rootdir)
