#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 10:14:00 2020

@author: jonasg
"""
import matplotlib.pyplot as plt
import numpy as np
from cf_units import Unit
plt.close('all')
import pyaerocom as pya

#pya.const.__init__(config_file=pya.const._config_ini_localdb)
local_models = '/home/jonasg/MyPyaerocom/data/modeldata'
pya.const.add_data_search_dir(local_models)

aux_add_args = dict(
    ts_type='daily',
    prlim=0.1e-3,
    prlim_unit='m d-1',
    prlim_set_under=np.nan)

obs = pya.io.ReadUngridded().read('EBASMC', 'concprcpno3')

vmin, vmax = 1000, 1e7

obs.remove_outliers('concprcpno3', inplace=True, low=vmin, high=vmax,
                    unit_ref='ug N m-3')

obs = obs.apply_filters(set_flags_nan=True, ts_type='daily',
                        data_level=2)

models = ['CHIMERE.cams61.rerun', 'EMEP-cams50-u3all', 'DEHM.cams61.rerun']

fig, axes = plt.subplots(1, 3, figsize=(18,6))
axes=axes.flatten()

xlabel = 'EBAS (lev2, only daily, flags invalidated)'
for i, mid in enumerate(models):

    reader = pya.io.ReadGridded(mid)

    ax = axes[i]
    ts_type = aux_add_args['ts_type']
    model = reader.read_var('concprcpoxn',
                            try_convert_units=False,
                            aux_add_args=aux_add_args)

    coldata = pya.colocation.colocate_gridded_ungridded(model, obs,
                                                        ts_type=ts_type,
                                                        var_ref='concprcpno3')


    coldata.plot_scatter(loglog=True, ax=ax)
    ax.set_xlim([vmin, vmax])
    ax.set_ylim([vmin, vmax])
    ax.set_xlabel(xlabel)

plt.tight_layout()

fig.savefig('CAMS61_models_wdepoxn_daily_eval.png')