#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 15:24:31 2021

@author: jonasg
"""
import numpy as np
from datetime import datetime
import pandas as pd
from time import time

def _date_time_str_to_datetime64(date, time):
    mm, dd, yy = date.split('/')
    HH, MM = time.split(':')
    yr=str(2000+int(yy))
    return np.datetime64(f'{yr}-{mm}-{dd}T{HH}:{MM}:00')

def _date_time_str_to_datetime64_gen(date, time):
    mm, dd, yy = date.split('/')
    HH, MM = time.split(':')
    yr=str(2000+int(yy))
    yield np.datetime64(f'{yr}-{mm}-{dd}T{HH}:{MM}:00')

def _date_time_str_to_datetime64_alt(date, time):
    mm, dd, yy = date.split('/')
    HH, MM = time.split(':')
    dt = datetime(int(yy) + 2000, int(mm), int(dd), int(HH), int(MM), 0)
    return np.datetime64(dt).astype('datetime64[s]')


def _make_datetime64_arr(dates, times, method):

    dts = []
    for date, time in zip(dates, times):
        dts.append(method(date, time))
    return np.asarray(dts)


if __name__ == '__main__':
    # create fake data for testing (as it would be extracted from DataFrame)
    num_datapoints = int(1e6)
    # mm/dd/yy
    dates = np.asarray(['10/28/20']*num_datapoints)

    # HH:MM
    times = np.asarray(['08:00']*num_datapoints)

    t0 = time()
    dts0 = _make_datetime64_arr(dates, times, _date_time_str_to_datetime64)
    print(f'NEW METHOD (FAST, via numpy): {time()-t0:.2f} s')

    t0 = time()
    dts1 = _make_datetime64_arr(dates, times, _date_time_str_to_datetime64_alt)
    print(f'NEW METHOD (LITTLE SLOWER, via datetime): {time()-t0:.2f} s')

    fun = np.vectorize(_date_time_str_to_datetime64)
    t0 = time()
    dts2 = fun(dates, times)
    print(f'NEW METHOD (FAST, vectorized): {time()-t0:.2f} s')

    fun = np.vectorize(_date_time_str_to_datetime64_gen)
    t0 = time()
    dts3 = fun(dates, times)
    print(f'NEW METHOD (FAST, vectorized): {time()-t0:.2f} s')

    raise Exception
    ### OLD METHODOLOGY
    data = pd.DataFrame({'mm/dd/yy':dates, 'hh:mm':times})

    t0 = time()
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
    print(f'OLD METHOD: {time()-t0:.2f} s')







