import pyaerocom as pya
import numpy as np
import matplotlib.pyplot as plt
from time import time

plt.close('all')

scat_all = pya.io.ReadUngridded().read('EBASMC', 'scatc550aer')

r = pya.io.ReadEbas()

# Bir*, scatc550dryaer
#files = r.get_file_list('scatc550dryaer', station_names='Bir*')

files = ['/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20090708000000.20181031145000.nephelometer..pm10.6mo.1h.NO01L_TSI3563_70810508.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20100101000000.20150309134342.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20110101000000.20150309134342.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20120101000000.20150309134342.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20130101000000.20150309134342.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20140101000000.20150615082702.optical_particle_size_spectrometer...1y.1h.NO01L_Grimm_190_BIR_dry.NO01L_OPC_PM.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20140101000000.20180619104205.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20150101000000.20180619104205.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20160101000000.20180619104205.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas', '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/EBASMultiColumn/data/data/NO0002R.20170101000000.20180522133330.nephelometer..pm10.1y.1h.NO01L_TSI_3563_BIR_dry.NO01L_scat_coef.lev2.nas']


def get_data(data, var, meta_idx):
    return data._data[data.meta_idx[meta_idx][var], data._DATAINDEX]

def get_data_no_meta_idx(data, var, meta_idx):
    
    var_idx = data.var_idx[var]

    meta_mask = data._data[:, data._METADATAKEYINDEX] == meta_idx
    subset = data._data[meta_mask]

    var_mask = subset[:, data._VARINDEX] == var_idx
    return subset[var_mask][:, data._DATAINDEX]
    

r.files = files

data = r.read(['scatc550dryaer', 'scatc550aer'], files=files)
raise Exception
VAR = 'scatc550aer'
META_IDX = 1
#stat = data.to_station_data_all('scatc550dryaer')['stats'][0]

t0 = time()

d0 = get_data(data, VAR, META_IDX)

t1=time()

d1 = get_data_no_meta_idx(data, VAR, META_IDX)
t2 =time()
assert np.nansum(d1 - d0) == 0

print(t1-t0, 's')
print(t2-t1, 's')


t3 = time()

d2 = get_data(scat_all, VAR, 100)

t4 = time()

d3 = get_data_no_meta_idx(scat_all, VAR, 100)
t5 =time()
assert np.nansum(d1 - d0) == 0

print(t4-t3, 's')
print(t5-t4, 's')


stat = data.to_station_data('Bir*', 'scatc550dryaer')

