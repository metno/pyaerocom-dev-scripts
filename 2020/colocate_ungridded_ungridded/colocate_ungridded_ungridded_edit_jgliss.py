import pyaerocom as pya
import numpy as np

from pyaerocom import const
import os

from pyaerocom.conftest import TEST_PATHS

testdatadir = (const._TESTDATADIR)
obs_path = os.path.join(testdatadir, TEST_PATHS['AeronetSunV3L2Subset.daily'])
obs_ref_path = os.path.join(testdatadir, TEST_PATHS['AeronetSDAV3L2Subset.daily'])

pya.const.add_ungridded_obs('AeronetSunV3', obs_path, reader=pya.io.ReadAeronetSunV3)
pya.const.add_ungridded_obs('AeronetSdaV3', obs_ref_path, reader=pya.io.ReadAeronetSdaV3)


var = 'od550aer'
var_ref = 'od550lt1aer'


r = pya.io.ReadUngridded('AeronetSunV3')
r_ref = pya.io.ReadUngridded('AeronetSdaV3')
obs = r.read(vars_to_retrieve=var, common_meta={'ts_type':'daily'})
obs_ref = r_ref.read(vars_to_retrieve=[var_ref, var, 'od550gt1aer'],
                     common_meta={'ts_type':'daily'})

if len(obs.contains_datasets) > 1:
    raise NotImplementedError
elif len(obs_ref.contains_datasets) > 1:
    raise NotImplementedError

dataset = obs.contains_datasets[0]
dataset_ref = obs_ref.contains_datasets[0]

idobs='{};{}'.format(dataset, var)
idref='{};{}'.format(dataset_ref, var_ref)

obs_stats = obs.to_station_data_all(var)#, start=start, stop=stop)
obs_stats['var_name'] = var
obs_stats['id'] = idobs
obs_ref_stats = obs_ref.to_station_data_all(var_ref)#, start=start, stop=stop)
obs_ref_stats['var_name'] = var_ref
obs_ref_stats['id'] = idref


if len(obs_stats['latitude']) <= len(obs_ref_stats['latitude']): #
    short = obs_stats
    long = obs_ref_stats
else:
    short = obs_ref_stats
    long = obs_stats

# order of IDs (may be needed below for some of the merging strategies)
ids = [idobs, idref]

# tolerance in km if match_stats_how is closest
tolerance = 1

match_stats_opts = ['station_name', 'closest']
match_stats_how = 'closest'

if not match_stats_how in match_stats_opts:
    raise ValueError('Invalid input for match_stats_how {}, choose from {}'
                     .format(match_stats_how, match_stats_opts))

merge_how_opts = ['combine', 'mean', 'eval']
merge_how = 'eval'

merge_eval_fun = '{}-{}'.format(idobs, idref)

# if e.g. merge_how is combine, then the preferred dataset & variable can be
# provided via this instance
prefer = idobs
var_name_out = None

if not merge_how in merge_how_opts:
    raise ValueError

elif merge_how == 'eval':
    if not isinstance(merge_eval_fun, str):
        raise ValueError('merge_eval_fun needs to be string as it is parsed '
                         'to pd.DataFrame.eval method (look it up online).')
    elif not all([x in merge_eval_fun for x in [idobs, idref]]):
        raise ValueError('merge_eval_fun needs to contain both input datasets',
                         [idobs, idref])

if var_name_out is None:
    if merge_how in ['combine', 'mean']:
        if var != var_ref:
            raise ValueError('Please provide var_name_out (since you use '
                             'combine as merge method for different variables)')
        var_name_out = var

    elif merge_how == 'eval':
        var_name_out = merge_eval_fun
        var_name_out = var_name_out.replace('{};'.format(dataset), '')
        var_name_out = var_name_out.replace('{};'.format(dataset_ref), '')

merge_info_vars = {'merge_how' : merge_how}
if merge_how == 'combine':
    merge_info_vars['prefer'] = prefer
elif merge_how == 'eval':
    merge_info_vars['merge_eval_fun'] = merge_eval_fun


distfun = pya.geodesy.calc_distance
long_coords = list(zip(long['latitude'], long['longitude']))

merged_stats = []
var, var_other = short['var_name'], long['var_name']
for i, stat in enumerate(short['stats']):
    statname = stat.station_name
    lat0, lon0 = short['latitude'][i], short['longitude'][i]

    if match_stats_how == 'station_name':
        try:
            idx_other = long['station_name'].index(statname)
        except ValueError:
            continue
    else:
        dists = [distfun(lat0, lon0,c[0],c[1]) for c in long_coords]

        idx_other = np.nanargmin(dists)
        if dists[idx_other] > tolerance:
            continue

    stat_other = long['stats'][idx_other]
    lat1, lon1 = long['latitude'][idx_other], long['longitude'][idx_other]

    #ts = stat[var]
    #ts_other = stat_other[var_other]

    tt = stat.get_var_ts_type(var)
    tto = stat.get_var_ts_type(var_other)

    to_ts_type = pya.helpers.sort_ts_types([tt, tto])[-1]

    df = pya.colocation._colocate_site_data_helper(
        stat, stat_other,
        var, var_other,
        to_ts_type,
        resample_how=None,
        apply_time_resampling_constraints=None,
        min_num_obs=None,
        use_climatology_ref=False
        )

    df.dropna(axis=0, how='all', inplace=True)

    # NOTE: the dataframe returned by _colocate_site_data_helper has ref as first
    # column and the first input data as 2nd!
    col_order = [long['id'], short['id']]
    col_names = list(df.columns.values)

    if merge_how == 'combine':
        if not prefer in df.columns:
            prefer = ids[0]

        prefer_col = col_names[col_order.index(prefer)]
        dont_prefer = col_names[int(not (col_names.index(prefer_col)))]
        df['result'] = df[prefer_col].combine_first(df[dont_prefer])

    elif merge_how == 'mean':
        df['result'] = df.mean(axis=1)

    elif merge_how == 'eval':
        func = merge_eval_fun.replace(col_order[0], col_names[0])
        func = func.replace(col_order[1], col_names[1])

        df['result'] = df.eval(func)


    ts = df['result'].dropna()

    var_info = {'ts_type' : to_ts_type}
    var_info.update(merge_info_vars)

    new = pya.StationData()

    meta_merged = stat.merge_meta_same_station(stat_other,
                                               inplace=False)

    for key in new.STANDARD_META_KEYS:
        new[key] = meta_merged[key]

    new['var_info'][var_name_out] = var_info
    new[var_name_out] = ts

    merged_stats.append(new)

data = pya.UngriddedData.from_station_data(merged_stats)

# =============================================================================
#
#     var ='od550aer'
#     sdaod = obs_ref.to_station_data(statname, [var, var_ref, 'od550gt1aer'])
#     od = obs.to_station_data(statname, var)
#     date = '1994-08-19'
#     print()
#     print()
#
#     print(od[var][date])
#     print(sdaod[var][date])
#     print(sdaod['od550lt1aer'][date])
#     print(sdaod['od550gt1aer'][date])
#     raise Exception
# =============================================================================

