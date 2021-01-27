#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 15:52:17 2020

@author: jonasg
"""

import pyaerocom as pya

aux_info_vmrox = dict(

EBAS = dict(
    obs_id='EBAS',
    obs_vars=['vmrox'],
    obs_type='ungridded',
    obs_merge_how={'vmrox' : 'eval'},
    obs_aux_requires = {'vmrox' : {'EBASMC' : ['vmro3', 'vmrno2']}},
    obs_aux_funs = {'vmrox' : 'EBASMC;vmro3+EBASMC;vmrno2'},
    obs_aux_units = {'vmrox' : 'mol mol-1'}
),

GHOST = dict(
    obs_id='GHOST',
    obs_vars=['vmrox'],
    obs_type='ungridded',
    obs_merge_how={'vmrox' : 'eval'},
    obs_aux_requires = {'vmrox' : {'GHOST.EEA.daily' : ['vmro3', 'vmrno2']}},
    obs_aux_funs = {'vmrox' : 'GHOST.EEA.daily;vmro3+GHOST.EEA.daily;vmrno2'},
    obs_aux_units = {'vmrox' : 'mol mol-1'}
)
)

assert pya.const.has_access_lustre


mid = 'EMEP.cams61.rerun'


#vmrno2 = pya.io.ReadUngridded().read('EBASMC', 'vmrno2')
for name, info in aux_info_vmrox.items():
    pya.const.add_ungridded_post_dataset(**info)

obs_reader = pya.io.ReadUngridded()

ghost = obs_reader.read('GHOST', 'vmrox')
print(ghost)
#ebas = obs_reader.read('EBAS', 'vmrox')
#print(ebas)


mdata = pya.io.ReadGridded(mid).read_var('vmrox',vert_which='Surface')
mdata = mdata.resample_time('daily')
print(mdata)
coldata = pya.colocation.colocate_gridded_ungridded(mdata, ghost,
                                                    ts_type='daily')

coldata.plot_scatter()






