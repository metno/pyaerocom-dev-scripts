#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 13:54:02 2019

@author: jonasg
"""

import sqlite3
import os

FILE = 'testdb'

try:
    os.remove(FILE)
    print('Deleted existing database file')
except Exception as e:
    print(repr(e))
db = sqlite3.connect(FILE)

cursor = db.cursor()

cursor.execute('''
    CREATE TABLE obsdata(id TEXT PRIMARY KEY, 
                         network TEXT,
                         product TEXT, 
                         datalevel INT, 
                         version FLOAT,
                         freq TEXT,
                         path_lustre TEXT)
''')
db.commit()


cursor = db.cursor()

 # Insert example data
cursor.execute('''INSERT INTO obsdata(id, network)
                  VALUES(?,?)''', ('TestId1.Sun', 'Blaaaa'))

print('First data object inserted')
 
db.commit()