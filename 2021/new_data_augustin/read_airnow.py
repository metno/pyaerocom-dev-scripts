import pyaerocom as pya
import os
import csv
from glob import glob
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import numpy as np

# variables conversion and units dictionnary
pyvars = {
    'concbc': {
        'var': 'BC',
        'unit': 'ppb'
    },
    'concco': {
        'var': 'CO',
        'unit': 'ppb'
    },
    'concnh3': {
        'var': 'NH3',
        'unit': 'ppb'
    },
    'concno': {
        'var': 'NO',
        'unit': 'ppb'
    },
    'concno2': {
        'var': 'NO2',
        'unit': 'ppb'
    },
    'concnox': {
        'var': 'NOX',
        'unit': 'ppb'
    },
    'concnoy': {
        'var': 'NOY',
        'unit': 'ppb'
    },
    'conco3': {
        'var': 'OZONE',
        'unit': 'ppb'
    },
    'concpm10': {
        'var': 'PM10',
        'unit': 'ug m-3'
    },
    'concpm25': {
        'var': 'PM2.5',
        'unit': 'ug m-3'
    },
    'concso2': {
        'var': 'SO2',
        'unit': 'ppb'
    }
}

def _read_file(file):
    return pd.read_csv(file,sep='|',
                       names=['mm/dd/yy',
                              'hh:mm',
                              'station_id',
                              'station_name',
                              'time_zone',
                              'variable',
                              'unit',
                              'value',
                              'Institute'])

def _calc_datetime(data):
    _sub = data.apply(lambda row: datetime(year=2000+int(
        row['mm/dd/yy'].split('/')[2]),
        month=int(row['mm/dd/yy'].split('/')[0]),
        day=int(row['mm/dd/yy'].split('/')[1]),
        hour=int(row['hh:mm'].split(':')[0]),
        minute=int(row['hh:mm'].split(':')[1])),
        axis=1)

    data['datetime'] = pd.to_datetime(_sub)
    data.set_index('datetime', inplace=True)
    #drop yy/mm/dd and hh:mm columns
    data.drop(columns=['mm/dd/yy','hh:mm'], inplace=True)
    return data

def _data_to_dicts(data, cfg):
    dic_cfg = dict()
    for column in cfg.columns:
        dic_cfg[column] = np.array(cfg[column].values)
    dic_data = dict()
    for column in data.columns:
        dic_data[column] = np.array(data[column].values)
    return (dic_cfg, dic_data)

def _make_station_data(dic_cfg, dic_data, i, var):
    stat = pya.StationData()

    # fill stat with cfg
    stat['data_id'] = 'CAMS84_AIRNOW'
    stat['station_name'] = dic_cfg['name'][i]
    stat['station_id'] = dic_cfg['aqsid'][i]
    stat['latitude'] = dic_cfg['lat'][i]
    stat['longitude'] = dic_cfg['lon'][i]
    stat['altitude'] = dic_cfg['elevation'][i]
    stat['ts_type'] = 'hourly'

    # fill stat with data
    mask = (dic_data['variable'] == pyvars[var]['var']) & (dic_data['station_id'] == stat['station_id'])
    stat[var] = dic_data['value'][mask].astype('datetime64[s]')

    # for each variable, there needs to be an entry in the var_info dict
    stat['var_info'][var] = dict()
    stat['var_info'][var]['units'] = pyvars[var]['unit']

    return stat

def read_airnow(files, vars_to_retrieve=None):

    # first, read configuration file
    print('read configuration file')
    path_cfg = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/MACC_INSITU_AirNow'
    fn = os.path.join(path_cfg,'allStations_20191224.csv')
    cfg = pd.read_csv(fn,sep=',', converters={'aqsid': lambda x: str(x)})


    # read data using pandas
    print('read data file(s)')
    # initialize empty dataframe
    data = pd.DataFrame()
    for i in tqdm(range(len(files))):
        filedata = _read_file(files[i])
        data = data.append(filedata)

    #create datetimeindex
    data = _calc_datetime(data)

    #list of available variables
    av_data = ['concbc', 'concco', 'concnh3', 'concno', 'concno2', 'concnox', 'concnoy', 'conco3', 'concpm10', 'concpm25', 'concso2']
    if vars_to_retrieve == None:
        vars_to_retrieve = av_data

    #convert dataframes to dictionnaries
    dic_cfg, dic_data = _data_to_dicts(data, cfg)

    # list of stat objects
    print('create stat objects')
    stats = []
    for i in tqdm(range(len(cfg['aqsid']))):
        for var in vars_to_retrieve:
            try:
                stat = _make_station_data(dic_cfg, dic_data, i, var)

                stats.append(stat)
            except KeyError:
                print("Available variables: ",av_data)
                raise
    return stats

if __name__ == '__main__':
    path_data = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/MACC_INSITU_AirNow'
    dirs = [os.path.join(path_data, o) for o in os.listdir(path_data) if os.path.isdir(os.path.join(path_data,o))]
    files = [glob(os.path.join(path_data, d, '*.dat')) for d in dirs][0]

    data = read_airnow(files[:1], ['concpm10'])

    #data1 = _read_file_alt(files[0])
