"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code contains code to parse the dataset and list
all artists. It can either be used as a library, or
as a standalone if we want the result to be output to a file.

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


def get_artistid_trackid_artistname(trackfile):
    """
    Utility function, opens a h5 file, gets the 4 following fields:
     - artist Echo Nest ID
     - artist Musicbrainz ID
     - track Echo Nest ID
     - artist name
    It is returns as a triple (,,)
    Assumes one song per file only!
    """
    h5 = hdf5_utils.open_h5_file_read(trackfile)
    assert GETTERS.get_num_songs(h5) == 1,'code must be modified if more than one song per .h5 file'
    aid = GETTERS.get_artist_id(h5)
    ambid = GETTERS.get_artist_mbid(h5)
    tid = GETTERS.get_track_id(h5)
    aname = GETTERS.get_artist_name(h5)
    h5.close()
    return aid,ambid,tid,aname

def list_all(maindir):
    """
    Goes through all subdirectories, open every song file,
    and list all artists it finds.
    It returns a dictionary of string -> tuples:
       artistID -> (musicbrainz ID, trackID, artist_name)
    The track ID is random, i.e. the first one we find for that
    artist. The artist information should be the same in all track
    files from that artist.
    We assume one song per file, if not, must be modified to take
    into account the number of songs in each file.
    INPUT
      maindir  - top directory of the dataset, we will parse all
                 subdirectories for .h5 files
    RETURN
      dictionary that maps artist ID to tuple (MBID, track ID, artist name)
    """
    results = {}
    numfiles = 0
    # iterate over all files in all subdirectories
    for root, dirs, files in os.walk(maindir):
        # keep the .h5 files
        files = glob.glob(os.path.join(root,'*.h5'))
        for f in files :
            numfiles +=1
            # get the info we want
            aid,ambid,tid,aname = get_artistid_trackid_artistname(f)
            assert aid != '','null artist id in track file: '+f
            # check if we know that artist
            if aid in results.keys():
                continue
            # we add to the results dictionary
            results[aid] = (ambid,tid,aname)
    # done
    return results


def die_with_usage():
    """ HELP MENU """
    print 'list_all_artists.py'
    print '   by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'usage:'
    print '  python list_all_artists.py <DATASET DIR> output.txt'
    print ''
    print 'This code lets you list all artists contained in all'
    print 'subdirectories of a given directory.'
    print 'This script puts the result in a text file, but its main'
    print 'function can be used by other codes.'
    print 'The txt file format is: (we use <SEP> as separator symbol):'
    print 'artist Echo Nest ID<SEP>artist Musicbrainz ID<SEP>one track Echo Nest ID<SEP>artist name'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # Million Song Dataset imports, works under Linux
    # otherwise, put the PythonSrc directory in the PYTHONPATH!
    pythonsrc = os.path.join(sys.argv[0],'../../../PythonSrc')
    pythonsrc = os.path.abspath( pythonsrc )
    sys.path.append( pythonsrc )
    import hdf5_utils
    import hdf5_getters as GETTERS

    # params
    maindir = sys.argv[1]
    output = sys.argv[2]

    # sanity checks
    if not os.path.isdir(maindir):
        print maindir,'is not a directory'
        sys.exit(0)
    if os.path.isfile(output):
        print 'output file:',output,'exists, please delete or choose new one'
        sys.exit(0)

    # go!
    t1 = time.time()
    dArtists = list_all(maindir)
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'number of artists found:', len(dArtists),'in',stimelength


    # print to file
    artistids = dArtists.keys()
    try:
        import numpy
        artistids = numpy.sort(artistids)
    except ImportError:
        print 'artists IDs will not be sorted alphabetically (numpy not installed)'
    f = open(output,'w')
    for aid in artistids:
        ambid,tid,aname = dArtists[aid]
        f.write(aid+'<SEP>'+ambid+'<SEP>'+tid+'<SEP>'+aname+'\n')
    f.close()

    # FUN STATS! (require numpy)
    try:
        import numpy as np
    except ImportError:
        print 'no numpy, no fun stats!'
        sys.exit(0)
    import re
    print 'FUN STATS!'
    # name length
    name_lengths = map(lambda x: len(dArtists[x][2]), artistids)
    print 'average artist name length:',np.mean(name_lengths),'(std =',str(np.std(name_lengths))+')'
    # most common word
    dWords = {}
    for ambid,tid,aname in dArtists.values():
        words = re.findall(r'\w+', aname.lower())
        for w in words:
            if w in dWords.keys():
                dWords[w] += 1
            else:
                dWords[w] = 1
    words = dWords.keys()
    wfreqs = map(lambda x: dWords[x], words)
    pos = np.argsort(wfreqs)
    pos = pos[-1::-1]
    print 'number of different words used:',len(words)
    print 'the most used words in artist names are:'
    for p in pos[:5]:
        print '*',words[p],'(freq='+str(wfreqs[p])+')'
    print 'some artists using the 30th most frequent word ('+words[pos[30]]+'):'
    frequentword = words[pos[30]]
    cnt = 0
    for ambid,tid,aname in dArtists.values():
        words = re.findall(r'\w+', aname.lower())
        if frequentword in words:
            print '*',aname
            cnt += 1
        if cnt >= min(5,wfreqs[pos[10]]):
            break
