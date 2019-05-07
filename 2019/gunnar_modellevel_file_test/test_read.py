#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 13:37:40 2019

@author: jonasg
"""

import glob
import pyaerocom as pya
import xarray as xarr

f = glob.glob('test*.nc')[0]
print(f)

#d = pya.GriddedData(f)

ds = xarr.open_dataset(f, decode_times=False)

ds = xarr.open_dataset(f)

print(ds)

d = pya.GriddedData(f,var_name='ec550aer')
print(d)

# =============================================================================
# ds['time'].attrs['calendar'] = 'gregorian'
# 
# ds.to_netcdf('test_{}'.format(f))
# 
# =============================================================================

