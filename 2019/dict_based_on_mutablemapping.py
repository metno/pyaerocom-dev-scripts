#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 15:35:27 2019

@author: jonasg
"""
from pyaerocom._lowlevel_helpers import BrowseDict
from collections.abc import MutableMapping
# =============================================================================
# 
# class D1(MutableMapping):
#     
#     def __init__(self, **kwargs):
#         self.update(**kwargs)
#         
#     def __delitem__(self, key):
#         raise NotImplementedError
#     
#     def __getitem__(self, key):
#         return self.__dict__[key]
#     
#     def __setitem__(self, key, val):
#         self.__dict__[key] = val
#         
#     def __iter
#  
# =============================================================================
class D(MutableMapping):
    '''
    Mapping that works like both a dict and a mutable object, i.e.
    d = D(foo='bar')
    and 
    d.foo returns 'bar'
    '''
    # ``__init__`` method required to create instance from class.
    def __init__(self, *args, **kwargs):
        '''Use the object dict'''
        self.blaaaaa='blaaaaaaaaa'
        self._dtime = []
        
        self.__dict__.update(*args, **kwargs)
    
    @property
    def dtime(self):
        return self.__dict__['_dtime']
    
    @dtime.setter
    def dtime(self, val):
        self.__dict__['_dtime'] = val
        
    # The next five methods are requirements of the ABC.
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __delitem__(self, key):
        del self.__dict__[key]
    
    def __iter__(self):
        return iter(self.__dict__)
    
    def __len__(self):
        return len(self.__dict__)
    
    # The final two methods aren't required, but nice for demo purposes:
    def __str__(self):
        '''returns simple dict representation of the mapping'''
        return str(self.__dict__)
    
    def __repr__(self):
        '''echoes class, id, & reproducible representation in the REPL'''
        return '{}'.format(self.__dict__)

def assign_numbers(d):
    for num in range(100):
        d[num] = num
    return d

def iter_items(d):
    for k, v in d.items():
        pass
    
class C(object):
    def __init__(self, **kwargs):
        self.update(**kwargs)
        
    def update(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
    
    def items(self):
        return self.__dict__.items()

    def __setitem__(self, k, v):
        self.__dict__[k] = v
        
    def __repr__(self):
        '''echoes class, id, & reproducible representation in the REPL'''
        return '{}'.format(self.__dict__)
    
    def __str__(self):
        return self.__dict__.__str__()
    
d = D(bla=42, blub=44)

c = C(**d)


print(d)

d.dtime = 456

d1 = dict()
d1.update(d)



d2 = BrowseDict()
d2.update(d1)

print('MutableMapping ', d, isinstance(d, dict))
print('dict', d1, isinstance(d1, dict))

print('BrowseDict ', d2, isinstance(d, dict))