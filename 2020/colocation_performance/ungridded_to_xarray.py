#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:32:35 2020

@author: jonasg
"""
import numpy as np
import pyaerocom as pya
import xarray as xr
if __name__=='__main__':
    pya.const.GEONUM_AVAILABLE
    #modeldata = pya.io.ReadGridded('ECMWF_CAMS_REAN').read_var('od550aer')
    
    #modeldata = modeldata.to_xarray()
    data_dir = '/home/jonasg/MyPyaerocom/data/obsdata/GHOST'
# =============================================================================
#     pya.const.add_ungridded_obs('GHOST.daily', data_dir,
#                                 pya.io.ReadGhost, check_read=True)
# =============================================================================
    obsdata = pya.io.ReadUngridded().read('GHOST.daily', 
                                          'concpm10')
    
    
    yr = 2018
    freq='D'
    
    start, stop = pya.helpers.start_stop_from_year(yr)
    index = pya.helpers.make_datetime_index(start, stop, freq)
# =============================================================================
#     
#     res = obsdata.to_station_data('Cabo De Creus',
#                                   start=start, stop=stop, 
#                                   ts_type='freq',
#                                   allow_wildcards_station_name=False)
#     
# =============================================================================
    
    sname = 'Vidin 2'
    
    indices = obsdata.find_station_meta_indices(sname, 
                                                allow_wildcards=False)
    s0 = obsdata.to_station_data(indices[0])
    s1 = obsdata.to_station_data(indices[1])
    
    s1m= s1.resample_time('concpm10', 'monthly', inplace=False)
    #del s1.var_info['concpm10']['ts_type']
    #del s1['ts_type']
    #for k in range(10):
    res = s0.merge_other(s1, 'concpm10', check_overlaps=True, 
                         check_coords=False, sort_index=False,
                         is_ts_type='daily')
    
    
    #arr = np.ones((len(index)))