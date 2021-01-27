#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 16:02:34 2020

@author: jonasg
"""

import pyaerocom as pya

reader = pya.io.ReadEbas()

files = reader.get_file_list('concprcpso4')

print(len(files))

has_precip = 0
files_wprecip = []
varcols = []
i = 0
check_cols = ['precipitation_amount', 'precipitation_amount_off']
for i, file in enumerate(files):
    if i%50 == 0:
        print(i)
    data = pya.io.EbasNasaAmesFile(file)
    varcols.extend(data.col_names_vars)
    prcols = [x in data.col_names_vars for x in check_cols]
    if any(prcols):
        has_precip += 1
        files_wprecip.append(file)
        if all(prcols):
            print(42)

unique_cols = list(dict.fromkeys(varcols))




