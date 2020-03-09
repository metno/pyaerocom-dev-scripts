#!/usr/bin/env python
# coding: utf-8

# # Test reading and colocation of GHOST data

import pyaerocom as pya

model_reader = pya.io.ReadGridded('EMEP_rv4_33_Glob-CTRL')
emep_pm10_2010 = model_reader.read_var('concpm10', start=2010)

reader = pya.io.ReadUngridded()
obs_pm10 = reader.read('GHOST.daily', 'concpm10')

coldata2018 = pya.colocation.colocate_gridded_ungridded(emep_pm10_2010, obs_pm10, 
                                                        update_baseyear_gridded=2018, 
                                                        start=2018, 
                                                        ts_type='monthly',
                                                        var_ref='concpm10')
