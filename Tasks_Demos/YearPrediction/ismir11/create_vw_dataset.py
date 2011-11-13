"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Code to create a dataset for the vw machine learning tool on
Year Prediction. Features are mean and covariance of
the timbre features. The task is a regression, year
being the target (brought back to 0-1)

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.


Copyright 2011, Thierry Bertin-Mahieux
parts of this code from Ron J. Weiss

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
import sqlite3
import datetime
import numpy as np
import hdf5_getters as GETTERS


def convert_year(y):
    """
    brings back the year between 0 and 1
    returns a float
    """
    res = (y - 1922.) / (2011.-1922.)
    assert res>=0 and res<=1,'problem in year conversion, '+str(y)+'->'+str(res)
    return res

def fullpath_from_trackid(maindir,trackid):
    """ Creates proper file paths for song files """
    p = os.path.join(maindir,trackid[2])
    p = os.path.join(p,trackid[3])
    p = os.path.join(p,trackid[4])
    p = os.path.join(p,trackid+'.h5')
    return str(p)


def get_train_test_songs(msd_dir,testartists,tmdb):
    """
    Creates two list of songs, one for training and one for testing.
    INPUT
           msd_dir   - main MSD dir, <?>/MillionSong/data
       testartists   - file containing test artist IDs
              tmdb   - SQLite database track_metadata.db
    RETURN
       2 lists: trainsongs, testsongs
    """
    # read test artists
    testartists_set = set()
    if testartists != '':
        f = open(testartists,'r')
        for line in f.xreadlines():
            if line == '' or line.strip() == '':
                continue
            testartists_set.add( line.strip() )
        f.close()
    print 'Found',len(testartists_set),'test artists.'
    # get songlist from track_metadata.db
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
    q = "SELECT track_id FROM songs JOIN trainartists"
    q += " ON trainartists.artist_id=songs.artist_id WHERE year>0"
    res = conn.execute(q)
    data = res.fetchall()
    print 'Found',len(data),'training files from track_metadata.db'
    trainsongs = map(lambda x: fullpath_from_trackid(msd_dir,x[0]),data)
    assert os.path.isfile(trainsongs[0]),'first training file does not exist? '+trainsongs[0]
    q = "SELECT track_id FROM songs JOIN testartists"
    q += " ON testartists.artist_id=songs.artist_id WHERE year>0"
    res = conn.execute(q)
    data = res.fetchall()
    print 'Found',len(data),'testing files from track_metadata.db'
    testsongs = map(lambda x: fullpath_from_trackid(msd_dir,x[0]),data)
    assert os.path.isfile(testsongs[0]),'first testing file does not exist? '+testsongs[0]
    # close db
    conn.close()
    # done
    return trainsongs,testsongs


def extract_features(songlist,outputf):
    """
    Extract features from a list of songs, save them in a give filename
    in MLcomp ready format
    INPUT
        songlist   - arrays of path to HDF5 song files
         outputf   - filename (text file)
    """
    # sanity check
    if os.path.isfile(outputf):
        print 'ERROR:',outputf,'already exists.'
        sys.exit(0)
    # open file
    output = open(outputf,'w')
    # iterate ofer songs
    cnt = 0
    for f in songlist:
        # counter
        cnt += 1
        if cnt % 50000 == 0:
            print 'DOING FILE',cnt,'/',len(songlist)
        # extract info
        h5 = GETTERS.open_h5_file_read(f)
        timbres = GETTERS.get_segments_timbre(h5).T
        year = GETTERS.get_year(h5)
        h5.close()
        # sanity checks
        if year <= 0:
            continue
        if timbres.shape[1] == 0 or timbres.shape[0] == 0:
            continue
        if timbres.shape[1] < 10:
            continue # we can save some space from bad examples?
        # features
        avg = np.average(timbres,1)
        cov = np.cov(timbres)
        covflat = []
        for k in range(12):
            covflat.extend( np.diag(cov,k) )
        covflat = np.array(covflat)
        feats = np.concatenate([avg,covflat])
        # sanity check NaN and INF
        if np.isnan(feats).any() or np.isinf(feats).any():
            continue
        # all good? write to file
        output.write(str(convert_year(year))+' |avgcov')
        for k in range(90):
            output.write(' '+str(k+1)+':%.4f' % feats[k])
        output.write('\n')
    # close file
    output.close()


def die_with_usage():
    """ HELP MENU """
    print 'create_vw_dataset.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print '      copyright (c) TBM, 2011, All Rights Reserved'
    print ''
    print 'Code to create a dataset on year prediction for MLcomp.'
    print 'Features are mean and covariance of timbre features.'
    print 'Target is "year".'
    print ''
    print 'USAGE:'
    print '  python create_vw_dataset.py <MSD_DIR> <testartists> <tmdb> <train> <test>'
    print 'PARAMS'
    print '     MSD_DIR  - main Million Song Dataset dir, <?>/millionsong/data'
    print ' testartists  - file containing test artist IDs, one per line'
    print '        tmdb  - SQLite database track_metadata.db'
    print '       train  - output text file with training data'
    print '        test  - output text file with testing data'
    print ''
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv)<6:
        die_with_usage()

    # params
    msd_dir = sys.argv[1]
    testartists = sys.argv[2]
    tmdb = sys.argv[3]
    outtrain = sys.argv[4]
    outtest = sys.argv[5]

    # sanity checks
    if not os.path.isdir(msd_dir):
        print 'ERROR:',msd_dir,'is not a directory.'
        sys.exit(0)
    if not os.path.isfile(testartists):
        print 'ERROR:',testartists,'is not a file.'
        sys.exit(0)
    if not os.path.isfile(tmdb):
        print 'ERROR:',tmdb,'is not a file.'
        sys.exit(0)
    if os.path.isfile(outtrain):
        print 'ERROR:',outtrain,'already exists.'
        sys.exit(0)
    if os.path.isfile(outtest):
        print 'ERROR:',outtest,'already exists.'
        sys.exit(0)

    # start time
    t1 = time.time()

    # get training and testing songs
    trainsongs,testsongs = get_train_test_songs(msd_dir,testartists,tmdb)
    t2 = time.time()
    stimelen = str(datetime.timedelta(seconds=t2-t1))
    print 'Got train and test songs in',stimelen; sys.stdout.flush()

    # process train files
    extract_features(trainsongs,outtrain)
    t3 = time.time()
    stimelen = str(datetime.timedelta(seconds=t3-t1))
    print 'Done with train songs',stimelen; sys.stdout.flush()

    # process test files
    extract_features(testsongs,outtest)
    t4 = time.time()
    stimelen = str(datetime.timedelta(seconds=t4-t1))
    print 'Done with test songs',stimelen; sys.stdout.flush()

    # done
    t5 = time.time()
    stimelen = str(datetime.timedelta(seconds=t5-t1))
    print 'ALL DONE IN',stimelen; sys.stdout.flush()
