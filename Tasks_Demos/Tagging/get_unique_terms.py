"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code is used to get the list of unique terms as fast
as possible. It dumps it to a file which can be used later.

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
import glob
import time
import datetime
import numpy as np


NUMBUCKETS=10000 # hashing parameter


def path_from_trackid(trackid):
    """
    Creates the path from a given trackid
    """
    s = os.path.join(trackid[2],trackid[3])
    s = os.path.join(s,trackid[4])
    s = os.path.join(s,trackid)
    s = s.upper() + '.h5'
    return s

def put_term_in_hash_table(hash_table,term):
    """
    Function to get the hash code of a term and put it in the
    given table
    """
    np.random.seed(hash(term))
    bucket_idx = np.random.randint(NUMBUCKETS)
    hash_table[bucket_idx].add(term)


def die_with_usage():
    """ HELP MENU """
    print 'get_unique_terms.py'
    print '  by T. Bertin-Mahieux (2010) Colubia University'
    print 'GOAL'
    print '  creates a list of unique tags as fast as possible'
    print 'USAGE'
    print '  python get_unique_terms.py <MillionSong dir> <output.txt> (OPTIONAL <artist list>)'
    print 'PARAM'
    print '   MillionSong dir   - MillionSongDataset root directory'
    print '   output.txt        - result text file, one tag per line'
    print '   artist list       - text file: artistID<SEP>artistMBID<SEP>track<SEP>...   OPTIONAL BUT FASTER'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # import HDF5 stuff
    pythonsrc = os.path.join(sys.argv[0],'../../../PythonSrc')
    pythonsrc = os.path.abspath( pythonsrc )
    sys.path.append( pythonsrc )
    import hdf5_utils
    from hdf5_getters import *

    # read params
    maindir = os.path.abspath(sys.argv[1])
    output = os.path.abspath(sys.argv[2])
    artistfile = ''
    if len(sys.argv) > 3:
        artistfile = sys.argv[3]

    # check if file exists!
    if os.path.exists(output):
        print output,'already exists! delete or provide a new name'
        sys.exit(0)

    # start time
    t1 = time.time()

    # create hash table
    hash_table = [None] * NUMBUCKETS
    for k in range(NUMBUCKETS):
        hash_table[k] = set()
    
    # iterate HDF5 files
    cnt_files = 0
    if artistfile == '':
        for root, dirs, files in os.walk(maindir):
            files = glob.glob(os.path.join(root,'*.h5'))
            for f in files :
                h5 = hdf5_utils.open_h5_file_read(f)
                terms = get_artist_terms(h5)
                h5.close()
                # iterate over terms
                for t in terms:
                    put_term_in_hash_table(hash_table,t)
                cnt_files += 1
    else:
        f = open(artistfile,'r')
        trackids = []
        for line in f.xreadlines():
            if line == '' or line.strip() == '':
                continue
            trackids.append( line.split('<SEP>')[2] )
        f.close()
        print 'found',len(trackids),'artist in file:',artistfile
        for trackid in trackids:
            f = os.path.join(maindir,path_from_trackid(trackid))
            h5 = hdf5_utils.open_h5_file_read(f)
            terms = get_artist_terms(h5)
            h5.close()
            # iterate over terms
            for t in terms:
                put_term_in_hash_table(hash_table,t)
            cnt_files += 1

    # list all terms
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'all terms added from',cnt_files,'files in',stimelength
    nUniqueTags = 0
    for k in range(NUMBUCKETS):
        nUniqueTags += len(hash_table[k])
    print 'There are',nUniqueTags,'unique tags.'

    alltags = [None] * nUniqueTags
    cnt = 0
    for k in range(NUMBUCKETS):
        for t in hash_table[k]:
            alltags[cnt] = t
            cnt += 1
    alltags = np.sort(alltags)

    # write to file
    f = open(output,'w')
    for t in alltags:
        f.write(t + '\n')
    f.close()

    # end time
    t3 = time.time()
    stimelength = str(datetime.timedelta(seconds=t3-t1))
    print 'all done in',stimelength
