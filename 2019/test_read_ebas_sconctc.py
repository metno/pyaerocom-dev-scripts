import pyaerocom as pya

import matplotlib.pyplot as plt

plt.close('all')

r = pya.io.ReadEbas()

print(r.PROVIDES_VARIABLES)

data = r.read('conctc')

