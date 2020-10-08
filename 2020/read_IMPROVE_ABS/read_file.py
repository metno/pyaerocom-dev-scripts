#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 12:03:12 2020

@author: jonasg
"""

import glob
import numpy as np
import pandas as pd
import pyaerocom as pya

FILE_MASK = '*.txt'
DATA_DIR = '/home/jonasg/MyPyaerocom/data/obsdata/IMPROVE/'
COL_DELIM = ';'
files = glob.glob('{}{}'.format(DATA_DIR, FILE_MASK))

fp = files[0]
    
sections = ['Overview', 'Datasets', 'Sites', 'Parameters', 
            'Site History', 'Dataset History', 'Status Flags',
            'Data']

rename_head = {
    'site'      : 'station_name',
    'elevation' : 'altitude',
    'frequency' : 'ts_type', 
    'sitename'  : 'station_name'}

data_colnames = ['date', 'station_name', 'latitude', 'longitude',
                 'altitude']


var_names = {'ac550aer' :   'fAbs'}


convert = {'latitude' : np.float64,
           'longitude' : np.float64,
           'altitude' : np.float64}

sect_idx = -1

headers = {}
sites = {}
sc = 0 # section line counter
sect = None

site_id = 'station_name'

def update_col_index(head, var_info, col_index):
    
    return col_index

def get_val(key, val):
    if key in convert:
        return convert[key](val)
    return val

def add_site_info(line, head):
    add = {}
    spl = line.split(COL_DELIM)
    if not len(spl) == len(head):
        raise IOError('NEED ANOTHER DELIMITER THAN {}'.format(COL_DELIM))
# =============================================================================
#         iter = zip(head[:14], spl[:14])
#     else:
#         pass
# =============================================================================
    iter = zip(head, spl)
    for key, val in iter:
        add[key] = get_val(key, val) #convert[key](val)
        
    return add
     
lc = -1
INDATA = False
var_info = {}
add_var_info = {'wavelength_nm' : 633}
datasets = {}
col_index = {}

with open(fp, 'r') as f:
    for line in f:
        lc += 1
        sc += 1
        line = line.strip()
        
        if INDATA:
            spl = line.split(COL_DELIM)
            if not len(spl) == len(head):
                raise IOError('NEED ANOTHER DELIMITER THAN {}'.format(COL_DELIM))
            continue
        
        elif not line:
            continue
        
        if sc == 2 and sect is not None:
            head = [x.lower().strip() for x in line.split(COL_DELIM)]
            for i, s in enumerate(head):
                if s in rename_head:
                    head[i] = rename_head[s]
            headers[sect] = head
            if sect == 'Data':
                print('Entering data block, line', lc)
                col_index = update_col_index(head, var_info, col_index)
                INDATA = True
                
        elif line == sections[sect_idx + 1]:
            sect_idx += 1
            sc = 0
            sect = line # sections[sect_idx]
            print('Enter ', line)
            continue
            
        elif sect == 'Sites':
            add = add_site_info(line, headers[sect])
            site_name = add[site_id]
            sites[site_name] = add
       
        elif sect == 'Parameters':
            head = headers[sect]
            spl = line.split(COL_DELIM)
            var_idx = head.index('code')
            var_name = spl[var_idx]
            var_info[var_name] = {}
            if len(head) == len(spl):
                for key, val in zip(head, spl):
                    var_info[var_name][key] = get_val(key, val)
            var_info[var_name].update(add_var_info)
            
        elif sect == 'Datasets':
            head = headers[sect]
            spl = line.split(COL_DELIM)
            ds = spl[0]
            if ds in datasets:
                raise Exception('DEBUG: Definition of dataset {} occured twice'.format(ds))
            datasets[ds] = {}
            if len(spl) == len(head):
                for key, val in zip(head, spl):
                    if key=='ts_type':
                        val = val.lower()
                    else:
                        val = get_val(key, val)
                    datasets[ds][key] = val
           
        
    
            
        
        
            
         