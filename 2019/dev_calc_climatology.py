import pyaerocom as pya
import matplotlib.pyplot as plt

plt.close('all')
print(pya.const.has_access_lustre)
import pandas as pd
import numpy as np

r = pya.io.ReadUngridded()

var = 'scatc550dryaer'
data= r.read('EBASMC',
            vars_to_retrieve=var)


stat = data.to_station_data('Bondville')
stat.plot_timeseries(var)

start = pya.const.CLIM_START
stop = pya.const.CLIM_STOP

ts = stat.to_timeseries(var)



### USE HELPER METHOD

#clim['num'] = clim.groupby('month').count()
clim = pya.helpers.calc_climatology(ts, start, stop, 5)

fig, ax = plt.subplots(1,1,figsize=(16,8))

ax.errorbar(clim['data'].index, clim['data'], clim['std'],c='#cccccc', 
            marker='', ls='')
pp = ax.scatter(clim.index, clim['data'], s=100, c=clim['numobs'])

fig.colorbar(pp, ax=ax)
ax.set_title('Lowlevel')

low = clim['data'] - clim['std']
high = clim['data'] + clim['std']
#ax.fill_between(low.index, low.data, high.data, alpha=0.1)



### TEST IMPLEMENTATION IN STATIONDATA

new = stat.calc_climatology(var)

fig, ax = plt.subplots(1,1,figsize=(16,8))

data = new[var]
ax.errorbar(data.index, data, new.data_err[var],c='#cccccc', 
            marker='', ls='')
pp = ax.scatter(data.index, data, s=100, c=new.numobs[var])

fig.colorbar(pp, ax=ax)
ax.set_title('Stationdata')

new.plot_timeseries(var)


### CHECK BASED ON DAILY

if not isinstance(start, pd.Timestamp):
    start, stop = pya.helpers.start_stop(start, stop)
sc = ts[start:stop]
sc.dropna(inplace=True)

if len(sc) == 0:
    raise ValueError('Cropping input time series in climatological '
                     'interval resulted in empty series')

df = pd.DataFrame(sc)
df['month'] = df.index.month


clim = df.groupby('month').agg(['mean', 'std','count'])

#clim.columns = clim.columns.droplevel(0)
clim.columns = ['data', 'std', 'numobs']
idx = [np.datetime64('{}-{:02d}-15'.format(2010, x)) for x in 
       clim.index.values]
clim.set_index(pd.DatetimeIndex(idx), inplace=True)
