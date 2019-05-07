import matplotlib.pyplot as plt
import pyaerocom as pya


LON1 = 15
LAT1 = 55

if __name__=="__main__":
    plt.close('all')
    
    ### ECMWF reanalysis
    reader = pya.io.ReadGridded('ECMWF_CAMS_REAN')
    print(reader)
    
    d = reader.read_var('ec532aer', 
                        vert_which='ModelLevel', 
                        start=2010)
    
    #d.resample_time('monthly')
    print(d)
    
    #res = d._check_altitude_access()
    
    #alt = res['z'].cube
    
    altitude = d.get_altitude(latitude=LAT1, longitude=LON1)
    
    print(altitude)
    
    
    #auxc = iris.coords.AuxCoord(alt.data)
    #d.get_altitude(longitude=LON1, latitude=LAT1)
    
    #d.to_time_series(longitude=[15], latitude=[55],
    #                 vert_scheme='profile')
