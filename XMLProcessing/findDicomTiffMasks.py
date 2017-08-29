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
import pandas as pd
import untangle as ut


srvPath = '\\\\cochlea.artorg.unibe.ch\IGT\Projects\LIVER\_Clinical_Data\Interventions'
foundData = []

for dirname, dirnames, filenames in os.walk(srvPath):
    if dirname.find('datasets') == -1:
        continue
    # find the datasets folder
    for filename in filenames:
        # find the xml file ": PatientIntials.xml"
        idxPat = dirname.upper().lower().find('pat_') + 4
        idxPatEnd = dirname.find('_', idxPat)
        patientInitials = dirname[idxPat:idxPatEnd]
        clinic = dirname[len(srvPath)+1:dirname.find('\\', len(srvPath)+2)]

        file, fileExtension = os.path.splitext(filename)

        if fileExtension.lower().endswith('.xml') and patientInitials == file:
            roiData = []
            xmlFilePathName = os.path.join(dirname, filename)
            xmlFilePathName_norm = os.path.normpath(xmlFilePathName)
             # open XML filename and extract the path of the tumor segmentation map
            try:
                obj = ut.parse(xmlFilePathName_norm)
                data = obj.HEPAVISION_INFO.IMAGEDATA
                k = 0
                tumorData = []
                for imagedata in data:
                    rois = imagedata.ROI
                    for roi in rois:
                        try:
                            result = roi.RESULT
                            # save the obj id and filepaths to be able to retrieve the source img on which the segmentation was based on
                            roiData.append({
                                    'objID': roi.OBJ_ID.cdata,
                                    'FilePathSourceImg' : roi.FILENAME.cdata[2:],
                                    'ImageType' : roi.cdata
                            })
                            for res in result:
                                # add all the tumor data to a new list
                                if 'tumor'.casefold() in res.cdata.casefold() or \
                                'Metastas'.casefold() in res.cdata.casefold() or \
                                'Cyst'.casefold() in res.cdata.casefold():
                                   # remove the "./" in front of the filename
                                    filenameTumor = res.FILENAME.cdata[2:]
                                    # the TIFF contains the binary image mask
                                    # the DICOM contains only the metadata
                                    tumorData.append({
                                            'TumorTitle': res.TITLE.cdata,
                                            'PathDicomTumor': os.path.join(dirname,filenameTumor),
                                            'PathTiffTumor':  os.path.join(dirname, filenameTumor[:-4]+'.tif'),
                                            'basedon_ROI_OBJID': res.BASED_ON.cdata
                                            })
    
                        except Exception:
                            print('result data not found in roi:',xmlFilePathName)
                            
                    if k>1:  print('Tumors found:',str(k))
    
                for i, d in enumerate(tumorData):
                    # iterate through the list of dict ROIs to find segmentation source based on OBJ_ID
                    filepathSourceImg, ImageType = next((item["FilePathSourceImg"], 
                                                     item["ImageType"])for item in roiData if item["objID"] == d['basedon_ROI_OBJID'])
                    # add new entry to the tumorData dictionary --> 
                    # the image path on which the segmentation was based
                    foundData.append({
                                    'PatientID' : obj.HEPAVISION_INFO.PATIENT.PID.cdata,
                                    'PatientInitials': patientInitials,
                                    'Clinic' : clinic,
                                    'PathXML' : xmlFilePathName,
                                    'PathDicomTumor': d['PathDicomTumor'],
                                    'PathTiffTumor': d['PathTiffTumor'],
                                    'PathDicomSource':  os.path.join(dirname, filepathSourceImg),
                                    'ImageType' : ImageType,
                                    'TumorTitle': d['TumorTitle']
                                })
            except Exception:
                print('XML file structure problem:',xmlFilePathName)

#%%
df = pd.DataFrame(foundData)  # convert list of dicts to pandas dataframe
timestr = time.strftime("%Y%m%d-%H%M%S")
filenameExcel = '3DMevisSegmentationMasks.csv'
#writer = pd.ExcelWriter(filenameExcel)
#df.to_excel(writer,sheet_name='MevisFilepaths', index=False)
# might need to change to param "constant memory" for perfomance matters
# workbook = xlsxwriter.Workbook(filename, {'constant_memory': True})

with open(filenameExcel, 'a') as f:
    df.to_csv(f, header=False)
