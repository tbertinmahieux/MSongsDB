"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Code to measure a benchmark on year prediction, specifically
what score we get if we apply the average train year to the
whole dataset.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.

Copyright (c) 2011, Thierry Bertin-Mahieux, All Rights Reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import glob
import copy
import tables
import sqlite3
import datetime
import numpy as np


def evaluate(years_real,years_pred,verbose=0):
    """
    Evaluate the result of a year prediction algorithm
    RETURN
      avg diff
      std diff
      avg square diff
      std square diff
    """
    years_real = np.array(years_real).flatten()
    years_pred = np.array(years_pred).flatten()
    if verbose>0:
        print 'Evaluation based on',years_real.shape[0],'examples.'
    assert years_real.shape[0] == years_pred.shape[0],'wrong years length, they dont fit'
    avg_diff = np.average(np.abs(years_real - years_pred))
    std_diff = np.std(np.abs(years_real - years_pred))
    avg_square_diff = np.average(np.square(years_real - years_pred))
    std_square_diff = np.std(np.square(years_real - years_pred))
    # verbose
    if verbose>0:
        print 'avg diff:',avg_diff
        print 'std diff:',std_diff
        print 'avg square diff:',avg_square_diff
        print 'std square diff:',std_square_diff
    # done, return 
    return avg_diff,std_diff,avg_square_diff,std_square_diff

def die_with_usage():
    """ HELP MENU """
    print 'year_pred_benchmark.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print ''
    print 'Script to get a benchmark on year prediction without'
    print 'using features. Also, contains functions to measure'
    print 'our predictions'
    print ''
    print 'USAGE:'
    print '   python year_pred_benchmark.py <test_artists> <track_metadata.db>'
    print 'PARAM:'
    print '      test_artists   - a list of test artist ID'
    print ' track_metadata.db   - SQLite database, comes with the MSD'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    testf = sys.argv[1]
    tmdb = sys.argv[2]
    print 'test artists file:',testf
    print 'track_metadata.db:',tmdb

    # sanity checks
    if not os.path.isfile(testf):
        print 'ERROR: file',testf,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(tmdb):
        print 'ERROR: file',tmdb,'does not exist.'
        sys.exit(0)
        
    # get test artists
    testartists_set = set()
    if testf != '':
        f = open(testf,'r')
        for line in f.xreadlines():
            if line == '' or line.strip() == '':
                continue
            testartists_set.add( line.strip() )
        f.close()

    # get train artists in tmp table
    conn = sqlite3.connect(tmdb)
    q = "CREATE TEMP TABLE testartists (artist_id TEXT)"
    res = conn.execute(q)
    conn.commit()
    for aid in testartists_set:
        q = "INSERT INTO testartists VALUES ('"+aid+"')"
        conn.execute(q)
    conn.commit()
    q = "CREATE TEMP TABLE trainartists (artist_id TEXT)"
    res = conn.execute(q)
    conn.commit()
    q = "INSERT INTO trainartists SELECT DISTINCT artist_id FROM songs"
    q += " EXCEPT SELECT artist_id FROM testartists"
    res = conn.execute(q)
    conn.commit()
    q = "SELECT year FROM songs JOIN trainartists"
    q += " ON trainartists.artist_id=songs.artist_id WHERE year>0"
    res = conn.execute(q)
    trainyears = map(lambda x: x[0], res.fetchall())

    # avg train years
    avg_train_years = np.average(trainyears)
    std_train_years = np.std(trainyears)
    print 'avg train year:',avg_train_years
    print 'std train year:',std_train_years

    # test years
    q = "SELECT year FROM songs JOIN testartists"
    q += " ON testartists.artist_id=songs.artist_id WHERE year>0"
    res = conn.execute(q)
    testyears = map(lambda x: x[0], res.fetchall())

    # done with the connection
    conn.close()

    # avg test years
    avg_test_years = np.average(testyears)
    std_test_years = np.std(testyears)
    print 'avg test year:',avg_test_years
    print 'std test year:',std_test_years

    # the real years are test_years
    # the predicted years are avg_train_years
    predyears = [avg_train_years] * len(testyears)

    # evaluation
    evaluate( testyears, predyears, verbose=1)
    
