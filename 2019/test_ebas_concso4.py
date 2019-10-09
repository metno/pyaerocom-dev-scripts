#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 11:44:06 2019

@author: jonasg
"""
import pyaerocom as pya
import matplotlib.pyplot as plt
plt.close('all')

r = pya.io.ReadGridded('OsloCTM3v1.01-met2010_AP3-CTRL')

concso4 = r.read_var('concso4', start=2010)


sconcso4 = concso4.extract_surface_level()
#sconcso4.quickplot_map()


obs = pya.io.ReadUngridded().read('EBASMC', 'concso4')

coldata = pya.colocation.colocate_gridded_ungridded(concso4,
                                                    obs)

#coldata.plot_scatter()


coldata.plot_scatter(loglog=True)