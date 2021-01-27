#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyaerocom as pya
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns
from matplotlib.axes import Axes
from cartopy.mpl.geoaxes import GeoAxes
GeoAxes._pcolormesh_patched = Axes.pcolormesh
plt.style.use('ggplot')


# In[2]:


pya.browse_database('CAM5*-Oslo*')


# In[ ]:


modid = 'CAM5.3-Oslo_CTRL2016'
var = 'ang4487aer'#'ang4487aer'#'od550aer'
year = 2010
reader = pya.io.ReadGridded(modid)

#read variable
data = reader.read_var(var, start=year)
np.shape(data.data)

#crop in time and monthly average
data_year = data.resample_time('monthly').to_xarray()


# In[ ]:


#writ data as pickle
import pickle
with open(var+'-'+modid+'.pickle', 'wb') as handle:
    pickle.dump(data_year, handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[126]:


#plot parameters
nlayers = 20
if var=='od550aer':
    cm=plt.cm.get_cmap('Reds',nlayers)
    levels = np.linspace(0,1,nlayers)
if var=='ang4487aer':
    from matplotlib.colors import ListedColormap
    cm = ListedColormap(sns.color_palette("BrBG_r", nlayers))
    #cm=plt.cm.get_cmap('Reds',nlayers)
    levels = np.linspace(0,2,nlayers)


# In[127]:


#set projection
proj = ccrs.PlateCarree()
ax = plt.axes(projection=proj)


# In[128]:


#generate contourplot over time axis
csf = {}
for i in np.arange(np.shape(data_year)[0]):
    lon = data_year.isel(time=i).lon.data
    lat = data_year.isel(time=i).lat.data
    data = data_year.isel(time=i).data
    csf[i] = ax.contourf(lon, lat, data, transform=proj, cmap=cm, levels = levels, extend='max');

# Convert matplotlib contour to geojson
import geojsoncontour
geojson = {}
keys= ['2010-01-15','2010-02-15','2010-03-15','2010-04-15','2010-05-15','2010-06-15','2010-07-15','2010-08-15','2010-09-15','2010-10-15','2010-11-15','2010-12-15']
for i in np.arange(np.shape(data_year)[0]):
    geojson[keys[i]] = eval(geojsoncontour.contourf_to_geojson(
        contourf=csf[i],
        ndigits=2,
        unit='m'
    ))

#set the legend in one key
import matplotlib
geojson['legend'] = {
    'colors': list([matplotlib.colors.to_hex(rgba) for rgba in cm._lut][0:len(levels)]),
    'levels':  list(levels)
}

#write the file
import json
fn = var+'_Column_'+modid+'.geojson'
with open(fn,'w') as f:
    json.dump(geojson, f)


# In[ ]:




