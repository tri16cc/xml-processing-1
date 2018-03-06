# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:49:22 2018

@author: Raluca Sandu
"""
import os
import re
import time
import numpy as np
import pandas as pd
from datetime import datetime
import IREExtractClass as ie
import parseIREtrajectories as pit 
import extractTrajectoriesAngles as eta
#%%

#        
rootdir = "C:/Users/Raluca Sandu/Documents/MATLAB/My CAS-One Data/"
#rootdir = "C:/IRE_Stockholm_35cases/"
#
#instantiate the Patient's Repository class
patientsRepo = ie.PatientRepo()
pat_ids = []

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        fileName,fileExtension = os.path.splitext(file)
        if fileExtension.lower().endswith('.xml') and 'validation'in fileName.lower():
            xmlFilePathName = os.path.join(subdir, file)
            xmlfilename = os.path.normpath(xmlFilePathName)
            try:
                pat_id_str = re.findall('\\d+', xmlfilename)
                pat_id = int(pat_id_str[0])
                pat_ids.append(pat_id)
            except Exception:
                print('numeric data not found in the file name', xmlfilename)
                
            xmlobj = pit.I_parseRecordingXML(xmlfilename, pat_id)
            
            if xmlobj is not None:
                # parse trajectories
                trajectories = pit.II_parseTrajectories(xmlobj)
                # check if patient exists first, if yes, instantiate new object, otherwise retrieve it from list
                patients = patientsRepo.getPatients()
                patient = [x for x in patients if x.patientId == pat_id]
                if not patient:
                    # create patient measuerements if patient is not already in the PatientsRepository
                    patient = patientsRepo.addNewPatient(pat_id)
                    pit.III_parseTrajectory(trajectories, patient)
                else:
                    # update patient measurements in the PatientsRepository if the patient (id) already exists
                    pit.III_parseTrajectory(trajectories, patient[0])

IRE_data = []
patients = patientsRepo.getPatients()
for p in patients:
    lesions = p.getLesions()
    patientID = p.patientId
    for lIdx, l in enumerate(lesions):
        ie.NeedleToDictWriter.needlesToDict(IRE_data,patientID, lIdx+1, l.getNeedles())        

df = pd.DataFrame(IRE_data)  
Angles = []     
patient_unique = df['PatientID'].unique()     
for PatientIdx, patient in enumerate(patient_unique):
    patient_data = df[df['PatientID']==patient]
    eta.ComputeAnglesTrajectories.FromTrajectoriesToNeedles(patient_data,patient, Angles)
    
dfAngles = pd.DataFrame(Angles)        
    
# TO DO: 1) write to CSV/Excel --> DONE
# TO DO: 2) calculate angle plan, calculate angle validation  --> DONE, still must check if the correct plan trajectory is extracted (seems so)       
# CAS- version: 3) database of needles (extract the type of needle from the plan), check if need to account for offset