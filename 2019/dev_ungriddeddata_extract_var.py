import pyaerocom as pya
import numpy as np
from collections import OrderedDict as od

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
    
aod = pya.UngriddedData(totnum)

aod.var_idx[VAR] = 0
aod._index = data.index

meta_idx = -1
arr_idx = 0

for midx, didx in data.meta_idx.items():
    if VAR in didx and len(didx[VAR]) > 0:
        meta_idx += 1
        meta =  {}
        _meta = data.metadata[midx]
        meta.update(_meta)
        meta['var_info'] = od()
        meta['var_info'][VAR] = _meta['var_info'][VAR]
        meta['variables'] = [VAR]
        aod.metadata[meta_idx] = meta
        
        idx = didx[VAR]
    
        aod.meta_idx[meta_idx] = {}
        
        num_add = len(idx)
        start = arr_idx
        stop = arr_idx + num_add
        aod.meta_idx[meta_idx][VAR] = np.arange(start, stop)
        
        
        aod._data[start:stop] = data._data[idx]
        aod._data[start:stop, aod._METADATAKEYINDEX] = meta_idx
        aod._data[start:stop, aod._VARINDEX] = 0
        
        arr_idx += num_add

aod._check_index()

ax = data['Bozeman'].plot_timeseries('od550aer')

aod['Bozeman'].plot_timeseries('od550aer', ax=ax)
