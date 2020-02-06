#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 09:31:45 2019

@author: jonasg
"""

import pyaerocom as pya

r = pya.io.ReadGridded('MIROC-SPRINTARS_AP3-CTRL')

print(r)

data = r.read_var('ac550aer')

print(data)

monthly = data.resample_time('monthly', use_iris=True)

ts_type = data.ts_type
outname = data.from_files[0].replace(ts_type, 'monthly')
monthly.to_netcdf('.', savename=outname)