import matplotlib.pyplot as plt
import pyaerocom as pya
import pandas as pd

per = pd.DatetimeIndex(start='1-1-2010', end='31-12-2010', freq='M')

r = pya.io.ReadGridded('GISS-MATRIX_GLOFIR0p5')

data2 = r.read_var('ec550aer', ts_type='daily', vert_which='ModelLevel')

r = pya.io.ReadGridded('ECHAM6.1-HAM2.2_GLOFIR0')

data = r.read_var('od550aer', start=2008)


r = pya.io.ReadGridded('ECHAM6-SALSA_GLOFIR0')

data1 = r.read_var('od550aer', start=2008)







# =============================================================================
# r = pya.io.ReadGridded('GFDL-AM4-met2010_AP3-CTRL')
# 
# ss = r.read_var('od550ss', start=2010)
# try:
#     dust = r.read_var('od550dust', start=2010)
# except Exception as e:
#     print(repr(e))
#     
# 
# 
# 
# =============================================================================
