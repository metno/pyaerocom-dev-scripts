#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:54:59 2020

@author: jonasg
"""
import os
import numpy as np
import simplejson
from pyaerocom import const
from pyaerocom.web.const import HEATMAP_FILENAME_EVAL_IFACE
from pyaerocom.colocateddata import ColocatedData
from pyaerocom.mathutils import calc_statistics
from pyaerocom.exceptions import DataDimensionError
from pyaerocom.region import (get_all_default_region_ids,
                              find_closest_region_coord)
from pyaerocom.web.helpers_evaluation_iface import (add_entry_heatmap_json,
                                                    get_json_mapname,
                                                    _write_stationdata_json,
                                                    compute_json_files_from_colocateddata)
from pyaerocom import __version__ as pyaerocom_version

def compute_json_files_from_colocateddata_v0(coldata, obs_name, 
                                          model_name, use_weights,
                                          colocation_settings,
                                          vert_code, out_dirs):
    
    """Creates all json files for one ColocatedData object
    
    First version
    """
    if not isinstance(coldata, ColocatedData):
        raise ValueError('Need ColocatedData object, got {}'
                         .format(type(coldata)))
    stats_dummy = {}
    
    for k in calc_statistics([1], [1]):
        stats_dummy[k] = np.nan
    
    stacked = False
    if 'altitude' in coldata.data.dims:
        raise NotImplementedError('Cannot yet handle profile data')
    if not 'station_name' in coldata.data.coords:
        if not coldata.data.ndim == 4:
            raise DataDimensionError('Invalid number of dimensions. '
                                     'Need 4, got: {}'
                                     .format(coldata.data.dims))
        elif not 'latitude' in coldata.data.dims and 'longitude' in coldata.data.dims:
            raise DataDimensionError('Need latitude and longitude '
                                     'dimension. Got {}'
                                     .format(coldata.data.dims))
        coldata.data = coldata.data.stack(station_name=('latitude', 
                                                        'longitude'))
        stacked = True
        
    ts_types_order = const.GRID_IO.TS_TYPES
    to_ts_types = ['daily', 'monthly', 'yearly']
    
    data_arrs = dict.fromkeys(to_ts_types)
    jsdate = dict.fromkeys(to_ts_types)
    
    ts_type = coldata.meta['ts_type']
    for freq in to_ts_types:
        if ts_types_order.index(freq) < ts_types_order.index(ts_type):
            data_arrs[freq] = None
        elif ts_types_order.index(freq) == ts_types_order.index(ts_type):
            data_arrs[freq] = coldata.data
            
            js = (coldata.data.time.values.astype('datetime64[s]') - 
                  np.datetime64('1970', '[s]')).astype(int) * 1000
            jsdate[freq] = js.tolist()
            
        else:
            colstp = colocation_settings
            _a = coldata.resample_time(to_ts_type=freq,
                                 apply_constraints=colstp.apply_time_resampling_constraints, 
                                 min_num_obs=colstp.min_num_obs,
                                 colocate_time=colstp.colocate_time,
                                 inplace=False).data
            data_arrs[freq] = _a #= resample_time_dataarray(arr, freq=freq)
            js = (_a.time.values.astype('datetime64[s]') - 
                  np.datetime64('1970', '[s]')).astype(int) * 1000
            jsdate[freq] = js.tolist()      
    
    #print(jsdate)

    obs_id = coldata.meta['data_source'][0]
    model_id = coldata.meta['data_source'][1]
    
    obs_var = coldata.meta['var_name'][0]
    model_var = coldata.meta['var_name'][1]
    
    ts_objs = []
    
    map_data = []
    scat_data = {}
    hm_data = {}
    
    # data used for heatmap display in interface
    if stacked:    
        hmd = ColocatedData(data_arrs[ts_type].unstack('station_name'))
    else:
        hmd = ColocatedData(data_arrs[ts_type])

    for reg in get_all_default_region_ids():
        filtered = hmd.filter_region(region_id=reg)
        stats = filtered.calc_statistics(use_area_weights=use_weights)
        for k, v in stats.items():
            if not k=='NOTE':
                v = np.float64(v)
            stats[k] = v
        
        hm_data[reg] = stats
    
    hm_file = os.path.join(out_dirs['hm'], HEATMAP_FILENAME_EVAL_IFACE)
    
    add_entry_heatmap_json(hm_file, hm_data, obs_name, obs_var, vert_code, 
                           model_name, model_var)
    
    if vert_code == 'ModelLevel':
        raise NotImplementedError('Coming soon...')
    const.print_log.info('Computing json files for {} vs. {}'
                         .format(model_name, obs_name))
    
    for i, stat_name in enumerate(coldata.data.station_name.values):
        has_data = False
        ts_data = {}
        ts_data['station_name'] = stat_name
        ts_data['pyaerocom_version'] = pyaerocom_version
        ts_data['obs_name'] = obs_name
        ts_data['model_name'] = model_name
        ts_data['obs_var'] = coldata.meta['var_name'][0]
        ts_data['obs_unit'] = coldata.meta['var_units'][0]
        ts_data['vert_code'] = vert_code
        ts_data['obs_freq_src'] = coldata.meta['ts_type_src'][0]
        ts_data['obs_revision'] = coldata.meta['revision_ref']
        
        ts_data['mod_var'] = coldata.meta['var_name'][1]
        ts_data['mod_unit'] = coldata.meta['var_units'][1]
        ts_data['mod_freq_src'] = coldata.meta['ts_type_src'][1]
        
        stat_lat = np.float64(coldata.data.latitude[i])
        stat_lon = np.float64(coldata.data.longitude[i])
        if 'altitude' in coldata.data.coords:
            stat_alt = np.float64(coldata.data.altitude[i])
        else:
            stat_alt = np.nan
        region = find_closest_region_coord(stat_lat, stat_lon)
        
        # station information for map view
        map_stat = {'site'      : stat_name, 
                    'lat'       : stat_lat, 
                    'lon'       : stat_lon,
                    'alt'       : stat_alt,
                    'region'    : region}
        
        for tres, arr in data_arrs.items():
            map_stat['{}_statistics'.format(tres)] = {}
            if arr is None:
                ts_data['{}_date'.format(tres)] = []
                ts_data['{}_obs'.format(tres)] = []
                ts_data['{}_mod'.format(tres)] = []
                map_stat['{}_statistics'.format(tres)].update(stats_dummy)
                continue
    
            obs_vals = arr.sel(data_source=obs_id, 
                               station_name=stat_name).values

            if all(np.isnan(obs_vals)):
                ts_data['{}_date'.format(tres)] = []
                ts_data['{}_obs'.format(tres)] = []
                ts_data['{}_mod'.format(tres)] = []
                map_stat['{}_statistics'.format(tres)].update(stats_dummy)
                continue
            has_data = True
            mod_vals = arr.sel(data_source=model_id, 
                               station_name=stat_name).values
            
            if not len(jsdate[tres]) == len(obs_vals):
                raise Exception('Please debug...')
            
            ts_data['{}_date'.format(tres)] = jsdate[tres]
            ts_data['{}_obs'.format(tres)] = obs_vals.tolist()
            ts_data['{}_mod'.format(tres)] = mod_vals.tolist()
            
            station_statistics = calc_statistics(mod_vals, obs_vals)
            for k, v in station_statistics.items():
                station_statistics[k] = np.float64(v)
            map_stat['{}_statistics'.format(tres)] = station_statistics
        
        if has_data:
            ts_objs.append(ts_data)
            map_data.append(map_stat)
            scat_data[str(stat_name)] = sc = {}
            sc['obs'] = ts_data['monthly_obs']
            sc['mod'] = ts_data['monthly_mod']
            sc['region'] = region
        
    dirs = out_dirs

    map_name = get_json_mapname(obs_name, obs_var, model_name, 
                                model_var, vert_code)
    
    outfile_map =  os.path.join(dirs['map'], map_name)
    with open(outfile_map, 'w') as f:
        simplejson.dump(map_data, f, ignore_nan=True)
    
    outfile_scat =  os.path.join(dirs['scat'], map_name)
    with open(outfile_scat, 'w') as f:
        simplejson.dump(scat_data, f, ignore_nan=True)
        
    for ts_data in ts_objs:
        #writes json file
        _write_stationdata_json(ts_data, out_dirs)
        
if __name__ == '__main__':
    import pyaerocom as pya
    stp = pya.web.AerocomEvaluation('test', 'test')
    
    #colfile = '/home/jonasg/github/aerocom_evaluation/coldata/PIII-optics2019-P/AEROCOM-MEDIAN_AP3-CTRL/od550aer_REF-AeronetSun_MOD-AEROCOM-MEDIAN_20100101_20101231_monthly_WORLD-noMOUNTAINS.nc'
    colfile = '/home/jonasg/github/aerocom_evaluation/coldata/PIII-optics2019-P/AEROCOM-MEDIAN_AP3-CTRL/od550aer_REF-AATSR4.3-SU_MOD-AEROCOM-MEDIAN_20100101_20101231_monthly_WORLD-noMOUNTAINS.nc'
    
    coldata = ColocatedData(colfile)
    out_dirs = stp.out_dirs
    obs_name, model_name = coldata.meta['data_source']
    compute_json_files_from_colocateddata_v0(coldata, obs_name, 
                                          model_name, 
                                          use_weights=False,
                                          colocation_settings=stp.colocation_settings,
                                          vert_code='Column', 
                                          out_dirs=out_dirs)
    
    coldata = ColocatedData(colfile)
    compute_json_files_from_colocateddata(coldata, obs_name, 
                                          model_name, 
                                          use_weights=False,
                                          colocation_settings=stp.colocation_settings,
                                          vert_code='Column', 
                                          out_dirs=out_dirs)