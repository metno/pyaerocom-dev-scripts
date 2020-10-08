#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 13:23:53 2020

@author: jonasg
"""
from datetime import datetime
import glob
import os
import requests
import shutil
import tqdm
import zipfile
import pyaerocom as pya

def delete_make_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    return path

def download_file(url, filename):
    chunks = 1024
    req = requests.get(url, stream=True)
    with open(filename, 'wb') as data:
        pbar = tqdm.tqdm(unit='B',total=int(req.headers['Content-Length']))
        for chunk in req.iter_content(chunk_size=chunks):
            if chunk:
                pbar.update(len(chunk))
                data.write(chunk)
            else:
                print('Bla')

def cleanup(*locs):
    for loc in locs:
        if os.path.exists(loc):
            if os.path.isdir(loc):
                shutil.rmtree(loc)
            else:
                os.remove(loc)

NOWSTR = datetime.now().strftime('%Y%m%d')

DATA_ID = 'AeronetSunV3Lev2.daily'

OUTBASE = os.path.join(pya.const.DOWNLOAD_DATADIR, DATA_ID)
OUTDATADIR = os.path.join(OUTBASE, 'renamed')

delete_make_dir(OUTBASE)
delete_make_dir(OUTDATADIR)

with open(os.path.join(OUTDATADIR, 'Revision.txt'), 'w') as f:
    f.write(NOWSTR)

AERONETWEB = 'https://aeronet.gsfc.nasa.gov/'
DATA_DISCLAIMER = 'https://aeronet.gsfc.nasa.gov/new_web/data_usage.html'
DATAURL = 'https://aeronet.gsfc.nasa.gov/data_push/V3/All_Sites_Times_Daily_Averages_AOD20.zip'

with open(os.path.join(OUTBASE, 'README'), 'w') as f:
    f.write(DATA_ID + 'data\n')
    f.write('This data was automatically downloaded by pyaerocom\n')
    f.write('Download date: {}'.format(NOWSTR))
    f.write('AERONET WEBSITE: {}\n'.format(AERONETWEB))
    f.write('DATA USAGE GUIDELINES: {}\n'.format(DATA_DISCLAIMER))

DOWNLOAD_FILE = os.path.join(pya.const.LOCAL_TMP_DIR, 'AeronetTmp.zip')

if os.path.exists(DOWNLOAD_FILE):
    os.remove(DOWNLOAD_FILE)

pya.const.print_log.info('Downloading {} data'.format(DATA_ID))
download_file(DATAURL, DOWNLOAD_FILE)

UNZIPDIR = os.path.join(pya.const.LOCAL_TMP_DIR, 'unzipped')
if os.path.exists(UNZIPDIR):
    shutil.rmtree(UNZIPDIR)
os.mkdir(UNZIPDIR)

with zipfile.ZipFile(DOWNLOAD_FILE, 'r') as zip_ref:
    zip_ref.extractall(UNZIPDIR)

files = glob.glob('{}/*.dat'.format(UNZIPDIR))
if len(files) != 1:
    raise Exception('FATAL')

from MakeAeronetStationFiles import WriteAeronetFiles
WriteAeronetFiles(files[0], OUTDATADIR)

cleanup(DOWNLOAD_FILE, UNZIPDIR)





