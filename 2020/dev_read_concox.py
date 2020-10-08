#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 11:11:48 2020

@author: jonasg
"""

import pyaerocom as pya


model_id = 'SILAM.cams61.day1'

reader =  pya.io.ReadGridded(model_id)

print(reader)

mod = reader.read_var('concox', vert_which='Surface')

mod.quickplot_map()