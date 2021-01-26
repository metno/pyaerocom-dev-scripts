#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example station data design
"""
import numpy as np
import pandas as pd
import pyaerocom as pya

time = np.arange(100).astype('datetime64[s]') # INDEX NEEDS TO BE IN UNITS OF s

example_statdata = dict() # pya.StationData()

example_statdata['data_id'] = 'CHINA_DATASET_NAME'
example_statdata['station_name'] = 'USE_ID' # because the names are in mandarin
example_statdata['latitude'] = 20
example_statdata['longitude'] = 100
example_statdata['altitude'] = 100 # in units of m

example_statdata['ts_type'] = 'hourly'

example_statdata['var_info'] = dict()

# Then, for each variable
example_statdata['vmrso2'] = pd.Series(np.ones_like(time), time)

# for each variable, there needs to be an entry in the var_info dict
example_statdata['var_info']['vmrso2'] = dict()
example_statdata['var_info']['vmrso2']['units'] = 'BEST_GUESS' # e.g. nmole mole-1

def method_dummy_that_reads_all(filepaths,
                                vars_to_retrieve=None):
    stats = []
    # code that loops over all files, identifies all unique site locations,
    # and stitches variable timeseries and station metadata together into
    # individual StationData dictionaries (see above) and appends them to
    # stats, which is returned.
    return stats


