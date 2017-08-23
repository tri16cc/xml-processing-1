# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 10:18:00 2017

The XML file : \\cochlea.artorg.unibe.ch\IGT\Projects\LIVER\_Clinical_Data\Laparoscopic_Liver_Surgery\Bern\Pat_BP_0010922318_2015-10-13_14-27-30\Technical Report\MeVis Data\datasets\BP.xml
contains tumors tags <Tumor> </Tumour> where the filename is located

The segmented tumor can be found in the MeVis DICOM file “BP_0010922318_0001021.dcm”.

@author: Raluca Sandu
"""

import os
import time
import csv
import argparse
import untangle as ut


srvPath = '\\\\cochlea.artorg.unibe.ch\IGT\Projects\LIVER\_Clinical_Data\Laparoscopic_Liver_Surgery'
print('searching in ', srvPath)

numLivers = 0
foundData = []

for dirname, dirnames, filenames in os.walk(srvPath):
    if dirname.find('datasets') == -1:
        continue
  # find the datasets folder  
    for filename in filenames:
        # find the xml file ": PatientIntials.xml"
        idxPat = dirname.upper().lower().find('pat_') + 4
        idxPatEnd = dirname.find('_', idxPat)
        patientID = dirname[idxPat:idxPatEnd]
        idxPatEnd = dirname.find('\\', idxPat)
        patientID_full = dirname[idxPat:idxPatEnd]
        clinic = dirname[len(srvPath)+1:dirname.find('\\', len(srvPath)+2)]
        
        file, fileExtension = os.path.splitext(filename)
        if fileExtension.lower().endswith('.xml') and patientID == file:
            xmlFilePathName = os.path.join(dirname, filename)
            xmlFilePathName_norm = os.path.normpath(xmlFilePathName)
            
            # open XML filename and extract the path of the tumor segmentation map
            try:
                obj = ut.parse(xmlFilePathName_norm)
                try:
                    data = obj.HEPAVISION_INFO.IMAGEDATA
                    for imagedata in data:
                        rois = imagedata.ROI
                        for roi in rois:
                            try:
                                result = roi.RESULT
                                for re in result:
                                    if 'Tumor' in re.cdata:
                                        filenameTumor = re.FILENAME.cdata
                                        basedon_ROI_OBJID = re.BASED_ON.cdata
        #                                print('a tumor found')
                            except Exception:
                                print('result data not found')
                     # add the ROI corresponding to the segmentation map, ie venous or arterial phase
                     # exctract OBJ_ID from <BASED_ON>, go to corresponding OBJ_ID ROI --> 
                     # --> extract filename .dcm, add path to csv
                    foundData.append({
                            'Patient' : patientID_full,
                            'Clinic' : clinic,
                            'Path' : xmlFilePathName,
                            # add the path of the tumor!!
        
                        })
                except Exception:
                    print('no imageData found: ',xmlFilePathName)
            except Exception:
                print('XML file structure problem:',xmlFilePathName)
                