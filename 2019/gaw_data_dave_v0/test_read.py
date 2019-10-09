#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 11:32:13 2019

@author: jonasg
"""

import pyaerocom as pya

import glob

files = glob.glob('*.dat')

print(files)

r = pya.io.ReadGAW()

r.read_file(files[0])