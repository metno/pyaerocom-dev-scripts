import matplotlib.pyplot as plt
import pyaerocom as pya

    
MODEL_ID = 'ECHAM6.1-HAM2.2_GLOFIR1'

if __name__=="__main__":
    plt.close('all')
    
    ### ECMWF reanalysis
    reader = pya.io.ReadGridded(MODEL_ID)
    print(reader)
    
    def add_cube(gridded1, gridded2):
        return  gridded1.grid + gridded2.grid
    
    reader.add_aux_compute('od550gt1aer', 
                           vars_required=['od550dust', 'od550ss'],
                           fun=add_cube)
    
    print(reader.vars_provided)
    
    d0 = reader.read_var('od550gt1aer')
    
    r = pya.io.ReadGridded('ECMWF_CAMS_REAN')
    
    print(r)
    
    d1 =  r.read_var('od550gt1aer', aux_vars=['od550dust', 'od550ss'],
                     aux_fun=add_cube)
    
    
    
    