#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 09:44:21 2020

@author: jonasg
"""

import pyaerocom as pya

assert pya.const.has_access_lustre

obs = pya.io.ReadUngridded().read('EBASMC','concpm25')
mod = pya.io.ReadGridded('EMEP.cams61.rerun').read_var('concpm25',
                                                       vert_which='Surface')
obs.set_flags_nan(inplace=True)
col = pya.colocation.colocate_gridded_ungridded(mod, obs,
                                                ts_type='daily',
                                                start=2018,
                                                stop=2019)