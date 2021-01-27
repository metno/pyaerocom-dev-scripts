#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:23:13 2020

@author: jonasg
"""

import pyaerocom as pya

reader = pya.io.ReadUngridded()

data = reader.read('EBASMC', 'conctno3')

data.plot_station_coordinates()