import matplotlib.pyplot as plt
import pyaerocom as pya

MODEL_ID = 'GFDL-AM4-amip_HIST'


def load_cube_custom_multiproc(files, var_name=None, file_convention=None, 
                               perform_checks=True,
                               num_proc=4):
    """Like :func:`load_cube_custom` but faster"""
    
    readfun = pya.io.iris_io.load_cube_custom
    
    
    import multiprocessing
    from functools import partial
    
    func = partial(readfun, var_name=var_name,
                   file_convention=file_convention, 
                   perform_checks=perform_checks)
    p = multiprocessing.Pool(processes=num_proc)
    return p.map(func, files)
    
if __name__=="__main__":
    plt.close('all')
    
    from time import time
    
    
    ### ECMWF reanalysis
    reader = pya.io.ReadGridded(MODEL_ID)
    print(reader)
    
    t0 = time()
    data = reader.read_var('od550aer', start=1900, stop=1950,
                           num_proc=10)
    t1 = time()
    
    
    ts = data.to_time_series(latitude=30, longitude=15)
    
    
    ts[0].plot_timeseries('od550aer')
    
    import numpy as np
    procs = np.arange(1, 21)
    times_10y = []
    times_100y = []
    for cpu_num in procs:
        t0 =  time()
        data = reader.read_var('od550aer', start=1900, stop=1910,
                               num_proc=cpu_num)
        times_10y.append(time() - t0)
        
        t0 =  time()
        data = reader.read_var('od550aer', start=1900, stop=2000,
                               num_proc=cpu_num)
        times_100y.append(time() - t0)
        
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(1,1, figsize=(16, 12))
    ax.plot(procs,times_10y, 'x--', label='10 years')
    ax.plot(procs,times_100y, 'x--', label='100 years')
    
    ax.set_xlabel('Number of processes')    
    ax.set_ylabel('Required time load cubes [s]')    
    ax.grid()
    ax.legend()
    ax.set_title('Performance load multiple cubes vs. number of cores used')
    fig.savefig('output/test_timeseries_historical_run_out1.png')
    
    
        
        
        
    
    
    
    
    
    
    