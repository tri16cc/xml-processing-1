# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 13:43:49 2017

@author: Raluca Sandu
"""
# libraries import

import numpy as np
from medpy import metric
import pandas as pd
import SimpleITK as sitk
#from scipy import ndimage
from surface import Surface
from enum import Enum
import matplotlib.pyplot as plt
#plt.style.use('ggplot')
#plt.style.use('classic')
#print(plt.style.available)

#%%
class DistanceMetrics(object):
    

    
    def __init__(self,mask, reference):

        # image read as img[x,y,z]
        reference_segmentation = sitk.ReadImage(reference, sitk.sitkUInt8)
        segmentation = sitk.ReadImage(mask,sitk.sitkUInt8)
        print(reference_segmentation.GetSpacing())
        print(reference_segmentation.GetOrigin())
        print(reference_segmentation.GetSize())
        label = 255
         
        class SurfaceDistanceMeasuresITK(Enum):
            hausdorff_distance, max_surface_distance, avg_surface_distance, median_surface_distance, std_surfance_distance = range(5)
        
        # Computes the maximum symmetric surface distance = Hausdorff distance between the two objects surfaces.
        class SurfaceDistanceMeasuresSurfacePy(Enum):
            hausdorff_distance, avg_symmetric_surface_distance, rms_symmetric_surface_distance = range(3)
        
        class MedpyMetricDists(Enum):
            hausdorff_distanceMedPy, avg_surface_distanceMedPy, avg_symmetric_surface_distanceMedPy = range(3)
        
        surface_distance_results = np.zeros((1,len(SurfaceDistanceMeasuresITK.__members__.items())))
        surface_distance_SurfacePy = np.zeros((1,len(SurfaceDistanceMeasuresSurfacePy.__members__.items())))
        surface_dists_Medpy = np.zeros((1,len(MedpyMetricDists.__members__.items())))
        
        #%%
        segmented_surface = sitk.LabelContour(segmentation)
        
        # init signed mauerer distance as reference metrics
        reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(reference_segmentation, squaredDistance=False, useImageSpacing=True))
        
        # init label intensity statistics filter
        label_intensity_statistics_filter = sitk.LabelIntensityStatisticsImageFilter()
        label_intensity_statistics_filter.Execute(segmented_surface, reference_distance_map)
        
        hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
        hausdorff_distance_filter.Execute(reference_segmentation, segmentation)

        surface_distance_results[0,SurfaceDistanceMeasuresITK.hausdorff_distance.value] = hausdorff_distance_filter.GetHausdorffDistance()
        surface_distance_results[0,SurfaceDistanceMeasuresITK.max_surface_distance.value] = label_intensity_statistics_filter.GetMaximum(label)
        surface_distance_results[0,SurfaceDistanceMeasuresITK.avg_surface_distance.value] = label_intensity_statistics_filter.GetMean(label)
        surface_distance_results[0,SurfaceDistanceMeasuresITK.median_surface_distance.value] = label_intensity_statistics_filter.GetMedian(label)
        surface_distance_results[0,SurfaceDistanceMeasuresITK.std_surfance_distance.value] = label_intensity_statistics_filter.GetStandardDeviation(label)
        
        self.surface_distance_results_df = pd.DataFrame(data=surface_distance_results, index = list(range(1)),
                                      columns=[name for name, _ in SurfaceDistanceMeasuresITK.__members__.items()])
        
        
        # mauerer distances from simple itk
        #fig, ax= plt.subplots()
        #plt.hist(reference_distance_map)
        #plt.title('Mauerer Distance Map')
        
        # plt mauerer distance map multiplied with the contour
        segmented_surface_float = sitk.GetArrayFromImage(segmented_surface)
        reference_distance_map_float = sitk.GetArrayFromImage(reference_distance_map)
        dists_to_plot = segmented_surface_float * reference_distance_map_float
        fig1, ax1= plt.subplots()
        z = int(np.floor(np.shape(dists_to_plot)[0]/2))
        plt.imshow(dists_to_plot[z,:,:]/255)
        plt.title(' Distance Map. 1 Slice Visualization')
        
        ix = dists_to_plot.nonzero()
        dists_nonzero = dists_to_plot[ix]
        fig3, ax3 = plt.subplots()
        plt.hist(dists_nonzero/255)
        plt.title('Histogram Mauerer Distances')
        #%%
        # img read as img[z,y,x]
        img_array = sitk.GetArrayFromImage(reference_segmentation)
        seg_array = sitk.GetArrayFromImage(segmentation)
        # reverse array in the order x, y, z
        img_array_rev = np.flip(img_array,2)
        seg_array_rev = np.flip(seg_array,2)
        vxlspacing = segmentation.GetSpacing()
        
        if np.count_nonzero(img_array)==0 or np.count_nonzero(seg_array)==0:
            surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.hausdorff_distance.value] = 0
            surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.avg_surface_distance.value] = 0
            surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.rms_surface_distance.value] = 0
        
        else:
            evalsurf = Surface(img_array_rev, seg_array_rev, physical_voxel_spacing = vxlspacing , mask_offset = [0.,0.,0.], reference_offset = [0.,0.,0.])
            surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.hausdorff_distance.value] = evalsurf.get_maximum_symmetric_surface_distance()
            surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.avg_symmetric_surface_distance.value] = evalsurf.get_average_symmetric_surface_distance()
            surface_distance_SurfacePy[0,SurfaceDistanceMeasuresSurfacePy.rms_symmetric_surface_distance.value]= evalsurf.get_root_mean_square_symmetric_surface_distance()
        
        surface_distance_SurfacePY_df = pd.DataFrame(data=surface_distance_SurfacePy, index = list(range(1)),
                                      columns=[name for name, _ in SurfaceDistanceMeasuresSurfacePy.__members__.items()])
        
        #%% use the MedPy metric library
        
        #msd = metric.hd(ref,seg,voxelspacing=vxlspacing)
        surface_dists_Medpy[0,MedpyMetricDists.hausdorff_distanceMedPy.value] = metric.binary.hd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
        surface_dists_Medpy[0,MedpyMetricDists.avg_surface_distanceMedPy.value] = metric.binary.asd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
        surface_dists_Medpy[0,MedpyMetricDists.avg_symmetric_surface_distanceMedPy.value] = metric.binary.assd(seg_array_rev,img_array_rev, voxelspacing=vxlspacing)
        self.surface_dists_Medpy_df = pd.DataFrame(data=surface_dists_Medpy, index = list(range(1)),
                                      columns=[name for name, _ in MedpyMetricDists.__members__.items()])
        
        

    #%%
           # Plot the data as bar plots
        self.surface_distance_results_df.plot(kind='bar').legend(loc='best')
        plt.title('Metrics Computed with Simple ITK')
        surface_distance_SurfacePY_df.plot(kind='bar').legend(loc='best')
        plt.title("Metrics Computed with Surface Py . LITS Challenge")
        self.surface_dists_Medpy_df.plot(kind='bar').legend(loc='best')
        plt.title("Metrics Computed with MedPy Library")
        
    def get_Distances(self):
        # convert to DataFrame
        metrics_all = pd.concat([self.surface_dists_Medpy_df, self.surface_distance_results_df], axis=1)
        return(metrics_all)
    
    def get_SitkDistances(self):
        return self.surface_distance_results_df