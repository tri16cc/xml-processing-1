# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:49:22 2018

@author: Raluca Sandu
"""
import os
import pandas as pd
from time import strftime
import NeedlesInfoClasses
import parseNeedleTrajectories as parseNeedleTrajectories
from collections import defaultdict
import extractTrajectoriesAngles as eta
#from customize_dataframe import customize_dataframe
# %%
rootdir = r"C:\Stockholm_IRE_Study\IRE_Stockholm_allCases"

patientsRepo = NeedlesInfoClasses.PatientRepo()
pat_ids = []
pat_id = 0

for subdir, dirs, files in os.walk(rootdir):

    for file in files:
        fileName, fileExtension = os.path.splitext(file)

        if fileExtension.lower().endswith('.xml') and (
                'validation' in fileName.lower() or 'plan' in fileName.lower()):
            xmlFilePathName = os.path.join(subdir, file)
            xmlfilename = os.path.normpath(xmlFilePathName)

            xmlobj = parseNeedleTrajectories.I_parseRecordingXML(xmlfilename)

            if xmlobj is 1:
                # file was re-written of weird characters so we need to re-open it.
                xmlobj = parseNeedleTrajectories.I_parseRecordingXML(xmlfilename)
            if xmlobj is not None and xmlobj!=1:
                pat_id = xmlobj.patient_id_xml
                pat_ids.append(pat_id)
                # parse trajectories and other patient specific info
                trajectories_info = parseNeedleTrajectories.II_parseTrajectories(xmlobj.trajectories)
                if trajectories_info.trajectories is None:
                    continue # no trajectories found in this xml, go on to the next file.
                else:
                    # check if patient exists first, if yes, instantiate new object, otherwise retrieve it from list
                    patients = patientsRepo.getPatients()
                    patient = [x for x in patients if x.patient_id_xml == pat_id]
                    if not patient:
                        # instantiate patient object
                        # create patient measurements if patient is not already in the PatientsRepository
                        patient = patientsRepo.addNewPatient(pat_id,
                                                             xmlobj.patient_name)
                        # instantiate extract registration
                        # TODO: write registration matrix to Excel
                        parseNeedleTrajectories.II_extractRegistration(xmlobj.trajectories, patient, xmlfilename)
                        # add intervention data
                        parseNeedleTrajectories.III_parseTrajectory(trajectories_info.trajectories, patient,
                                                                    trajectories_info.series, xmlfilename,
                                                                    trajectories_info.time_intervention,
                                                                    trajectories_info.cas_version)
                    else:
                        # update patient measurements in the PatientsRepository if the patient (id) already exists
                        # patient[0] because the returned result is a list with one element.
                        parseNeedleTrajectories.III_parseTrajectory(trajectories_info.trajectories, patient[0],
                                                                    trajectories_info.series, xmlfilename,
                                                                    trajectories_info.time_intervention,
                                                                    trajectories_info.cas_version)
                        # add the registration, if several exist (hopefully not)
                        # TODO: add flag in excel if registration existing (write registration to excel)
                        parseNeedleTrajectories.II_extractRegistration(xmlobj.trajectories, patient[0], xmlfilename)

# %% extract information from the object classes into pandas dataframe
patients = patientsRepo.getPatients()
needles_list = []
if patients :
    for patient in patients:
        lesions = patient.getLesions()
        patientID = patient.patient_id_xml
        patientName = patient.patient_name
        img_registration = patient.registrations
        # check-up if more than one distinct img_registration available
        if len(img_registration) > 1:
            print('more than one registration available for patient', patientName)
        for l_idx, lesion in enumerate(lesions):
            needles = lesion.getNeedles()
            needles_defaultdict = NeedlesInfoClasses.NeedleToDictWriter.needlesToDict(patientID,
                                                                                    patientName,
                                                                                    l_idx,
                                                                                    needles,
                                                                                    img_registration)
            needles_list.append(needles_defaultdict)
    # unpack from defaultdict and list
    needles_unpacked_list = defaultdict(list)
    for needle_trajectories in needles_list:
        for keys, vals in needle_trajectories.items():
            for val in vals:
                needles_unpacked_list[keys].append(val)
    # conver to DataFrame for easier writing to Excel
    df_patients_trajectories = pd.DataFrame(needles_unpacked_list)
    print("success")
elif not patients:
    print('No CAS Recordings found. Check if the files are there and in the correct folder structure.')


    #%%  write to excel final list.
timestr = strftime("%Y%m%d-%H%M%S")
filename = 'MAVERRIC_Stockholm_June_all_patients_' + timestr + '.xlsx'
filepathExcel = os.path.join(rootdir, filename)
writer = pd.ExcelWriter(filepathExcel)
df_final = df_patients_trajectories
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
