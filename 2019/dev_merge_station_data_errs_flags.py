import pyaerocom as pya
import numpy as np
import matplotlib.pyplot as plt
from time import time

plt.close('all')

scat_all = pya.io.ReadUngridded().read('EBASMC', 'scatc550aer')

subset = scat_all.filter_by_meta(datalevel=2)

subset1 = subset.set_flags_nan(inplace=False).remove_outliers('scatc550aer')


subset.plot_station_timeseries('Birken*', 'scatc550aer')


subset1.plot_station_timeseries('Birken*', 'scatc550aer')

print(np.nanmean(subset._data[:, 6]))
print(np.nanmean(subset1._data[:, 6]))

print(subset1)

stat = subset.to_station_data('Birk*')