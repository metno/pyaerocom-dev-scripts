#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 16:02:34 2020

@author: jonasg
"""

import pyaerocom as pya

reader = pya.io.ReadEbas()

files = reader.get_file_list('wetso4')
