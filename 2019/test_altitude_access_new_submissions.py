import matplotlib.pyplot as plt
import pyaerocom as pya
import iris
    
MODEL2 = 'OsloCTM3v1.01'

LON1 = 15
LAT1 = 55

FILE1 = ('/lustre/storeA/project/aerocom/aerocom-users-database/'
         'AEROCOM-PHASE-III-2019/OsloCTM3v1.01/renamed/'
         'aerocom3_OsloCTM3v1.01-met2010_AP3-CTRL_ec550aer_ModelLevel_2010_monthly.nc')

if __name__=="__main__":
    plt.close('all')
    
    cubes = iris.load(FILE1)
    
    print(cubes)
    
    ec = cubes[2]
    
    print([x.standard_name for x in ec.coords()])
    