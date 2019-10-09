from scipy.stats import kendalltau
from scipy.stats.mstats import theilslopes
import datetime 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from pyaerocom.helpers import resample_timeseries

DISP_TRENDS_DETAILS = False

### METHODS TO CREATE AND MODIFY SYNTHETIC SIGNAL

# Creates synthetic signal with periodicity and noise
def create_signal(start, num_years, sampling_freq, sine_amp, freq_periodicity_y, 
                  del_y_whole_period,  y_offset, noise_amp):
    dates = pd.date_range(start=str(start),
                          end='31-12-{} 23:59:59'.format(start + num_years -1), 
                          freq=sampling_freq)

    num = len(dates)
    x = np.arange(num)
    
    trend_signal = del_y_whole_period/num * x + y_offset
    mean_trend = np.mean(trend_signal)
    
    periodic_signal = (sine_amp * mean_trend * 
                       np.sin(np.pi*2*x / (freq_periodicity_y * 365) - np.pi/2))
    
    noise = (np.random.random(num) - .5) * noise_amp *mean_trend
    
    vals = trend_signal + periodic_signal + noise 
    
    
    return (pd.Series(vals, dates), pd.Series(trend_signal, dates))

def pick_random_indices(num, rest_coverage_percent):
    num_samples = int(rest_coverage_percent / 100 * num)
    return sorted(random.sample(range(num), num_samples))
    
def remove_datapoints_random(s, rest_coverage_percent=40):
    idx = pick_random_indices(len(s), rest_coverage_percent)    
    return pd.Series(s.values[idx], s.index[idx])

def setnan_datapoints_random(s, rest_coverage_percent=40):
    idx = pick_random_indices(len(s), rest_coverage_percent)
    new = pd.Series(np.ones(len(s)) * np.nan, s.index)
    new[idx] = s[idx]
    return new

def invalidate_all_but_first_day_in_month(s):
    mask  = s.index.day == 1
    
    new = pd.Series(np.ones(len(s)) * np.nan, s.index)
    new[mask] = s[mask]
    return new

### METHODS FROM CURRENT TRENDS INTERFACE
def to_monthly_current(s, min_dim):
    """Helper to convert daily to monthly 
    """
    d = dict(month = s.index.month, 
             year  = s.index.year,
             value = s.values)
    daily = pd.DataFrame(d)
    daily = daily[pd.notnull(daily['value'])]
    
    # Group data first by year, then by month
    g = daily.groupby(["year", "month"])
    
    # For each group, calculate the average of value
    _m = g.aggregate({"value":np.mean})
    numdays = g.size()
    
    # NOTE: This condition was changed from <= to <
    invalid_mask = numdays < min_dim
    _m['value'].loc[invalid_mask] = np.nan
    
    
    #js date
    _m.reset_index(inplace=True)
    if not len(_m['value']) > 0:
        raise ValueError('Derived monthly averages do not contain '
                                'data')
    dates = _m.apply(lambda row: datetime.datetime(int(row['year']),
                                                   int(row['month']), 
                                                   15), axis=1)
    #mobs.set_index(dates, inplace=True)
    
    monthly = pd.Series(_m.value.values, dates.values)#.resample('MS').mean()
    monthly = monthly.resample('MS').mean()
    monthly.index = monthly.index.shift(14, 'D')
    
    return monthly

def _get_season_current(mm,yyyy):
    if mm in [3,4,5]:
        s = 'spring-'+str(int(yyyy))
    if mm in [6,7,8]:
        s = 'summer-'+str(int(yyyy))
    if mm in [9,10,11]:
        s = 'autumn-'+str(int(yyyy))
    if mm in [12]:
        s = 'winter-'+str(int(yyyy))
    if mm in [1,2]:
        s = 'winter-'+str(int(yyyy-1))
    return s

def _mid_season_current(seas, yr):
    if seas=='spring':
        date = datetime.datetime(yr,4,15)
    if seas=='summer':
        date = datetime.datetime(yr,7,15)
    if seas=='autumn':
        date = datetime.datetime(yr,10,15)
    if seas=='winter':
        date = datetime.datetime(yr-1,1,15)
    if seas=='all':
        date = datetime.datetime(yr,6,15) 
    return date

def compute_trends_current(s_monthly, periods, only_yearly=True):
    """Compute trends for station
    
    Slightly modified code from original trends interface developed by 
    A. Mortier.
    
    Main changes applied:
        
        - Keep NaNs
    """
    #sm = to_monthly_current_trends_interface(s0, MIN_DIM)
    d = dict(month = s_monthly.index.month, 
             year  = s_monthly.index.year,
             value = s_monthly.values)

    mobs = pd.DataFrame(d)

    mobs['season'] = mobs.apply(lambda row: _get_season_current(row['month'],
                                                                row['year']), axis=1)
    
    mobs = mobs.dropna(subset=['value'])

    #trends with yearly and seasonal averages
    seasons = ['spring','summer','autumn','winter','all']
    yrs = np.unique(mobs['year'])

    data = {}

    for i, seas in enumerate(seasons):
        if only_yearly and not seas=='all':
            continue
        #initialize seasonal object
        data[seas] = {'date': [], 'jsdate': [], 'val': []}
        #filter the months
        for yr in yrs:
            if seas!='all':
                catch = mobs[mobs['season'].str.contains(seas+'-'+str(yr))]
            else:
                catch = mobs[mobs['season'].str.contains('-'+str(yr))]
            date = _mid_season_current(seas,yr)

            data[seas]['date'].append(date)
            epoch = datetime.datetime(1970,1,1)
            data[seas]['jsdate'] = [(dat-epoch).total_seconds()*1000 for dat in data[seas]['date']]
            #needs 4 seasons to compute seasonal average to avoid biases
            if (seas=='all') & (len(np.unique(catch['season'].values))<4):
                data[seas]['val'].append(np.nan)
            else:
                data[seas]['val'].append(np.nanmean(catch['value']))
        
        #trends for this season
        data[seas]['trends']={}

        #filter period
        for period in periods:
            p0 = int(period[:4])
            p1 = int(period[5:])
            data[seas]['trends'][period] = {}

            #Mann-Kendall test
            x = np.array(data[seas]['jsdate'])
            y = np.array(data[seas]['val'])
            #works only on not nan values
            x = x[~np.isnan(y)]
            y = y[~np.isnan(y)]
            #filtering to the period limit
            jsp0 = (datetime.datetime(p0,1,1)-epoch).total_seconds()*1000
            jsp1 = (datetime.datetime(p1,12,31)-epoch).total_seconds()*1000
            y = y[(x>=jsp0) & (x<=jsp1)]
            x = x[(x>=jsp0) & (x<=jsp1)]

            if len(x)>2:
                #kendall
                [tau,pval]=kendalltau(x,y)
                data[seas]['trends'][period]['pval'] = pval

                #theil slope
                res=theilslopes(y,x,0.9)
                
                reg=res[0]*np.asarray(x)+res[1]*np.ones(len(x))
                slp=res[0]*1000*60*60*24*365/reg[0] #slp per milliseconds to slp per year
                data[seas]['trends'][period]['slp'] = slp*100 #in percent
                data[seas]['trends'][period]['reg0'] = reg[0]
                data[seas]['trends'][period]['t0'] = x[0]
                data[seas]['trends'][period]['n'] = len(y)
            else:
                data[seas]['trends'][period]['pval'] = None
                data[seas]['trends'][period]['slp'] = None
                data[seas]['trends'][period]['reg0'] = None
                data[seas]['trends'][period]['t0'] = None
                data[seas]['trends'][period]['n'] = len(y)
                
    return data

def get_yearly_and_trend_current(s, period=None):
    """Helper to check only yearly signal"""
    if len(s.dropna()) == 0:
        raise ValueError('Monthly time-series contains only NaNs')
    if period is None:
        years = s.index.year
        period = "{}-{}".format(years[0], years[-1])
    td = compute_trends_current(s, periods=[period])
    subset = td['all']
    yearly = pd.Series(subset['val'], subset['date'])

    t = subset['trends'][period]
    return (yearly, t['slp'], t['pval'])

def compute_yearly_trend_current(s, coverage, period, min_dim):
    """Helper that computes trend based on yearly data"""
    if not coverage == 100:
        s = remove_datapoints_random(s, rest_coverage_percent=coverage)
        
    s_m = to_monthly_current(s, min_dim)
    _, slp, pval = get_yearly_and_trend_current(s=s_m, 
                                                period=period)
    return slp, pval

### NEW METHODS FOR TRENDS COMPUTATION
def to_monthly_new(s, min_dim):
    """Helper to convert daily to monthly 
    """
    return resample_timeseries(s, freq='monthly', 
                               how='mean', 
                               min_num_obs=min_dim)
    
def _get_season_new(mm,yyyy):
    if mm in [1,2,3]:
        s = 'JFM-'+str(int(yyyy))
    if mm in [4,5,6]:
        s = 'AMJ-'+str(int(yyyy))
    if mm in [7,8,9]:
        s = 'JAS-'+str(int(yyyy))
    if mm in [10,11,12]:
        s = 'OND-'+str(int(yyyy))
    
    return s

def _mid_season_new(seas, yr):
    if seas=='all':
        return np.datetime64('{}-06-15'.format(yr))
    elif seas=='JFM':
        return np.datetime64('{}-02-15'.format(yr))
    elif seas=='AMJ':
        return np.datetime64('{}-05-15'.format(yr))
    elif seas=='JAS':
        return np.datetime64('{}-08-15'.format(yr))
    elif seas=='OND':
        return np.datetime64('{}-11-15'.format(yr))
    raise ValueError('Invalid input for season (seas):', seas)

def to_jsdate(dates):
    epoch = np.datetime64('1970-01-01')
    
    return (dates - epoch).astype('timedelta64[ms]').astype(int)
 
def years_from_periodstr(period):
    return [int(x) for x in period.split('-')]

def compute_trends_new(s_monthly, periods, only_yearly=True):
    #sm = to_monthly_current_trends_interface(s0, MIN_DIM)
    d = dict(month = s_monthly.index.month, 
             year  = s_monthly.index.year,
             value = s_monthly.values)

    mobs = pd.DataFrame(d)

    mobs['season'] = mobs.apply(lambda row: _get_season_new(row['month'],
                                                            row['year']), axis=1)
    
    mobs = mobs.dropna(subset=['value'])
    seasons = ['JFM','AMJ','JAS','OND','all']
    #trends with yearly and seasonal averages
    
    # get all years that are contained in data
    yrs = np.unique(mobs['year'])
    
    data = {}
    for i, seas in enumerate(seasons):
        if only_yearly and not seas=='all':
            continue
        #initialize seasonal object
        data[seas] = {'date'    : [], 
                      'jsdate'  : [], 
                      'val'     : [],
                      'trends'  : {}}
        
        dates = []
        #filter the months
        for yr in yrs:
            if seas!='all':
                
                catch = mobs[mobs['season'].str.contains('{}-{}'.format(seas, yr))]
            else:
                catch = mobs[mobs['season'].str.contains('-{}'.format(yr))]
            date = _mid_season_new(seas, yr)

            dates.append(date)
            
            
            #needs 4 seasons to compute seasonal average to avoid biases
            if seas=='all' and len(np.unique(catch['season'].values)) < 4:
                data[seas]['val'].append(np.nan)
            else:
                data[seas]['val'].append(np.nanmean(catch['value']))
        data[seas]['date'] = np.asarray(dates)
        data[seas]['jsdate'] = to_jsdate(data[seas]['date'])
        #filter period
        for period in periods:
            data[seas]['trends'][period] = {}
            
            # desired start / stop year (note, that this may change if first 
            # or last value in tseries (or both) is NaN)
            start_yr, stop_yr = years_from_periodstr(period)
            num_yrs = stop_yr - start_yr
            
            #filtering to the period limit
            jsp0 = to_jsdate(np.datetime64('{}-01-01'.format(start_yr)))
            jsp1 = to_jsdate(np.datetime64('{}-12-31'.format(stop_yr)))
            
            # vector containing numerical timestamps in javascript format
            jsdate = data[seas]['jsdate']
            
            # get period filter mask
            tmask = np.logical_and(jsdate>=jsp0, jsdate<=jsp1) 
            
            # filter data by period
            jsdate = jsdate[tmask]
            
            # vector containing data values
            y = np.asarray(data[seas]['val'])[tmask]
            
# =============================================================================
#             num_leap_years = np.sum(dt_idx.is_leap_year)
#             
#             secs_per_year = np.mean(([86400 * 365] * (num_yrs-num_leap_years) +
#                                      [86400 * 366] * num_leap_years))
#             
#             
# =============================================================================
            valid = ~np.isnan(y)
        
            # Remove NaNs for Mann-Kendall test and regression
            _jsdate = jsdate[valid]
            _y = y[valid]
            
            if len(_jsdate)>2:
                
                #kendall
                [tau,pval]=kendalltau(_jsdate,_y)
                data[seas]['trends'][period]['pval'] = pval

                #theil slope
                res = theilslopes(_y,_jsdate, 0.9)
                slope = res[0]
                yoffs = res[1]
                # regression line (evaluate at ACTUAL time-stamps corresponding
                # to input period -> jsdate and not _jsdate, which may have 
                # removed first or last year, or both)
                reg = slope * jsdate + yoffs
                
# =============================================================================
#                 # time difference between start and stop in full years.
#                 dt = (np.datetime64(dates[-1]) - 
#                       np.datetime64(dates[0])).astype('timedelta64[s]').astype(int)
#                 
# =============================================================================
# =============================================================================
#                 from numpy.testing import assert_allclose
#                 try:
#                     assert_allclose(dt, secs_per_year * num_yrs, rtol=1e-3)
#                 except:
#                     print(start_yr, stop_yr)
#                     print(dates[0], dates[-1])
#                     print(yrs)
# =============================================================================

                
                #dt = dt / secs_per_year #time diff in units of years
                
                # compute slope in units of %/yr-1 normalised by first value
                # of considered time-series
                slp = (reg[-1] - reg[0]) / (num_yrs * reg[0]) * 100 
                
                data[seas]['trends'][period]['slp'] = slp
                data[seas]['trends'][period]['reg0'] = reg[0]
                data[seas]['trends'][period]['t0'] = jsdate[0]
                data[seas]['trends'][period]['n'] = len(y)
            else:
                data[seas]['trends'][period]['pval'] = None
                data[seas]['trends'][period]['slp'] = None
                data[seas]['trends'][period]['reg0'] = None
                data[seas]['trends'][period]['t0'] = None
                data[seas]['trends'][period]['n'] = len(y)
    return data

def get_yearly_and_trend_new(s, period=None):
    """Helper to check only yearly signal"""
    if len(s.dropna()) == 0:
        raise ValueError('Monthly time-series contains only NaNs')
    if period is None:
        years = s.index.year
        period = "{}-{}".format(years[0], years[-1])
    td = compute_trends_new(s, periods=[period])
    subset = td['all']
    yearly = pd.Series(subset['val'], subset['date'])

    t = subset['trends'][period]
    return (yearly, t['slp'], t['pval'])

def compute_yearly_trend_new(s, coverage, period, min_dim):
    """Helper that computes trend based on yearly data"""
    if not coverage == 100:
        s = remove_datapoints_random(s, rest_coverage_percent=coverage)
        
    s_m = to_monthly_new(s, min_dim)
    _, slp, pval = get_yearly_and_trend_new(s=s_m, period=period)
    return slp, pval


### High level processing and plotting tools
def process_and_plot(s0, coverage=100, period=None, min_dim=5, use_new=False,
                     figsize=None):
    if period is None:
        years = s0.index.year
        period = "{}-{}".format(years[0], years[-1])
    if coverage == 100:
        s = s0
    else:
        s = remove_datapoints_random(s0, rest_coverage_percent=coverage)
        
    if use_new:
        s0_m = to_monthly_new(s, min_dim)
    else:
        s0_m = to_monthly_current(s, min_dim)
    
    if figsize is None:
        figsize = (12,6)
    fig, ax = plt.subplots(1,1, figsize=figsize)
    
    ax.plot(s, '-x', c='lime', label='daily, N={}'.format(len(s.dropna())))
    ax.plot(s0_m, ls='--', marker='o', mfc='none', c='b', ms=8, 
            label='monthly, N={}, mu={:.2f}'.format(len(s0_m.dropna()), s0_m.dropna().mean()))
    try:
        if use_new:
            s0_y, slp, pval = get_yearly_and_trend_new(s0_m, period)
        else:
            s0_y, slp, pval = get_yearly_and_trend_current(s0_m, period)
        if slp is None:
            slp = 999.999
            pval = np.inf
        lbl = ('yearly, N={}, mu={:.2f}'
               .format(len(s0_y.dropna()), s0_y.dropna().mean()))
        ax.plot(s0_y, ls='--', marker='o', c='r',mfc='none', lw=2, ms=12, 
                label=lbl)
        res_str = 'Trend={:.1f} %/yr, pval={:.1f}'.format(slp, pval)
    except:
        res_str = 'FAILURE'
    ax.legend(fontsize=12);
    method = ['CURRENT', 'NEW']
    ax.set_title('({}) {}: {} ({}% coverage)'
                 .format(method[use_new], period, res_str, coverage))
    return ax

def compute_true_trend(st, period=None):
    """Computes true trend based on linear synthetic trend signal
    
    Parameters
    ----------
    st : pandas.Series
        trend time series
    period
    
    Returns
    -------
    float
        true trend for input period
    """
    if period is None:
        period = '{}-{}'.format(st.index.year[0], st.index.year[-1])
    start_year, stop_year = years_from_periodstr(period)
    v_t0, v_tN = st['{}-06-15'.format(start_year)], st['{}-06-15'.format(stop_year)]
    dt = stop_year - start_year
    
    return (v_tN - v_t0) / (dt * v_t0) * 100

def run_stat_analysis(signal_func, num, coverage, period, min_dim, true_trend, 
                      use_new=False, ax=None, pgbar=None,xlim=None, 
                      ylim=None):
    success = 0
    slopes = []
    pvals = []
    if pgbar is not None:
        pgbar.min = 0
        pgbar.value = 0
        pgbar.max = num
    else:
        disp_ival = int(num*0.1)
        if disp_ival == 0:
            disp_ival+=1
    for k in range(num):
        if pgbar is not None:
            pgbar.value += 1
        elif k%disp_ival==0:
            print(k, num)
        s, t = signal_func()
        if use_new:
            slp, pval = compute_yearly_trend_new(s, coverage, period, min_dim)
        else:
            slp, pval = compute_yearly_trend_current(s, coverage, period, min_dim)
        if slp is not None:
            slopes.append(slp)
            pvals.append(pval)
            success += 1
    
    if ax is None:
        _, ax = plt.subplots(1,1, figsize=(8, 8))
        
    if len(slopes) > 0:
        
        ax.hist(slopes, bins=10, color='b', alpha=.3, label='Distribution')
        mu = np.mean(slopes)
        l,h = ax.get_ylim()
        ax.plot([mu, mu], [l, h], '--b', label='Mean')
    
    l,h = ax.get_ylim()

    ax.plot([true_trend, true_trend], [l, h], '--r', label='True trend')

    ax.set_xlabel('Trend [%/yr]')
    ax.set_xlabel('Count')
    which = ['CURRENT', 'NEW']
    ax.set_title('({}): Success={}/{} (Cov.: {:.0f} %)'
                 .format(which[use_new], success, num, coverage),
                 fontsize=11)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    return (slopes, pvals, success, ax)

if __name__ == '__main__':
    plt.close('all')
    # ## Setup signal details and options
    
    # time stuff
    START = 2010 # start of timeseries
    NUM_YEARS = 15 # number of years
    SAMPLING_FREQ = 'D' # time resolution
    MIN_DIM = 5 # minimum number of days in month for monthly means
    PERIODS = ["{}-{}".format(START+2, START + NUM_YEARS - 2)]
               #"{}-{}".format(START, START + 7)]
        
    # trend signal
    DEL_Y_TREND = 3 # between start / stop in variable units
    Y_OFFSET = 1
    
    # noise signal
    NOISE_AMP = .2 #amplitude of noise (relative to mean value of trend signal)
    
    # superimposed sine signal
    PERIODICITY_Y = 1 # periodicity of superimposed sine signale (units of years)
    SINE_AMP = 0.1 # amplitude of superimposed sine signal (relative to mean of trend signal)
    
    COVERAGE = 5/31*100 # % for random bootstrpping of timeseries (5 out of 31 days -> ~ 16%)
        
    # compute true trend
    if not Y_OFFSET > 0:
        raise ValueError('Y_OFFSET needs to be larger than zero')
    TRUE_TREND = DEL_Y_TREND / NUM_YEARS / Y_OFFSET * 100
    
    ### OPTIONS FOR SCRIPT
    #figure size for plots
    FIGSIZE = (16, 8)
    
    RUN_STAT_ANALYSIS = False
    
    # create function shortcuts for default settings
    from functools import partial
    
    # shortcut for create signal
    cs = partial(create_signal, # the method
                 start=START, 
                 num_years=NUM_YEARS, 
                 sampling_freq=SAMPLING_FREQ, 
                 sine_amp=SINE_AMP, 
                 freq_periodicity_y=PERIODICITY_Y, 
                 del_y_whole_period=DEL_Y_TREND, 
                 y_offset=Y_OFFSET, 
                 noise_amp=NOISE_AMP)
    # shotcurt for process_and_plot method using code from current interface
    pp_current = partial(process_and_plot, period=PERIODS[0], min_dim=MIN_DIM)
    
    # shotcurt for process_and_plot method using new methods
    pp_new = partial(process_and_plot, period=PERIODS[0], min_dim=MIN_DIM,
                     use_new=True)
    
    ### Run analysis
    axes = []
    # original signal (s0) and only linear trend signal (st)
    s0, st = cs()
    mean = st.mean()
       
    ax = s0.plot(figsize=FIGSIZE, label='Synthetic sample')
    st.plot(ax=ax, style='-r', label='Trend signal')
    ax.grid()
    ax.legend()
    ax.set_title(r'$\mu_t=${:.3f}; True trend: {:.3f} %/yr'.format(mean, TRUE_TREND));
    
    
    np.testing.assert_allclose(Y_OFFSET * (1 + NUM_YEARS * TRUE_TREND/100), st[-1], rtol=.1)
    
    axes.append(ax)
    # process and plot trends signal
    axes.append(pp_current(st))
    axes.append(pp_new(st))
    
    RUN_ALL = False
    if RUN_ALL:
        #process and plot syntethic signal
        pp_current(s0)
        
        # invalidate, process and plot
        s1 = invalidate_all_but_first_day_in_month(s0)
        axes.append(pp_current(s1))
        axes.append(pp_new(s1))
        
        # remove, data points using default coverage, process and plot
        s3 = setnan_datapoints_random(cs()[0], COVERAGE)
        axes.append(pp_current(s3))
        axes.append(pp_new(s3))
        
        
        
        if RUN_STAT_ANALYSIS:
            test_coverages = [100, 70, 40, 20, 18, 16, 10]
            
            for cov in test_coverages:
                for use_new in [False, True]:
                    slopes, pvals = {},{}
                    sl, pval, _, ax = run_stat_analysis(100, 
                                                        coverage=cov, 
                                                        period=PERIODS[0], 
                                                        true_trend=TRUE_TREND,
                                                        min_dim=MIN_DIM,
                                                        use_new=use_new)
                    slopes[cov] = sl
                    pvals[cov] = pval
                    axes.append(ax)
