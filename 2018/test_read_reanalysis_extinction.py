#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 09:24:35 2019

@author: jonasg
"""

import pyaerocom as pya 

reader = pya.io.ReadGridded('ECMWF_CAMS_REAN')

data = reader.read_var('ec532aer3D', ts_type='daily')