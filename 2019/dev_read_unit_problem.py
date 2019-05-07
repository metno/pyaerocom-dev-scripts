
from pyaerocom.io.readgridded import ReadGridded
gridded_reader = ReadGridded(data_id = "EMEP_rv4.1.1.T2.1_ctl")
data = gridded_reader.read_var(var_name = 'wetso4', ts_type="daily")

print(data.unit)

data.unit = 'mg/m2'

print(data.unit)
