#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 13:39:09 2019

@author: jonasg
"""

import pyaerocom as pya
import numpy as np
import xarray as xarr
import matplotlib.pyplot as plt

plt.close('all')

r = pya.io.ReadGridded('ECHAM')

print(r.filter_files(start=2010))

rh = r.read_var('rhs', start=2010)
ec = r.read_var('ecs550aer', start=2010)


#ecdry = pya.io.aux_read_cubes.apply_rh_thresh_cubes(ec, rh)
print(rh.from_files)
print(ec.from_files)

ax =pya.plot.mapping.init_map()
ds = xarr.load_dataset(rh.from_files[0])

ds.rhs[0].plot(ax=ax)

ds1 = xarr.load_dataset(ec.from_files[0])

#ax1 = ds1.ecs550aer[0].plot()        

rh.quickplot_map()
ec.quickplot_map()
