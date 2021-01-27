#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 10:14:00 2020

@author: jonasg
"""

import pyaerocom as pya
import iris
import xarray as xr

pya.const.__init__(config_file=pya.const._config_ini_localdb)


reader = pya.io.ReadGridded('EMEP-cams50-u3all')
#print(reader)

#reader = pya.io.ReadGridded('EURAD-IM.cams61.rerun')
print(reader)


#pr = reader.read_var('pr', start=2018)
#wetox = reader.read_var('wetoxn', start=2018)

concprcpoxn = reader.read_var('concprcpoxn',
                              try_convert_units=False)
#cube = iris.load_raw(ff)


#print(cube)


