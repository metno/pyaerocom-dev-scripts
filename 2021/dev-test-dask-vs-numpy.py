#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 13:12:31 2021

@author: jonasg
"""

import dask.array as da
import numpy as np
import xarray as xr

nparr = np.zeros(2)
nparr[0]=42

darr = da.from_array(nparr)





