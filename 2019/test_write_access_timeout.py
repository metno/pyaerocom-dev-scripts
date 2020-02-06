#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 11:34:57 2018

@author: jonasg
"""
from concurrent.futures import ThreadPoolExecutor
import os

def check_write_access(path, timeout=0.1):
    if not isinstance(path, str):
        # not a path
        return True
    
    pool = ThreadPoolExecutor()

    def _test_write_access(path):
        test = os.path.join(path, '_tmp')
        try:
            os.mkdir(test)
            os.rmdir(test)
            return True
        except Exception as e:
            print('Failed... Reason: {}'.format(repr(e)))
            return False    
        
    def run_timeout(path, timeout):
        future = pool.submit(_test_write_access, path)
        try:
            res = future.result(timeout)
            return res
        except:
            return False
    return run_timeout(path, timeout)

test_dirs = [
        '/',
        '/home/jonasg/',
        '/home/jonasg/lustre/storeB/project/aerocom',
        '/lustre/storeA/project/aerocom/aerocom2/pyaerocom_out/'
        ]


for d in test_dirs:
    print('Test dir: ', d)
    print('Could write: ', check_write_access(d))
    print()