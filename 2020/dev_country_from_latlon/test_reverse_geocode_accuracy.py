#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 10:15:06 2020

@author: jonasg
"""


import pyaerocom as pya
from time import time
import pandas as pd

data = pya.io.ReadUngridded().read('GHOST.daily', 'concpm10')

results = []
checked = []
for idx, meta in data.metadata.items():
    stat = meta['station_name']
    if stat in checked:
        continue
    checked.append(stat)
    lat, lon = meta['latitude'], meta['longitude']
    country = meta['country']
    info = pya.geodesy.get_country_info_coords((lat, lon))
    results.append([stat, lat, lon, country, info['country'], info['country_code']])
    
df = pd.DataFrame(results, columns=['Station name', 'lat', 'lon','Country (meta)', 'Country (RG)', 'Country code (RG)'])

df.to_csv('country_compare_ghost_meta_vs_reverse_geocode.csv')