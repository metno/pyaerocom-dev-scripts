#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 10:15:06 2020

@author: jonasg
"""


import pyaerocom as pya
from time import time


data = pya.io.ReadUngridded().read('GHOST.daily', 'concpm10')

coords = []
t00=time()
for idx, meta in data.metadata.items():
    coords.append((meta['latitude'], meta['longitude']))

t0 = time()    
country_info = pya.geodesy.get_country_info_coords(coords)
t1 = time()
for idx, meta in data.metadata.items():
    lat, lon = meta['latitude'], meta['longitude']
    pya.geodesy.get_country_info_coords((lat, lon))
t2=time()

print('Loop over all sites: {:.2} s'.format(t0-t00))
print('All at once: {:.2} s'.format(t1-t0))
print('Site by site: {:.2} s'.format(t2-t1))
                