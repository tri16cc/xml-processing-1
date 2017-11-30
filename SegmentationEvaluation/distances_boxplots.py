# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 19:15:03 2017

@author: Raluca Sandu
"""

import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
#plt.style.use('classic')
#plt.style.use('seaborn')

test_data = [np.random.normal(mean, 1, 5) for mean in range(10)]

fig, axes = plt.subplots(figsize=(12, 16))

# Horizontal box plot
bplot = plt.boxplot(test_data,
                     vert=True,   # vertical box aligmnent
                     patch_artist=False,
                     showmeans=True)   # fill with color
                    
                     
for element in ['medians','boxes', 'fliers', 'whiskers', 'caps']:
    plt.setp(bplot[element], color='black',linewidth=1.5)

plt.setp(bplot['whiskers'], linestyle='--')
plt.setp(bplot['fliers'], markersize=5)
                     
xlim = np.array(plt.gca().get_xlim())
ylim = np.array(plt.gca().get_ylim())
plt.fill_between(xlim, y1=([ylim[0],ylim[0]]) , y2=([0, 0]) ,
                 color="#EC7063", zorder=0)
plt.fill_between(xlim, y1=([0, 0]), y2=([5, 5]) ,
                 color="#FAD7A0", zorder=0)
plt.fill_between(xlim, y1=([5, 5]), y2=(ylim[1], ylim[1]), 
                 color="#ABEBC6", zorder=0 )
plt.margins(0)

plt.xlabel('Patients')
plt.ylabel('[mm]')
plt.show()                     