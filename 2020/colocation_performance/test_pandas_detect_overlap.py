#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:58:13 2020

@author: jonasg
"""


import pandas as pd
import numpy as np
idx = pd.date_range('1-1-2018', '31-12-2018', freq='D')

idx1 = idx.shift(180)
idx2 = idx.shift(366)
data = np.ones(len(idx))

s0 = pd.Series(data, idx)
s1 = pd.Series(data, idx1)
s2 = pd.Series(data, idx2)

def try_concat(s0, s1):
    try:
        return pd.concat([s0, s1], axis=0, verify_integrity=True)
    except:
        pass

def check_remove_overlap_then_concat(s0, s1):
    overlap = s0.index.intersection(s1.index)
    if len(overlap) > 0:
        removed = s1[overlap]
        s1.drop(index=overlap, inplace=True)
    return pd.concat([s0, s1], axis=0)

df0 = try_concat(s0, s1)
assert df0 == None
df1 = try_concat(s0, s2)
assert len(df1) == len(idx)*2
df2 = check_remove_overlap_then_concat(s0, s1.copy())
assert len(df2) == 545
df3 = check_remove_overlap_then_concat(s0, s2.copy())
assert len(df3) == 365*2
