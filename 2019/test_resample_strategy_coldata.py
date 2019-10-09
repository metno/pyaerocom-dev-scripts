#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 11:44:06 2019

@author: jonasg
"""

import xarray as xarr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.close('all')

idx = pd.date_range('1-1-2010', '31-12-2010', freq='D')

per_idx = pd.date_range('1-1-2010', '31-12-2010', freq='M').to_period('M')
print(idx)


arr = np.empty((2, len(idx))) * np.nan

arr[1] = 0

arr[:, 15] = 10 #one in January
arr[:, 46] = 20 # one in Feb
arr[:, 75] = 30 # one in March




coords={'s':  ['o', 'm'], 
        't' : idx}

dims = ['s', 't']

daily = xarr.DataArray(arr, dims=dims, coords=coords)

monthly = daily.resample(t='M').mean(dim='t')

print('Mean (daily, ALL):', daily.mean())
print('Mean (monthly, ALL):', monthly.mean())

daily1 = daily.copy()
daily1[1][np.isnan(daily1[0])] = np.nan

monthly1 = daily1.resample(t='M').mean(dim='t')

print('Mean (daily1, ALL):', daily1.mean())
print('Mean (monthly1, ALL):', monthly1.mean())

idx = pd.date_range('1-1-2010', '31-12-2010', freq='D')

s = pd.Series(np.ones_like(idx), idx)

s.plot()

