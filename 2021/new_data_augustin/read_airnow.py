import os
from glob import glob
import pandas as pd
from tqdm import tqdm
import numpy as np
from pyaerocom import const
from pyaerocom.io import ReadUngriddedBase
from pyaerocom.exceptions import DataCoverageError
from pyaerocom import UngriddedData, StationData

class ReadAirNow(ReadUngriddedBase):

    # data type of files
    _FILETYPE = '.dat'

    # to recursively retrieve list of data files
    _FILEMASK = f'/**/*{_FILETYPE}'

    #: version log of this class (for caching)
    __version__ = '0.1'

    #: column delimiter
    FILE_COL_DELIM = '|'

    #: columns in data files
    FILE_COL_NAMES = ['date','time', 'station_id',
                      'station_name', 'time_zone',
                      'variable', 'unit', 'value',
                      'institute']

    #: mapping of columns in station metadata file to pyaerocom standard
    STATION_META_MAP = {
            'aqsid'             : 'station_id',
            'name'              : 'station_name',
            'lat'               : 'latitude',
            'lon'               : 'longitude',
            'elevation'         : 'altitude',
            'city'              : 'city',
            'address'           : 'address',
            'timezone'          : 'timezone',
            'environment'       : 'environment',
            'modificationdate'  : 'modificationdate',
            'populationclass'   : 'classification',
            'comment'           : 'comment'
            }

    #:
    BASEYEAR = 2000

    #: Name of dataset (OBS_ID)
    DATA_ID = 'AirNow' #'GAWTADsubsetAasEtAl'

    #: List of all datasets supported by this interface
    SUPPORTED_DATASETS = [DATA_ID]

    #: units found in file
    UNIT_MAP = {
        'C' : 'celcius',
        'M/S' : 'm s-1',
        'MILLIBAR' : 'mbar',
        'MM' : 'mm',
        'PERCENT' : '%',
        'PPB' : 'ppb',
        'PPM' : 'ppm',
        'UG/M3' : 'ug m-2',
        'WATTS/M2': 'W m-2'
        }

    VAR_MAP = {
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

    PROVIDES_VARIABLES = list(VAR_MAP.keys())

    DEFAULT_VARS = PROVIDES_VARIABLES

    TS_TYPE = 'hourly'

    #: file containing station metadata
    STAT_METADATA_FILENAME = 'allStations_20191224.csv'

    def __init__(self, data_dir=None):
        super(ReadAirNow, self).__init__(None, dataset_path=data_dir)
        self.make_datetime64_array = np.vectorize(self._date_time_str_to_datetime64)

    def _date_time_str_to_datetime64(self, date, time):
        mm, dd, yy = date.split('/')
        HH, MM = time.split(':')
        yr=str(self.BASEYEAR + int(yy))
        # returns as datetime64[s]
        return np.datetime64(f'{yr}-{mm}-{dd}T{HH}:{MM}:00')

    def _calc_datetime(self, data):
        dates  = data['date'].values
        times = data['time'].values

        dt = self.make_datetime64_array(dates, times)

        data['dtime'] = dt

        return data

    def _datetime_from_filename(self, filepath):
        fn = os.path.basename(filepath).split(self._FILETYPE)[0]
        assert len(fn) == 10
        tstr = f'{fn[:4]}-{fn[4:6]}-{fn[6:8]}T{fn[8:10]}:00:00'
        return np.datetime64(tstr)

    @staticmethod
    def _data_to_dicts(data, cfg):
        dic_cfg = dict()
        for column in cfg.columns:
            dic_cfg[column] = np.array(cfg[column].values)
        dic_data = dict()
        for column in data.columns:
            dic_data[column] = np.array(data[column].values)
        return (dic_cfg, dic_data)

    def _make_station_data(self, dic_cfg, dic_data, i, var):

        statid = dic_cfg['aqsid'][i]

        mask = (dic_data['variable'] == self.VAR_MAP[var]['var']) & (dic_data['station_id'] == statid)

        if mask.sum() == 0:
            raise DataCoverageError('No data ...')

        stat = StationData()

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
        stat['var_info'][var]['units'] = self.VAR_MAP[var]['unit']

        return stat

    def get_file_list(self):
        basepath = self.DATASET_PATH
        pattern = f'{basepath}{self._FILEMASK}'
        files = sorted(glob(pattern))
        return files

    def _read_file(self, file, assert_same_dtime=False):
        df = pd.read_csv(file,sep=self.FILE_COL_DELIM,
                         names=self.FILE_COL_NAMES)
        if assert_same_dtime:
            dates = np.unique(df.date.values)
            times = np.unique(df.time.values)
            assert 1 == len(dates) == len(times)
        df['dtime'] = self._datetime_from_filename(file)
        return df

    def _read_files(self, files, vars_to_retrieve, stat_metadata):


        # read data using pandas
        print('read data file(s)')
        # initialize empty dataframe
        data = pd.DataFrame()

        for i in tqdm(range(len(files))):
            fp = files[i]
            filedata = self._read_file(fp)
            data = data.append(filedata)

        #create datetimeindex
        #data = self._calc_datetime(data)

        #convert dataframes to dictionnaries
        dic_cfg, dic_data = self._data_to_dicts(data, stat_metadata)

        # list of stat objects
        print('create stat objects')
        stats = []
        for i in tqdm(range(len(stat_metadata['aqsid']))):
            for var in vars_to_retrieve:
                try:
                    stat = self._make_station_data(dic_cfg, dic_data, i, var)

                    stats.append(stat)
                except (DataCoverageError):
                    pass

        return stats

    def _read_files_new(self, files, vars_to_retrieve,
                                    stat_metadata):

        stat_meta = self._init_station_metadata(stat_metadata)
        stat_ids = list(stat_meta.keys())
        print('read data file(s)')
        # initialize empty dataframe
        data = pd.DataFrame()

        for i in tqdm(range(len(files))):
            fp = files[i]
            filedata = self._read_file(fp)
            data = data.append(filedata)


        varcol = self.FILE_COL_NAMES.index('variable')
        statcol = self.FILE_COL_NAMES.index('station_id')
        tzonecol = self.FILE_COL_NAMES.index('time_zone')
        unitcol = self.FILE_COL_NAMES.index('unit')
        valcol = self.FILE_COL_NAMES.index('value')

        dataarr = data.values
        stats = []
        for var in vars_to_retrieve:
            # extract only variable data (should speed things up)
            var_in_file = self.VAR_MAP[var]['var']
            mask = dataarr[:, varcol] == var_in_file
            subset = dataarr[mask]

            statlist = np.unique(subset[:, statcol])

            for stat_id in statlist:
                if not stat_id in stat_ids:
                    continue
                statmask = subset[:, statcol] == stat_id
                if statmask.sum() == 0:
                    continue
                statdata = subset[statmask]
                stat = StationData(**stat_meta[stat_id])
                dtime = statdata[:, -1]
                offs = np.unique(statdata[:, tzonecol])
                if not len(offs) == 1:
                    raise NotImplementedError(
                        f'Encountered several timezones for station ID {stat_id}'
                        )

                vals = statdata[:, valcol]
                units = np.unique(statdata[:, unitcol])
                if len(units) != 1:
                    raise NotImplementedError(
                        f'Encountered several units for {var}'
                        )
                elif not units[0] in self.UNIT_MAP:
                    raise AttributeError(
                        'Encountered unregistered unit {units[0]} for {var}'
                        )
                stat['dtime'] = dtime
                stat[var] = vals
                unit = self.UNIT_MAP[units[0]]
                stat['var_info'][var] = dict(units=unit)
                stats.append(stat)
        return stats

    def read_file(self):
        raise NotImplementedError('Not needed for these data since the format '
                                  'is unsuitable...')

    def _read_metadata_file(self):
        fn = os.path.join(self.DATASET_PATH, self.STAT_METADATA_FILENAME)
        cfg = pd.read_csv(fn,sep=',', converters={'aqsid': lambda x: str(x)})
        return cfg

    def _init_station_metadata(self, cfg):
        meta_map = self.STATION_META_MAP

        cols = list(cfg.columns.values)
        col_idx = {}
        for from_meta, to_meta in meta_map.items():
            col_idx[to_meta] = cols.index(from_meta)

        arr = cfg.values

#        station_names = arr[:, col_idx['station_name']]
        stats = {}
        for row in arr:
            stat = {}
            for meta_key, col_num in col_idx.items():
                stat[meta_key] = row[col_num]
            sid = stat['station_id']
            stats[sid] = stat

        return stats

    def read(self, vars_to_retrieve=None, first_file=None, last_file=None,
             new_method=False):

        if isinstance(vars_to_retrieve, str):
            vars_to_retrieve = [vars_to_retrieve]

        files = self.get_file_list()
        if first_file is None:
            first_file = 0
        if last_file is None:
            last_file = len(files)
        files = files[first_file:last_file]

        stat_metadata = self._read_metadata_file()
        if new_method:
            fun = self._read_files_new
        else:
            fun = self._read_files
        stats = fun(files, vars_to_retrieve, stat_metadata)

        data = UngriddedData.from_station_data(stats)

        return data


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    plt.close('all')
    path_data = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/MACC_INSITU_AirNow'
    #path_data = '/home/jonasg/MyPyaerocom/data/obsdata/MACC_INSITU_AirNow'

    test_file =  path_data + '/202001/2020010100.dat'
    reader = ReadAirNow(data_dir=path_data)

    #data = reader._read_file(test_file)

    last_file = 10
    data = reader.read('concpm10', last_file=last_file, new_method=False)

    if last_file == 10:
        assert len(data.unique_station_names) == 196
    data.plot_station_coordinates()
    #data1 = _read_file_alt(files[0])
