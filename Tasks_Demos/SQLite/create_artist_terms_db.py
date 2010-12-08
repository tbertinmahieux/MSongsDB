"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates an SQLite dataset that contains one row
per artist and one column per tag. Data is binary, 1 if
an artist was tagged with this tag, 0 otherwise.
Once you found an artist tagged as you want, use the
track_metadata.db database to find a track (or all tracks)
from that artist.

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
try:
    import sqlite3
except ImportError:
    print 'you need sqlite3 installed to use this program'
    sys.exit(0)




def path_from_trackid(trackid):
    """
    Creates the path from a given trackid
    """
    s = os.path.join(trackid[2],trackid[3])
    s = os.path.join(s,trackid[4])
    s = os.path.join(s,trackid)
    s = s.upper() + '.h5'
    return s


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'"+s.replace("'","''")+"'"


def create_db(filename,taglist):
    """
    Create a SQLite database where the first column
    is artist_id and contains the ECHONEST ID,
    then one column per tag.
    """
    # creates file
    conn = sqlite3.connect(filename)
    # create table, first column
    c = conn.cursor()
    q = "CREATE TABLE songs (artist_id text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    # add one column to the table for each tag
    taglist = np.sort(taglist)
    for tag in taglist:
        q = 'ALTER TABLE songs ADD COLUMN '
        q += encode_string(tag) + ' integer DEFAULT 0'
        c.execute(q)
    # commit and close
    conn.commit()
    c.close()
    conn.close()


def fill_from_h5(conn,h5path):
    """
    Add a row from h5 with he information from this .h5 file
    Doesn't commit, doesn't close conn at the end!
    This h5 file must be for a new artist, we can't have twice the
    same artist entered in the database!
    (artist_id is the primary key, therefore unique)
    """
    # get info from h5 file
    h5 = hdf5_utils.open_h5_file_append(h5path)
    artist_id = get_artist_id(h5)
    terms = get_artist_terms(h5)
    h5.close()
    # add a row with artist_id and zeros
    c = conn.cursor()
    q = "INSERT INTO songs ('artist_id') VALUES ('"
    q += artist_id + "'"
    c.execute(q)
    # alter info for cols corresponding to artist terms
    for t in terms:
        q = "UPDATE songs SET " + encode_str(t)
        q += "=1 WHERE 'artist_id'='" + artist_id + "'"
        q += encode_string(t) + ") 1"
        c.execute(q)
    # done
    c.close()


def die_with_usage():
    """ HELP MENU """
    print 'Command to create the track_metadata SQLite database'
    print 'to launch (it might take a while!):'
    print '   python create_artist_terms_db.py <MillionSong dir> <taglist> <artistlist> <artist_term.db>'
    print 'PARAMS'
    print '  MillionSong dir   - directory containing .h5 song files in sub dirs'
    print '  taglist           - list of all possible tags'
    print '  artist list       - list in form: artistid<SEP>artist_mbid<SEP>track_id<SEP>...'
    print '  artist_terms.db   - filename for the database'
    print ''
    print 'for artist list, check: /Tasks_Demos/NamesAnalysis/list_all_artists.py'
    print 'for taglist, check: /Tasks_Demos/Tagging/get_unique_terms.py'
    sys.exit(0)




if __name__ == '__main__':


    # help menu
    if len(sys.argv) < 5:
        die_with_usage()

    # import HDF5 stuff
    pythonsrc = os.path.join(sys.argv[0],'../../../PythonSrc')
    pythonsrc = os.path.abspath( pythonsrc )
    sys.path.append( pythonsrc )
    import hdf5_utils
    from hdf5_getters import *


    # params
    maindir = sys.argv[1]
    tagfile = sys.argv[2]
    artistfile = sys.argv[3]
    dbfile = os.path.abspath(sys.argv[4])

    # start time
    t1 = time.time()

    # get all tags
    alltags = []
    f = open(tagfile,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        alltags.append(line.strip())
    f.close()
    print 'found',len(alltags),'in file:',tagfile

    # get all track ids
    trackids = []
    f = open(artistfile,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        trackids.append( line.split('<SEP>')[2] )
    f.close()
    print 'found',len(trackids),'artists in file:',artistfile

    # iterate over file
    cnt_files = 0
    for trackid in trackids:
        f = os.path.join(maindir,path_from_trackid(trackid))
        fill_from_h5(conn,f)
        cnt_files += 1
        if cnt_files % 50 == 0:
            conn.commit()
    conn.commit()
    conn.close()

    # done
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'Looked at',cnt_files,'files, done in',stimelength

    
