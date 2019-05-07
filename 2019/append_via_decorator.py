#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
class MyList(object):
    def __init__(self, lst=None):
        if lst is None:
            lst = []
        self._lst = lst
    
    @property
    def lst(self):
        return self._lst
    
    @lst.setter
    def lst(self, val):
        if isinstance(val, list):
            self._lst = val
        else:
            raise ValueError('Invalid input')
      
    def __str__(self):
        return str(self.lst)

        
l = MyList([1,2,3])

print(l)

l.lst.append(4)

print(l)


class MyDict(dict):
    def __init__(self, bla=42, **kwargs):
        super(MyDict, self).__init__(**kwargs)
        self['_bla'] = bla
        
    @property
    def bla(self):
        return self['_bla']
    
    @bla.setter
    def bla(self, val):
        if not isinstance(val, int):
            raise ValueError('Not supported...')
        self['_bla'] = val
# =============================================================================
#         
#     def __setattr__(self, key, val):
#         super(MyDict, self).__setitem__(key, val)
#             
# =============================================================================
    def __str__(self):
        return super(MyDict, self).__str__()
    
class MyDict2(dict):
    pass

d = MyDict()

print(d)

d.bla = 45

print(d)

d2 = MyDict2()