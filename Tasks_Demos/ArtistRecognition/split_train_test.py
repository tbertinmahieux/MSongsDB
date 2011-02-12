"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to split the list of songs for artist recognition.

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
from operator import itemgetter
import numpy as np
import sqlite3

# random seed, note that we actually use hash(RNDSEED) so it can be anything
RNDSEED='caitlin'
# number of songs required to consider an artist
NUMSONGS=20

def die_with_usage():
    """ HELP MENU """
    print 'split_train_test.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print '     tb2332@columbia.edu'
    print 'GOAL'
    print '  Split the list of songs into train and test for artist recognition.'
    print '  We only consider artists with at least 20 songs.'
    print '  The training set consists of 15 songs from each of these artists.'
    print 'USAGE'
    print '  python split_train_test.py <track_metadata.db> <train.txt> <test.txt>'
    print 'PARAMS'
    print ' track_metadata.db    - SQLite database containing metadata for each track'
    print '         train.txt    - list of Echo Nest artist ID'
    print '          test.txt    - list of Echo Nest artist ID'
    print 'NOTE: this gives a train set of 271,095 songs and a test set of 532,300 songs.'
    print '      See songs_train.txt and songs_test.txt.'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv)<4:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output_train = sys.argv[2]
    output_test = sys.argv[3]

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

    # open connection
    conn = sqlite3.connect(dbfile)

    # get artists with their number of songs
    q = "SELECT artist_id,Count(track_id) FROM songs GROUP BY artist_id"
    res = conn.execute(q)
    data = res.fetchall()
    sorted_artists = sorted(data,key=itemgetter(1,0),reverse=True)

    # find the last artist with that many songs
    last_pos = np.where(np.array(map(lambda x: x[1],sorted_artists))>=NUMSONGS)[0][-1]
    print 'We have',last_pos+1,'artists with at least',NUMSONGS,'songs.'

    # open output files
    ftrain = open(output_train,'w')
    ftest = open(output_test,'w')

    # random seed
    np.random.seed(hash(RNDSEED))

    # iterate over these artists
    for aid,nsongs in sorted_artists[:last_pos+1]:
        # get songs
        q = "SELECT track_id FROM songs WHERE artist_id='"+aid+"'"
        res = conn.execute(q)
        tracks = map(lambda x: x[0], res.fetchall())
        assert len(tracks)==nsongs,'ERROR: num songs should be '+str(nsongs)+' for '+aid+', got: '+str(len(tracks))
        tracks = sorted(tracks)
        np.random.shuffle(tracks)
        for t in tracks[:15]:
            ftrain.write(t+'<SEP>'+aid+'\n')
        for t in tracks[15:]:
            ftest.write(t+'<SEP>'+aid+'\n')
            
    # close files
    ftrain.close()
    ftest.close()
    
    # close connection
    conn.close()

    # done
    print 'DONE!'
