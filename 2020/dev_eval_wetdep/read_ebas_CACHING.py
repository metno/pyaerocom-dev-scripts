#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 10:14:00 2020

@author: jonasg
"""

import pyaerocom as pya

assert pya.const.has_access_lustre

read_vars = ['concprcpno3', 'concprcpso4']
reader = pya.io.ReadUngridded()
for var in read_vars:
    print(f'READING {var}')
    data = reader.read('EBASMC', var)