---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.4.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import os
from EMEP_to_Aerocom import *
```

## Conversion settings

```python
basepath = '/home/eirikg/Desktop/pyaerocom/data/2020_AerocomHIST/'
store = '/home/eirikg/Desktop/pyaerocom/data/2020_AerocomHIST/processed'
data_id = 'EMEP-met2010'

years = [2000]
ts_types = ['monthly']
paths = [os.path.join(basepath, '{}_GLOB1_2010met'.format(year)) for year in years]
```

## Convert files

```python
for ts_type in ts_types:
    for (path, year) in  zip(paths, years):
        EMEP_to_aerocom(path, store, ts_type, year, data_id)
```

## Check converted files

```python
# Setup directories and readers
# Control: files converted with EMEP bash script
# Convert: files converted with ReadEMEP

## Lustre
# control_dir = '/lustre/storeA/project/aerocom/aerocom-users-database/AEROCOM-PHASE-III-2019/EMEPrv4.33-met2010_HIST/renamed'
# convert_dir = store

## Locally
control_dir = '/home/eirikg/Desktop/pyaerocom/data/2020_AerocomHIST/control'
convert_dir = store
data_id = "EMEPrv4.33-met2010"
control_reader = ReadGridded(data_dir=control_dir, data_id=data_id+'-control')
convert_reader = ReadGridded(data_dir=convert_dir, data_id=data_id+'-converted')
```

```python
# Try reading the converted files
for variable in convert_reader.vars_provided:
    convert_reader.read_var(variable)
```

```python
# Check which variables are available, print every variable missing from converted files
var_in_both = []

for variable in control_reader.vars_provided:
    if variable not in convert_reader.vars_provided:
        print('Variable: {} missing from converted files.'.format(variable))
    else:
        var_in_both.append(variable)
```

```python
results = run_compare('monthly', 1950, alltimes=True)
```

```python
results
```
