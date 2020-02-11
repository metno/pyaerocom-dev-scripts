#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:55:03 2020

@author: jonasg
"""
import pyaerocom as pya
import matplotlib.pyplot as plt

plt.close('all')

data_dir = '/lustre/storeA/project/fou/kl/CAMS61/CAMS_2018/EMEP/'

data_file = 'EMEP_20180101_O3_0H24H.nc'

data = pya.GriddedData(data_dir + data_file)

data = data.extract_surface_level()

data.metadata['ts_type'] = None

# THIS WORKS NOW
data.quickplot_map()


# NOW CHECK PALEO DATE
data.change_base_year(901)

data.quickplot_map()

print("ALL GOOD")