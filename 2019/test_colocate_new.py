import matplotlib.pyplot as plt
import pyaerocom as pya

    
AERONET = 'AeronetSunV2Lev2.daily'
EBAS = 'EBASMC'

MODEL_ID = 'ECMWF_CAMS_REAN'

if __name__=="__main__":
    plt.close('all')
    
    ### ECMWF reanalysis
    reader = pya.io.ReadGridded(MODEL_ID)
    print(reader)
    
    od550aer = reader.read_var('od550aer', ts_type='daily',
                               start=2010, stop=2013)
    
    od550aer.quickplot_map(time_idx = '31-1-2011')

    
    ### AERONET
    
    data =pya.io.ReadUngridded().read(AERONET, 'od550aer')    
    
    stat = data.to_station_data('Granada', 'od550aer', insert_nans=True)
    
    print(stat)
    
    ax = stat.plot_timeseries('od550aer')
    ax = stat.plot_timeseries('od550aer', freq='monthly', lw=3, ax=ax)
    stat.plot_timeseries('od550aer', freq='yearly', ls='none', marker='o', 
                         ms=14, ax=ax)
    
    
    
    
    col_aero = pya.colocation.colocate_gridded_ungridded(od550aer, data, 
                                                         ts_type='monthly',
                                                         start=2010,
                                                         filter_name='WORLD-noMOUNTAINS')
    
    col_aero.plot_scatter()
    
                         
                        
# =============================================================================
#     ### EBAS
#     
#     ebas = pya.io.ReadUngridded().read(EBAS, 'scatc550aer',
#                                station_names=['Jung*', 'Bond*'])
#     
#     ebas.to_station_data('Bondville').plot_timeseries('scatc550aer', freq='daily')
#     ebas.to_station_data('Jungfraujoch').plot_timeseries('scatc550aer', freq='daily')
#     
#     col_ebas = pya.colocation.colocate_gridded_ungridded(od550aer, ebas, 
#                                                          ts_type='monthly',
#                                                          start=2010,
#                                                          filter_name='WORLD-wMOUNTAINS',
#                                                          var_ref='scatc550aer')
#     col_ebas.plot_scatter()
# 
# 
# =============================================================================
