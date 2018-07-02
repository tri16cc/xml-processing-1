# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:49:22 2018

@author: Raluca Sandu
"""
import os
import re
import pandas as pd
import NeedlesInfoClass
import parseIREtrajectories
import extractTrajectoriesAngles as eta
from customize_dataframe import customize_dataframe

# %%
# TODO: user keyboard input to ask for study folder
# TODO: get patient id from the folder name before the intervention
# TODO: patient naming consistency
# TODO: extract the datatime from the segmentations folder(new cas version)
# old cas version: segmentations path read the plan.xml and validation.xml from each segmentations folder to find the corresponding trajectory.
# new cas version: segmentation path in Ablation_Validation.xml
# find correct plan/validation based on series number
rootdir = r"C:\PatientDatasets_GroundTruth_Database\GroundTruth_2018\GT_23042018"
# instantiate the Patient's Repository class
patientsRepo = NeedlesInfoClass.PatientRepo()
pat_ids = []
pat_id = 0


for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        fileName, fileExtension = os.path.splitext(file)
        # TODO: add ablation validation xml type of file
        if fileExtension.lower().endswith('.xml') and (
                'validation' in fileName.lower() or 'plan' in fileName.lower()):
            xmlFilePathName = os.path.join(subdir, file)
            xmlfilename = os.path.normpath(xmlFilePathName)
            try:
                # find the numbers before the "_Pat" till the "//"
                pat_idx = xmlfilename.find("_Pat")
                pat_id_str = re.findall('\\d+', xmlfilename[0:pat_idx])
                pat_id = int(pat_id_str[len(pat_id_str) - 1])
                pat_ids.append(pat_id)
            except Exception:
                print('numeric data not found in the file name', xmlfilename)
            pat_ids.append(pat_id)
            xmlobj = parseIREtrajectories.I_parseRecordingXML(xmlfilename)
            if xmlobj is not None:
                # parse trajectories and other patient specific info
                trajectories_info = parseIREtrajectories.II_parseTrajectories(xmlobj)
                if trajectories_info.trajectories is None:
                    continue
                else:
                    # check if patient exists first, if yes, instantiate new object, otherwise retrieve it from list
                    patients = patientsRepo.getPatients()
                    patient = [x for x in patients if x.patientId == pat_id]
                    if not patient:
                        # create patient measurements if patient is not already in the PatientsRepository
                        patient = patientsRepo.addNewPatient(pat_id,
                                                             trajectories_info.patient_id_xml,
                                                             trajectories_info.time_intervention)
                        parseIREtrajectories.III_parseTrajectory(trajectories_info.trajectories, patient,
                                                                 trajectories_info.series, xmlfilename)
                    else:
                        # update patient measurements in the PatientsRepository if the patient (id) already exists
                        parseIREtrajectories.III_parseTrajectory(trajectories_info.trajectories, patient[0],
                                                                 trajectories_info.series, xmlfilename)
# %% extract information from the object classes into pandas dataframe
needle_data = []
patients = patientsRepo.getPatients()
for p in patients:
    lesions = p.getLesions()
    patientID = p.patientId
    for l_idx, lesion in enumerate(lesions):
        # some type (list to dict!?) that I haven't figured out how to solve yet
        needles = lesion.getNeedles()
        # for each needle get the segmentations associated with it
        NeedlesInfoClass.NeedleToDictWriter.needlesToDict(needle_data, patientID, l_idx, lesion.getNeedles())

dfPatientsTrajectories = pd.DataFrame(needle_data)
print("success")
# dfPatientsTrajectories.sort_values(by=['PatientID'])
# Angles = []
# patient_unique = dfPatientsTrajectories['PatientID'].unique()

# %% dataframes for Angles
# TODO: flag to cancel Angles if Dataset is MWA
# for PatientIdx, patient in enumerate(patient_unique):
#    patient_data = dfPatientsTrajectories[dfPatientsTrajectories['PatientID'] == patient]
#    eta.ComputeAnglesTrajectories.FromTrajectoriesToNeedles(patient_data, patient, Angles)
# dfAngles = pd.DataFrame(Angles)
## call the customize_dataframe to make columns numerical, write with 2 decimals
# customize_dataframe(dfAngles, dfPatientsTrajectories, rootdir)
