#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:52:42 2020

@author: jonasg
"""


import glob
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import xarray as xr
import pyaerocom as pya
from pyaerocom import const
from pyaerocom.io.readungriddedbase import ReadUngriddedBase

plt.close('all')
files = glob.glob('*.nc')

print(files)

fp = files[0]

ds = xr.open_dataset(fp)

def read_vardata_ghost(file_path, vars_to_read='sconco3'):
    reader = ReadGhost()
    return reader.read_file(file_path, vars_to_read)
    
        

stats, ds = read_vardata_ghost(fp, 'sconco3')
st = stats[0]

fig, ax = plt.subplots(2,1, sharex=True, figsize=(10, 5))
st.plot_timeseries('sconco3', ax=ax[0])

ser = deepcopy(st.sconco3)

ser[ser>900] = np.nan
ax[1].plot(ser)

class ReadGhost(ReadUngriddedBase):
    """Reading interface for GHOST data"""
    __version__ = '0.0.1'
    
    _FILEMASK = '*.nc'
    
    DATA_ID='GHOST'
    
    SUPPORTED_DATASETS = ['GHOST']
    
    DEFAULT_VARS = ['sconco3']
    
    TS_TYPE = 'hourly'
    
    def read_file(self, filename, vars_to_retrieve):
        """Read GHOST NetCDF data file
        
        Parameters
        ----------
        filename : str
            absolute path to filename to read
        vars_to_retrieve : list, optional
            list of strings with variable names to read
            
        Returns
        -------
        list
            list of loaded `StationData` objects
        
        """
        ds = xr.load_dataset(filename)
    
        if isinstance(vars_to_retrieve, str):
            vars_to_retrieve = [vars_to_retrieve]
        vars_avail = list(ds.variables)
        use_vars = [x for x in vars_to_retrieve if x in vars_avail]
        
        if len(use_vars) == 0:
            const.print_log.info('File {} does not contain any of the input '
                                 'variables {}'.format(filename, 
                                                       vars_to_retrieve))
            return []
        
        if not all(x in ds.dims for x in ['station', 'time']):
            raise AttributeError("Missing dimensions")
        if not 'station_name' in ds:
            raise AttributeError('No variable station_name found')
        
        
            
        stats = []
        
        meta_vars_stats = []
        
        for meta_name in list(ds.variables):
            metadata = ds[meta_name]
            if len(metadata.dims) == 1 and metadata.dims[0] == 'station':
                meta_vars_stats.append(meta_name)
                
        tvals = ds['time'].values
        
        for idx in ds.station.values:
            stat = pya.StationData()
            
            stat['dtime'] = tvals
            
            for meta_name in meta_vars_stats:
                val = ds[meta_name].isel(station=idx).values 
                try:
                    val = float(val)
                except:
                    val = str(val)
                stat[meta_name] = val
            for var_name in use_vars:
                stat.var_info[var_name] = vi = {}
                sd = vardata.isel(station=idx)
                vi.update(sd.attrs)
            
            stat[var_name] = sd.values
            stats.append(stat)
        return stats
    
    @property
    def PROVIDES_VARIABLES(self):
        raise NotImplementedError('Maybe needed, maybe not')
    
    def read(self, vars_to_retrieve):
        raise NotImplementedError
        
        
    def _add_station_data_to_ungridded(self, station_data, ungridded):
        raise NotImplementedError
    

        





    