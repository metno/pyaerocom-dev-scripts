import pyaerocom as pya
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.axes import Axes
from cartopy.mpl.geoaxes import GeoAxes
import geojsoncontour

GeoAxes._pcolormesh_patched = Axes.pcolormesh
plt.style.use('ggplot')

modid = 'OsloCTM3v1.01-met2010_AP3-CTRL'
var = 'ec550dryaer'
reader = pya.io.ReadGridded(modid)

data = reader.read_var(var, start=2010,
                       ts_type='monthly',
                       vert_which='Surface').resample_time('monthly')

vardef = pya.const.VARS[var]

data.check_unit()

cmap = 'Reds'
nlayers = 20

MAP_COLOR_LIMS = {
    'ec550dryaer' : [0, 1000]
    }

if var in MAP_COLOR_LIMS:
    map_vmin, map_vmax = MAP_COLOR_LIMS[var]
else:
    map_vmin, map_vmax = vardef.map_vmin, vardef.map_vmax

if any([x is None for x in [map_vmin, map_vmax]]):
    raise ValueError

cm=plt.cm.get_cmap('Reds',nlayers)
levels = np.linspace(map_vmin, map_vmax, nlayers)

proj = ccrs.PlateCarree()
ax = plt.axes(projection=proj)

csf = {}

if not data.check_dimcoords_tseries():
    data.reorder_dimensions_tseries()

nparr = data.cube.data
lats = data.latitude.points
lons = data.longitude.points

geojson = {}

for i, month in enumerate(data.time_stamps()):
    date = str(month).split('T')[0]
    datamon = nparr[i]
    contour = ax.contourf(lons, lats, datamon,
                          transform=proj,
                          cmap=cm,
                          levels=levels,
                          extend='max')

    result = geojsoncontour.contourf_to_geojson(
                contourf=contour,
                ndigits=2,
                unit='m'
                )

    geojson[date] = eval(result)

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




