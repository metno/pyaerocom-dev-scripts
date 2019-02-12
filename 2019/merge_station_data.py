#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 09:16:24 2019

@author: jonasg
"""
import pandas as pd
import pyaerocom as pya
from pyaerocom.exceptions import DataCoverageError, MetaDataError

def merge_station_data(stats, var_name, pref_attr=None, 
                       sort_by_largest=True, fill_missing_nan=True,
                       **add_meta_keys):
    """Merge multiple StationData objects (from one station) into one instance
    
    Note
    ----
    - all input :class:`StationData` objects need to have same attributes\
       ``station_name``, ``latitude``, ``longitude`` and ``altitude``
    
    Parameters
    ----------
    stats : list
        list containing :class:`StationData` objects (note: all of these 
        objects must contain variable data for the specified input variable)
    var_name : str
        data variable name that is to be merged
    pref_attr 
        optional argument that may be used to specify a metadata attribute
        that is available in all input :class:`StationData` objects and that
        is used to order the input stations by relevance. The associated values
        of this attribute need to be sortable (e.g. revision_date). This is 
        only relevant in case overlaps occur. If unspecified the relevance of 
        the stations is sorted based on the length of the associated data 
        arrays.
    sort_by_largest : bool
        if True, the result from the sorting is inverted. E.g. if 
        ``pref_attr`` is unspecified, then the stations will be sorted based on
        the length of the data vectors, starting with the shortest, ending with
        the longest. This sorting result will then be inverted, if 
        ``sort_by_largest=True``, so that the longest time series get's highest
        importance. If, e.g. ``pref_attr='revision_date'``, then the stations 
        are sorted by the associated revision date value, starting with the 
        earliest, ending with the latest (which will also be inverted if 
        this argument is set to True)
    fill_missing_nan : bool
        if True, the resulting time series is filled with NaNs. NOTE: this 
        requires that information about the temporal resolution (ts_type) of
        the data is available in each of the StationData objects.
    """    
    # make sure the data is provided as pandas.Series object
    for stat in stats:
        if not var_name in stat:
            raise DataCoverageError('All input station must contain {} data'
                                    .format(var_name))
        elif not isinstance(stat[var_name], pd.Series):
            try:
                stat._to_ts_helper(var_name)
            except Exception as e:
                raise ValueError('Data needs to be provided as pandas Series in '
                                 'individual station data objects. Attempted to'
                                 'convert but failed with the following '
                                 'exception: {}'.format(repr(e)))
        elif fill_missing_nan:
            try:
                stat.get_var_ts_type(var_name)
            except MetaDataError:
                raise MetaDataError('Cannot merge StationData objects: one or '
                                    'more of the provided objects does not '
                                    'provide information about the ts_type of '
                                    'the {} data, which is required when input '
                                    'arg. fill_missing_nan is True.'.format(var_name))
                
    if pref_attr is not None:
        stats.sort(key=lambda s: s[pref_attr])
    else:
        stats.sort(key=lambda s: len(s[var_name].dropna()))
    
    if sort_by_largest:
        stats = stats[::-1]
    
    # remove first station from the list
    first = stats.pop(0)
        
    for i, stat in enumerate(stats):    
        first.merge_other(stat, var_name, **add_meta_keys)
        #first.merge_vardata(stat, var_name)
    
    if fill_missing_nan:
        first.insert_nans(var_name)
    return first

if __name__=='__main__':
    import matplotlib.pyplot as plt
    plt.close('all')
    
    VAR = 'scatc550aer'
    data = pya.io.ReadUngridded().read('EBASMC', 
                                       [VAR],
                                       station_names=['Trinidad*Head',
                                                      'Hohenpei*'])
    
    ### THIS ONE SHOULD HAVE OVERLAPPING TIMESERIES
    stats = data.to_station_data('Tr*', VAR)
    
    merged = merge_station_data(stats, VAR, pref_attr='revision_date')
    
    ax = merged.plot_variable('scatc550aer', add_overlaps=True, lw=2)
    ax = merged.plot_variable('scatc550aer', freq='monthly', ax=ax,
                              lw=4)
    ax = merged.plot_variable('scatc550aer', freq='yearly', ax=ax,
                              ls='none', marker='o', ms=20)
    
    ### THIS ONE SHOULD NOT HAVE OVERLAPPING TIMESERIES
    stats = data.to_station_data('Hohen*', VAR)
    
    merged2 = merge_station_data(stats, VAR, pref_attr='revision_date')
    
    ax = merged2.plot_variable('scatc550aer', add_overlaps=True, lw=2)
    ax = merged2.plot_variable('scatc550aer', freq='monthly', ax=ax,
                               lw=4)
    ax = merged2.plot_variable('scatc550aer', freq='yearly', ax=ax,
                               ls='none', marker='o', ms=20)
    