#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 14:56:35 2019

@author: jonasg
"""

import multiprocessing as mp
import os
import time
p1 = '/home'
p2 = '/lustre/storeA/'

def foo(p):
    os.listdir(p)
  
def foo1():
    
    time.sleep(1e-5)
    
TIMEOUT = 1e-3

def check_fun_timeout_multiproc(fun, timeout_secs=TIMEOUT, fun_args=()):
    # Start foo as a process
    OK = True
    p = mp.Process(target=fun, name="test", args=fun_args)
    p.start()
    p.join(timeout_secs)
    if p.is_alive():# Terminate foo
        print('Function was aborted after {} s'.format(timeout_secs))
        OK =False
        p.terminate()
        # Cleanup
        p.join()  
    
    return OK

if __name__ == '__main__':
    OK_HOME = check_fun_timeout_multiproc(fun=foo, fun_args=(p1,))
    OK_LUSTRE = check_fun_timeout_multiproc(fun=foo, fun_args=(p2,))
    
    print('home access ok: {}'.format(OK_HOME))
    print('lustre access ok: {}'.format(OK_LUSTRE))
        