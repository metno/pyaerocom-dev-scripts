#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 09:15:31 2020

@author: jonasg
"""

import pyaerocom as pya

tt = 'hourly'
gdir = f'/home/jonasg/MyPyaerocom/data/obsdata/GHOST/data/EEA_AQ_eReporting/{tt}'
reader = pya.io.ReadUngridded(f'GHOST.EEA.{tt}',
                              data_dir=gdir)

data = reader.read(vars_to_retrieve='conco3')

standard_filter = {'set_flags_nan':True,}

EEA_rural_station_types_to_include = ['background']
EEA_rural_area_types_to_include = ['rural','rural-near_city','rural-regional', 'rural-remote']

rural_filter = {'standardised_network_provided_station_classification':EEA_rural_station_types_to_include,
                'standardised_network_provided_area_classification':EEA_rural_area_types_to_include}

MBlandforms_to_include = ['high altitude plains','water', 'very low plateaus',
                        'plains', 'rugged lowlands','hills','high altitude plateaus',
                        'mid altitude plateaus', 'nan','lowlands', 'mid altitude plains',
                        'low plateaus']

mountain_filter = {'altitude':[-20,1500],
                   'ESDAC_Meybeck_landform_classification':MBlandforms_to_include}

data = data.apply_filters(**rural_filter)
stats = data.to_station_data_all()['stats']

rh = {'conco3': {'daily': {'hourly': 'max'}}},

first_daily = stats[0].resample_time('daily')

