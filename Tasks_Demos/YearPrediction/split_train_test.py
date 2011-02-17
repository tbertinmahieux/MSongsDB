"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to split the list of artists into train and test sets
for year prediction.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.


Copyright 2010, Thierry Bertin-Mahieux

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
import numpy as np
import sqlite3

# random seed, note that we actually use hash(RNDSEED) so it can be anything
RNDSEED='caitlin'



def die_with_usage():
    """ HELP MENU """
    print 'split_train_test.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print '     tb2332@columbia.edu'
    print 'GOAL'
    print '  Split the list of artists into train and test based on track years.'
    print '  We do not split individual tracks because of the producer effect,'
    print '  e.g. we want to predict years, not to recognize artists.'
    print 'USAGE'
    print '  python split_train_test.py <track_metadata.db> <train.txt> <test.txt>'
    print 'PARAMS'
    print ' track_metadata.db    - SQLite database containing metadata for each track'
    print '         train.txt    - list of Echo Nest artist ID'
    print '          test.txt    - list of Echo Nest artist ID'
    print '       subset_tmdb    - track_metadata for the subset, to be sure all subset artists are in train'
    print 'NOTE'
    print '  There are 515576 track with year info.'
    print '  There are 25398 artists with at least one song with year.'
    print '  With current seed, we get 2822 test artists, corresponding'
    print '  to 49436 test tracks.'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 5:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output_train = sys.argv[2]
    output_test = sys.argv[3]
    subset_tmdb = sys.argv[4]

    # sanity checks
    if not os.path.isfile(dbfile):
        print 'ERROR: database not found:',dbfile
        sys.exit(0)
    if os.path.exists(output_train):
        print 'ERROR:',output_train,'already exists! delete or provide a new name'
        sys.exit(0)
    if os.path.exists(output_test):
        print 'ERROR:',output_test,'already exists! delete or provide a new name'
        sys.exit(0)
    if not os.path.exists(subset_tmdb):
        print 'ERROR:',subset_tmdb,'does not exist.'
        sys.exit(0)

    # open connection
    conn = sqlite3.connect(dbfile)

    # get all tracks with year
    q = "SELECT Count(year) FROM songs WHERE year>0"
    res = conn.execute(q)
    ntracks = res.fetchone()[0]
    print 'Found',ntracks,'tracks for which we have year info.'

    # get all artists with average year
    q = "SELECT artist_id,Avg(year),artist_name FROM songs WHERE year>0 GROUP BY artist_id"
    res = conn.execute(q)
    artists = res.fetchall()
    print 'Found',len(artists),'artists with at least one song for which we have year.'

    # order artist per average year
    ordered_artists = sorted(artists,key=lambda x:x[0]) # so its reporducible, first sort by artist id
    ordered_artists = sorted(artists,key=lambda x:x[1])
    print 'Oldest artist:',ordered_artists[0][2]+'('+str(ordered_artists[0][1])+')'
    print 'Most recent artist:',ordered_artists[-1][2]+'('+str(ordered_artists[-1][1])+')'

    # set random seed
    np.random.seed( hash(RNDSEED) )

    # info about split
    print '*********************************************************'
    print 'We split artists by ordering them according to their'
    print 'average track year. For every 10 artists, we keep one at'
    print 'random for the test set.'
    print '*********************************************************'

    # get subset artists
    conn_subtmdb = sqlite3.connect(subset_tmdb)
    res = conn_subtmdb.execute('SELECT DISTINCT artist_id FROM songs')
    subset_artists = map(lambda x: x[0], res.fetchall())
    conn_subtmdb.close()
    print 'Found',len(subset_artists),'distinct subset artists.'
    
    # split between train and test, every 10 artists, put one at random in test
    train_artists = set()
    test_artists = set()
    artists_per_slice = 10
    nslices = int( len(ordered_artists) / artists_per_slice )
    for k in range(nslices):
        pos1 = k * artists_per_slice
        slice_artists = map(lambda x: x[0], ordered_artists[pos1:pos1+artists_per_slice])
        # get random artists, not in subset
        sanity_cnt = 0
        while True:
            sanity_cnt += 1
            test_pos = np.random.randint(len(slice_artists))
            if not slice_artists[test_pos] in subset_artists:
                break
            assert sanity_cnt < 100,'Cant find artist not in subset'
        for aidx,a in enumerate(slice_artists):
            if aidx == test_pos:
                test_artists.add(a)
            else:
                train_artists.add(a)
    print 'Split done, we have',len(test_artists),'test artists and',len(train_artists),'train artists.'

    # count test tracks
    n_test_tracks = 0
    for a in test_artists:
        q = "SELECT Count(track_id) FROM songs WHERE artist_id='"+a+"' AND year>0"
        res = conn.execute(q)
        n_test_tracks += res.fetchone()[0]
    print 'We have',n_test_tracks,'test tracks out of',str(ntracks)+'.'

    # write train
    train_artists_list = sorted(list(train_artists))
    f = open(output_train,'w')
    for a in train_artists_list:
        f.write(a + '\n')
    f.close()

    # write test
    test_artists_list = sorted(list(test_artists))
    f = open(output_test,'w')
    for a in test_artists_list:
        f.write(a + '\n')
    f.close()

    # close connection
    conn.close()

