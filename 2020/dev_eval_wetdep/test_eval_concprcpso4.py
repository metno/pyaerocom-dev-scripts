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


mid = 'EMEP-cams50-u3all'
mid = 'MINNI.cams61.rerun'

reader = pya.io.ReadGridded(mid)
print(reader)
#data = reader.read_var('vmrnh3')

raise Exception
vmin, vmax = 0, 1e10 #1000, 1e7
obs = pya.io.ReadUngridded().read('EBASMC', 'concprcpso4')
obs.remove_outliers('concprcpno3', inplace=True, low=vmin, high=vmax,
                    unit_ref='ug N m-3')
obs = obs.apply_filters(set_flags_nan=True, ts_type='daily',
                        data_level=2)

print('Successfully imported obsdata')

aux_add_args = [
    dict(ts_type='monthly',
         prlim=None,
         prlim_units='mm d-1',
         prlim_set_under=np.nan),

    dict(ts_type='monthly',
         prlim=0.1e-3,
         prlim_units='m d-1',
         prlim_set_under=np.nan),

    dict(ts_type='monthly',
         prlim=0.1e-3,
         prlim_units='m d-1',
         prlim_set_under=0),

    dict(ts_type='daily',
         prlim=None,
         prlim_units='mm d-1',
         prlim_set_under=np.nan),

    dict(ts_type='daily',
         prlim=0.1e-3,
         prlim_units='m d-1',
         prlim_set_under=np.nan),

    dict(ts_type='daily',
         prlim=0.1e-3,
         prlim_units='m d-1',
         prlim_set_under=0)
]
# =============================================================================
#
# model = reader.read_var('concprcpoxn',
#                             try_convert_units=False,
#                             aux_add_args=aux_add_args[0])
# =============================================================================

titels = ['No PR lim', 'PR-lim=0.1mm/d (repl. w. NaN)',
          'PR-lim=0.1mm/d (repl. w. 0)', '','','']

xlabel = 'EBAS (lev2, only daily, flags invalidated)'
fig, axes = plt.subplots(2, 3, figsize=(18,12),
                         sharey=True)

axes=axes.flatten()

for i, add_args in enumerate(aux_add_args):
    ax = axes[i]
    ts_type = add_args['ts_type']
    model = reader.read_var('concprcpoxn',
                            try_convert_units=False,
                            aux_add_args=add_args)




    print('Successfully imported modeldata')
    coldata = pya.colocation.colocate_gridded_ungridded(model, obs,
                                                        ts_type=ts_type,

                                                        var_ref='concprcpno3')


    coldata.plot_scatter(loglog=True, ax=ax)
    if i%3!=0:
        ax.set_ylabel('')
    ax.set_xlim([vmin, vmax])
    ax.set_ylim([vmin, vmax])
    ax.set_xlabel(xlabel)
    ax.set_title(titels[i])

plt.tight_layout()

fig.savefig(f'{mid}_wdepoxn_daily_eval.png')