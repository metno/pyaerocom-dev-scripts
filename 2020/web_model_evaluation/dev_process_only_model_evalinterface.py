#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 09:22:52 2020

@author: jonasg
"""
import os

import numpy as np
import pandas as pd

import pyaerocom as pya


def griddeddata_to_jsondict(model_id, var_name='od550aer', 
                            start=2010, lat_res=5, lon_res=5,
                            ts_type='monthly', outdir=None):
    r = pya.io.ReadGridded(model_id)
    
    data = r.read_var(var_name, start=start)
    
    data = data.regrid(lat_res_deg=lat_res, lon_res_deg=lon_res)
    data = data.resample_time(ts_type)
    
    arr = data.to_xarray()
    latname, lonname = 'lat', 'lon'
    try:
        stacked = arr.stack(station_name=(latname, lonname))
        
    except:
        latname, lonname = 'latitude', 'longitude'
        stacked = arr.stack(station_name=(latname, lonname))
    
    dd = {}
    from time import time
    
    t0 = time()
    
    dd['time'] = [pd.to_datetime(t).strftime('%Y-%m-%d') for t in data.time_stamps()]
    
    for i, stat in enumerate(stacked.station_name.values):
        
        lat = np.float64(stacked.lat[i].values)
        lon = np.float64(stacked.lon[i].values)
        
        
        d = stacked.sel(station_name=stat).values
        dd[str(stat)] = sd = {}
        sd['lat'] = lat
        sd['lon'] = lon
        sd['data'] = d.tolist()

    print(time() - t0, 's')        
    
    
    modname = model_id
    name = '{}_Column_MOD-{}:{}.json'.format(var_name, modname, var_name)
    
    if outdir is None:
        outdir = '.'
    
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    pya.io.helpers.save_dict_json(dd, os.path.join(outdir, name))


if __name__ == '__main__':
    
    
    
    model_ids = ['EMEP_rv4_33_Glob-CTRL']
    
    res = [1,2]
    for _res in res:
        outdir = './res_{}deg'.format(_res)
        for model in model_ids:
            griddeddata_to_jsondict(model, outdir=outdir,
                                    lat_res=_res, lon_res=_res)
    
    

        