#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 11:09:53 2019

@author: jonasg
"""

import pyaerocom as pya
#pya.const.load_default_config()

r = pya.io.ReadUngridded()

print(r.SUPPORTED_DATASETS)

data = r.read('AeronetSunV3Lev2.daily', ['od550aer', 'ang4487aer'])

print(data)