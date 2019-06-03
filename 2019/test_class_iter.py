#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 14:34:27 2019

@author: jonasg
"""

import numpy as np


class Dummy(object):
    
    def __init__(self):
        self.a1 = np.arange(10)
        self.a2 = np.arange(10)
        self.idx = -1
        
    def __iter__(self):
        return self
    
    def __next__(self):
        self.idx += 1
        if self.idx == len(self.a1):
            self.idx = -1
            raise StopIteration
        return self.a1[self.idx] * self.a2[self.idx]
    

d = Dummy()

for num in d:
    print(num)
        
    
for num in d:
    print(num)
        