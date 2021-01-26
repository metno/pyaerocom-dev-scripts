import pyaerocom as pya
import os
import csv
from glob import glob
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import numpy as np
import dask.dataframe

def read_airnow(files, vars_to_retrieve=None):
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
        data = data.append(pd.read_csv(files[i],sep='|',names=['mm/dd/yy','hh:mm','station_id','station_name','time_zone','variable','unit','value','Institute']))
        
    #create datetimeindex
    data['datetime'] = pd.to_datetime(data.apply(lambda row: datetime(year=2000+int(row['mm/dd/yy'].split('/')[2]),month=int(row['mm/dd/yy'].split('/')[0]),day=int(row['mm/dd/yy'].split('/')[1]),hour=int(row['hh:mm'].split(':')[0]),minute=int(row['hh:mm'].split(':')[1])), axis=1))
    data.set_index('datetime', inplace=True)
    #drop yy/mm/dd and hh:mm columns
    data.drop(columns=['mm/dd/yy','hh:mm'], inplace=True)
    
    
    
    #list of available variables
    av_data = ['concbc', 'concco', 'concnh3', 'concno', 'concno2', 'concnox', 'concnoy', 'conco3', 'concpm10', 'concpm25', 'concso2']
    if vars_to_retrieve == None:
        vars_to_retrieve = av_data
    
    
    # list of stationData objects
    print('create stationData objects')
    stationsData = []
    for i in tqdm(range(len(cfg))):
        row = cfg.iloc[i]

        for var in vars_to_retrieve:
            
            #initialize stationData object
            stationData = pya.StationData()

            # fill stationData with cfg
            stationData['data_id'] = 'CAMS84_AIRNOW'
            stationData['station_name'] = row['name']
            stationData['station_id'] = row['aqsid']
            stationData['latitude'] = row['lat']
            stationData['longitude'] = row['lon']
            stationData['altitude'] = row['elevation']
            stationData['ts_type'] = 'hourly'

            # fill stationData with data
            # Then, for each variable
            stationData[var] = data.loc[(data['station_id']==row['aqsid']) & (data['variable']==pyvars[var]['var'])].value.astype('datetime64[s]')

            # for each variable, there needs to be an entry in the var_info dict
            stationData['var_info'][var] = dict()
            stationData['var_info'][var]['units'] = pyvars[var]['unit']

            stationsData.append(stationData)

    return stationsData


path_data = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/MACC_INSITU_AirNow'
dirs = [os.path.join(path_data, o) for o in os.listdir(path_data) if os.path.isdir(os.path.join(path_data,o))]
files = [glob(os.path.join(path_data, d, '*.dat')) for d in dirs][0]
    
data = read_airnow(files, ['concpm10'])