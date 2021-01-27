#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 09:46:11 2020

@author: jonasg
"""
import pyaerocom as pya
assert pya.const.has_access_lustre


data_dir = '/home/jonasg/MyPyaerocom/data/obsdata/GHOST/data/EEA_AQ_eReporting/hourly/'

reader = pya.io.ReadUngridded('GHOST.EEA.hourly',
                              data_dir=data_dir)


data = reader.read(vars_to_retrieve='vmro3')

#stats0 = data.to_station_data_all('vmro3', start=2018)