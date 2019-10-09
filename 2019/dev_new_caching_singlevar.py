import pyaerocom as pya
import numpy as np

import matplotlib.pyplot as plt

plt.close('all')

r = pya.io.ReadUngridded()

data= r.read('AeronetSunV3Lev2.daily',
            vars_to_retrieve=['od550aer', 'ang4487aer'],
            file_pattern='Bo*')

data._check_index()

VAR = 'od550aer'
var_idx = data.var_idx[VAR]

totnum = np.sum(data._data[:, data._VARINDEX] == var_idx)

colnum, rownum = data.shape

if rownum != len(data._init_index()):
    raise NotImplementedError('Cannot split UngriddedData objects that have '
                              'additional columns other than default columns')
    
aod = data.extract_var('od550aer')

ax = data['Bozeman'].plot_timeseries('od550aer')

aod['Bozeman'].plot_timeseries('od550aer', ax=ax)


cache = pya.io.cachehandler_ungriddedDEV.CacheHandlerUngridded(r)
print(cache)

