#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 09:36:04 2019

@author: jonasg
"""

import pyaerocom as pya
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

plt.close('all')

#fig = plt.figure()
ax = pya.plot.mapping.init_map()
ax.stock_img()
print(type(ax))

x = np.arange(20)
y = np.sin(x)

# get figure instance
fig = ax.figure

coords = [(0,0), (5,5)]#, (20, 80), (-60, -120)]

axes = []
for (lat, lon) in coords:
    ax.plot(lon, lat, ' xr', markersize=12)
    
    ax1 = inset_axes(ax, width='100%', height='100%', loc=10,
                     bbox_to_anchor=(lon, lat, lon+5, lat+5),
                     bbox_transform=ax.transData, 
                     borderpad=True)
    axes.append(ax1)
    ax1.plot(x, y, c='lime')
    ax1.patch.set_facecolor('w')
    ax1.patch.set_edgecolor('none')
    ax1.patch.set_alpha(0.5)

    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    
plt.show()
print(ax.get_position())
for _ax in axes:
    print(_ax.get_position())