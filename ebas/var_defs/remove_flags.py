#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 16:03:37 2018

@author: jonasg
"""

import pyaerocom as pya

DIR = pya.const.EBASMC_DATA_DIR

req =  pya.io.EbasSQLRequest(['aerosol_light_scattering_coefficient'], 
                             station_names='Bondville')

db = pya.io.EbasFileIndex()

files = db.get_file_names(req)



f0 = DIR + files[0]

data = pya.io.EbasNasaAmesFile(f0)

result = pya.io.helpers.read_ebas_flags_file(pya.const.EBAS_FLAGS_FILE)




r = pya.io.ReadEbas()

data = r.read('scatc550aer', station_names='Bondville')