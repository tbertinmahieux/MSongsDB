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
    Create a SQLite database where 3 tables
    table1: artists
            contains one column, artist_id
    table2: terms
            contains one column, terms (tags)
    table3: artist_term
            contains two columns, artist_id and term
    """
    # creates file
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    # create table 1
    q = "CREATE TABLE artists (artist_id text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    # create table 2, fill with tags
    q = "CREATE TABLE terms (term text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    taglist = np.sort(taglist)
    for t in taglist: 
        q = "INSERT INTO terms VALUES ("
        q += encode_string(t) + ")"
        c.execute(q)
    conn.commit()
    # create table 3
    q = "CREATE TABLE artist_term (artist_id text, term text, "
    q += "FOREIGN KEY(artist_id) REFERENCES artists(artist_id), "
    q += "FOREIGN KEY(term) REFERENCES terms(term) )"
    c.execute(q)
    conn.commit()
    # close
    c.close()
    conn.close()


def fill_from_h5(conn,h5path):
    """
    Add a row from h5 with he information from this .h5 file
    Doesn't commit, doesn't close conn at the end!
    This h5 file must be for a new artist, we can't have twice the
    same artist entered in the database!

    The info is added to two tables: artists and artist_term
    one row is added to the first one, as many row as needed are
    added to the second one.
    """
    # get info from h5 file
    h5 = hdf5_utils.open_h5_file_append(h5path)
    artist_id = get_artist_id(h5)
    terms = get_artist_terms(h5)
    h5.close()
    # get cursor
    c = conn.cursor()
    # add a row with the new artist_id in artists table
    # if we've seen this artist before, it will be refused
    q = "INSERT INTO artists VALUES ("+encode_string(artist_id)+")"
    c.execute(q)
    # add as many rows as terms in artist_term table
    for t in terms:
        q = "INSERT INTO artist_term VALUES ("
        q += encode_string(artist_id) + "," + encode_string(t)
        q += ")"
        c.execute(q)
    # done
    c.close()

def add_indices_to_db(conn,verbose=0):
    """
    Since the db is considered final, we can add all sorts of indecies
    to make sure the retrieval time is as fast as possible.
    Indecies take up a little space, but they hurt performance only when
    we modify the data (which should not happen)
    This function commits its changes at the end
    
    Note: tutorial on MySQL (close enough to SQLite):
    http://www.databasejournal.com/features/mysql/article.php/10897_1382791_1/Optimizing-MySQL-Queries-and-Indexes.htm
    """
    c = conn.cursor()
    # index to search by (artist_id) or (artist_id,term) on artist_terms table
    q = "CREATE INDEX idx_artist_id ON artist_term ('artist_id','term')"
    if verbose > 0: print q
    c.execute(q)
    # index to search by (term) or (term,artist_id) on artist_terms table
    # might be redundant, we probably just need an index on term since the first
    # one can do the join search
    q = "CREATE INDEX idx_term ON artist_term ('artist_id','term')"
    if verbose > 0: print q
    c.execute(q)
    # we're done, we don't need to add keys to artists and tersm
    # since they have only one column that is a PRIMARY KEY, they have
    # an implicit index
    conn.commit()
    

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
    print '          or (faster!): /Tasks_Demos/SQLite/list_all_artists_from_db.py'
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

   # check if file exists!
    if os.path.exists(dbfile):
        print dbfile,'already exists! delete or provide a new name'
        sys.exit(0) 

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
    print 'found',len(alltags),'tags in file:',tagfile

    # get all track ids
    trackids = []
    f = open(artistfile,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        trackids.append( line.split('<SEP>')[2] )
    f.close()
    print 'found',len(trackids),'artists in file:',artistfile

    # create database
    create_db(dbfile,alltags)
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'tables created after', stimelength

    # open connection
    conn = sqlite3.connect(dbfile)

    # iterate over files
    cnt_files = 0
    for trackid in trackids:
        f = os.path.join(maindir,path_from_trackid(trackid))
        fill_from_h5(conn,f)
        cnt_files += 1
        if cnt_files % 50 == 0:
            conn.commit()
    conn.commit()

    # time update
    t3 = time.time()
    stimelength = str(datetime.timedelta(seconds=t3-t1))
    print 'Looked at',cnt_files,'files, done in',stimelength

    # creates indices
    add_indices_to_db(conn,verbose=0)

    # close connection
    conn.close()

    # done
    t4 = time.time()
    stimelength = str(datetime.timedelta(seconds=t4-t1))
    print 'All done (including indices) in',stimelength

    
