#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 15:32:58 2021

@author: jonasg
"""
import matplotlib.pyplot as plt
import numpy as np
import os

plt.close('all')
import pyaerocom as pya

pya.const.add_data_search_dir(pya.const.OUTPUTDIR + '/data/modeldata')

ebas_local = os.path.join(pya.const.OUTPUTDIR, 'data/obsdata/EBASMultiColumn/data')

obs_id = 'EBASMC'
obs_var = 'wetoxs'

model_id = 'LOTOSEUROS_CAMS61'
model_id = 'EMEP-cams50-u3all'

model_var = 'wetoxs'

yr=2018
colfreq = 'monthly'
colocate_time = True

model_constraints = None #[{'operator'      : '<=', 'filter_val'    : 0}]


min_num_obs = {'yearly': {'monthly': 9},
               'monthly': {'daily': 4,'weekly' : 1},
               'daily': {'hourly': 18},
               'hourly': {'minutely': 45}}

remove_outliers=True

var_ref_outlier_ranges = {'conctno3':(-1e9,1e9),'conctnh':(-1e9,1e9),
                          'concso4':(-1e9,1e9),'concnh3':(-1e9,1e9),
                          'concnh4':(-1e9,1e9),
                          'conchno3':(-1e9,1e9),'concno310':(-1e9,1e9),
                          'concno325':(-1e9,1e9),
                          'concss10':(-1e9,1e9),'concss25':(0,1e9),
                          'concec':(-1e9,1e9),'conccoc':(-1e9,1e9)},

reader = pya.io.ReadUngridded(obs_id, data_dir=ebas_local)


obsdata = reader.read(vars_to_retrieve=[obs_var])
obsdata = obsdata.apply_filters(data_level=2,
                                set_flags_nan=True,
                                #ts_type='daily'
                                )

res = {}
count = {}
obsst = None
for key, val in obsdata.metadata.items():
    tst = val['ts_type']
    unit = val['var_info'][obs_var]['units']
    if not tst in res:
        res[tst] = unit
        count[tst] = 0
    elif not res[tst] == unit:
        raise Exception('NOOOOO')
    else:
        count[tst] += 1
    if tst == 'daily' and obsst is None:
        try:
            obsst = obsdata.to_station_data(key,
                                            vars_to_convert=obs_var,
                                            start=yr)
        except:
            pass

print(obsst)

print(res)
print(count)


model_reader = pya.io.ReadGridded(model_id)

if model_constraints is None:
    cst = 'KEEP_ZEROS'
else:
    cst = 'ZEROS_TO_NAN'

wetoxs = model_reader.read_var(model_var, start=yr,
                               constraints=model_constraints)

coldata = pya.colocation.colocate_gridded_ungridded(wetoxs, obsdata,
                                                    ts_type=colfreq,
                                                    var_ref=obs_var,
                                                    colocate_time=True,
                                                    min_num_obs=min_num_obs,
                                                    remove_outliers=True,
                                                    harmonise_units=True)

ax = coldata.plot_scatter(loglog=True)


fname = f'scatter_{model_id}-{model_var}_{obs_id}-{obs_var}_{yr}_{colfreq}_{cst}.png'

print(fname)

ax.figure.tight_layout()
ax.figure.savefig(os.path.join(pya.const.OUTPUTDIR, f'output/{fname}'))
