import pyaerocom as pya
import os
import csv
from glob import glob
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import numpy as np

from pyaerocom.io import ReadUngriddedBase
from pyaerocom.exceptions import DataCoverageError
from pyaerocom import UngriddedData
# variables conversion and units dictionnary

BASEDATE = 2000


PYVARS = {
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

PROVIDES_VARIABLES = list(PYVARS.keys())

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

def _date_time_str_to_datetime64(date, time):
    mm, dd, yy = date.split('/')
    HH, MM = time.split(':')
    yr=str(BASEDATE+int(yy))
    return np.datetime64(f'{yr}-{mm}-{dd}T{HH}:{MM}:00')

make_datetime64_array = np.vectorize(_date_time_str_to_datetime64)

def _calc_datetime(data):
    dates  = data['mm/dd/yy'].values
    times = data['hh:mm'].values

    dt = make_datetime64_array(dates, times)

    data['dtime'] = dt
    #data.set_index('datetime', inplace=True)
    #drop yy/mm/dd and hh:mm columns
    #data.drop(columns=['mm/dd/yy','hh:mm'], inplace=True)
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

    statid = dic_cfg['aqsid'][i]

    mask = (dic_data['variable'] == PYVARS[var]['var']) & (dic_data['station_id'] == statid)

    if mask.sum() == 0:
        raise DataCoverageError('No data ...')

    stat = pya.StationData()

    # fill stat with cfg
    stat['data_id'] = 'CAMS84_AIRNOW'
    stat['station_name'] = dic_cfg['name'][i]
    stat['station_id'] = statid
    stat['latitude'] = dic_cfg['lat'][i]
    stat['longitude'] = dic_cfg['lon'][i]
    stat['altitude'] = dic_cfg['elevation'][i]
    stat['ts_type'] = 'hourly'


    # fill stat with data

    vals = dic_data['value'][mask]
    dtime = dic_data['dtime'][mask]

    stat[var] = vals
    stat['dtime'] = dtime

    # for each variable, there needs to be an entry in the var_info dict
    stat['var_info'][var] = dict()
    stat['var_info'][var]['units'] = PYVARS[var]['unit']

    return stat

def read_airnow(files, vars_to_retrieve):

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
            except (DataCoverageError):
                pass

    return stats

class ReadAirNow(ReadUngriddedBase):
    _FILEMASK = '/**/*.dat' # fix

    #: version log of this class (for caching)
    __version__ = '0.1'

    COL_DELIM = '|'

    #: Name of dataset (OBS_ID)
    DATA_ID = 'AirNow' #'GAWTADsubsetAasEtAl'

    #: List of all datasets supported by this interface
    SUPPORTED_DATASETS = [DATA_ID]

    PROVIDES_VARIABLES = PROVIDES_VARIABLES

    DEFAULT_VARS = PROVIDES_VARIABLES

    TS_TYPE = 'hourly'


    def __init__(self, data_dir=None):
        super(ReadAirNow, self).__init__(None, dataset_path=data_dir)

    def get_file_list(self):
        basepath = self.DATASET_PATH
        pattern = f'{basepath}{self._FILEMASK}'
        files = sorted(glob(pattern))
        return files

    def read_file(self):
        raise NotImplementedError('Not needed for these data since the format '
                                  'is unsuitable...')

    def read(self, vars_to_retrieve=None, first_file=None, last_file=None):

        if isinstance(vars_to_retrieve, str):
            vars_to_retrieve = [vars_to_retrieve]

        files = self.get_file_list()
        if first_file is None:
            first_file = 0
        if last_file is None:
            last_file = len(files)
        files = files[first_file:last_file]

        stats = read_airnow(files, vars_to_retrieve)

        data = UngriddedData.from_station_data(stats)

        return data


if __name__ == '__main__':
    path_data = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/MACC_INSITU_AirNow'
# =============================================================================
#     dirs = [os.path.join(path_data, o) for o in os.listdir(path_data) if os.path.isdir(os.path.join(path_data,o))]
#     files = [glob(os.path.join(path_data, d, '*.dat')) for d in dirs][0]
# =============================================================================

    #data = read_airnow(files[:1], ['concpm10'])

    reader = ReadAirNow(data_dir=path_data)

    data = reader.read('concpm10', last_file=10)

    data.plot_station_coordinates()
    #data1 = _read_file_alt(files[0])
