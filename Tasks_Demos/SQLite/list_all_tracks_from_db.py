"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates a text file with all track ID, song ID, artist name and
song name. Does it from the track_metadata.db
format is:
trackID<SEP>songID<SEP>artist name<SEP>song title

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
import string
import time
import datetime
import numpy as np
try:
    import sqlite3
except ImportError:
    print 'you need sqlite3 installed to use this program'
    sys.exit(0)


def die_with_usage():
    """ HELP MENU """
    print 'list_all_tracks_from_db.py'
    print '   by T. Bertin-Mahieux (2010) Columbia University'
    print 'Code to create a list of all tracks in the dataset as'
    print 'a text file. Assumes track_metadata.db already exists.'
    print "Format is (IDs are EchoNest's):"
    print 'trackID<SEP>songID<SEP>artist name<SEP>song title'
    print ' '
    print 'usage:'
    print '   python list_all_tracks_from_db.py <track_metadata.db> <output.txt>'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output = sys.argv[2]

    # sanity check
    if not os.path.isfile(dbfile):
        print 'ERROR: can not find database:',dbfile
        sys.exit(0)
    if os.path.exists(output):
        print 'ERROR: file',output,'exists, delete or provide a new name'
        sys.exit(0)

    # start time
    t1 = time.time()

    # connect to the db
    conn = sqlite3.connect(dbfile)

    # get what we want
    q = 'SELECT track_id,song_id,artist_name,title FROM songs'
    res = conn.execute(q)
    alldata = res.fetchall() # takes time and memory!
    
    # close connection to db
    conn.close()

    # sanity check
    if len(alldata) != 1000000:
        print 'NOT A MILLION TRACKS FOUND!'

    # write to file
    f = open(output,'w')
    for data in alldata:
        f.write(data[0]+'<SEP>'+data[1]+'<SEP>')
        f.write( data[2].encode('utf-8') +'<SEP>')
        f.write( data[3].encode('utf-8') + '\n' )
    f.close()

    # done
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'file',output,'created in',stimelength
