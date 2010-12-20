"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates an SQLite database with two tables,
one for each unique artist in the Million Song dataset
(based on Echo Nest ID) and one with similarity among
artists according to the Echo Nest:
the first row is 'target', the second row is 'similar',
artists in similar are considered similar to the target.

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


def create_db(filename,artistlist):
    """
    Create a SQLite database with 2 tables
    table1: artists
            contains one column, artist_id
    table2: similarity
            contains two columns, target and similar
            both containing Echo Nest artist ID
            it means that 'similars' are similar to the
            target. It is not necessarily symmetric!
            Also, artists in here have at least one song
            in the dataset!
    INPUT
    - artistlist    list of all artist Echo Nest IDs
    """
    # creates file
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    # create table 1 and fill it
    q = "CREATE TABLE artists (artist_id text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    artistlist = np.sort(artistlist)
    for aid in artistlist:
        q = "INSERT INTO artists VALUES ("
        q += encode_string(aid) + ")"
        c.execute(q)
    conn.commit()
    # create table 2
    q = "CREATE TABLE similarity (target text, similar text, "
    q += "FOREIGN KEY(target) REFERENCES artists(artist_id), "
    q += "FOREIGN KEY(similar) REFERENCES artists(artist_id) )"
    c.execute(q)
    conn.commit()

def fill_from_h5(conn,h5path):
    """
    Fill 'similarity' table from the information regarding the
    artist in that file, i.e. we get his similar artists, check
    if they are in the dataset, add them.
    Doesn't commit, doesn't close conn at the end!
    This h5 file must be for a new artist, we can't have twice the
    same artist entered in the database!

    The info is added to tables: similarity
    as many row as existing similar artists are added
    """
    # get info from h5 file
    h5 = open_h5_file_read(h5path)
    artist_id = get_artist_id(h5)
    sims = get_similar_artists(h5)
    h5.close()
    # add as many rows as terms in artist_term table
    for s in sims:
        q = "SELECT Count(artist_id) FROM artists WHERE"
        q += " artist_id="+encode_string(s)
        res = conn.execute(q)
        found = res.fetchone()[0]
        if found == 1:        
            q = "INSERT INTO similarity VALUES ("
            q += encode_string(artist_id) + "," + encode_string(s)
            q += ")"
            conn.execute(q)
    # done
    return


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
    # index to search by (target) or (target,sims)
    q = "CREATE INDEX idx_target_sim ON similarity ('target','similar')"
    if verbose > 0: print q
    c.execute(q)
    # index to search by (sims) or (sims,target)
    q = "CREATE INDEX idx_sim_target ON similarity ('similar','target')"
    if verbose > 0: print q
    c.execute(q)
    # done (artists table as an implicit index as artist_id is the
    # primary key)
    conn.commit()


def die_with_usage():
    """ HELP MENU """
    print 'Command to create the artist_terms SQLite database'
    print 'to launch (it might take a while!):'
    print '   python create_artist_terms_db.py <MillionSong dir> <artistlist> <artist_similarity.db>'
    print 'PARAMS'
    print '  MillionSong dir        - directory containing .h5 song files in sub dirs'
    print '  artist list            - list in form: artistid<SEP>artist_mbid<SEP>track_id<SEP>...'
    print '  artist_similarity.db   - filename for the database'
    print ''
    print 'for artist list, check:       /Tasks_Demos/NamesAnalysis/list_all_artists.py'
    print '          or (faster!):       /Tasks_Demos/SQLite/list_all_artists_from_db.py'
    sys.exit(0)

    
if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # import HDF5 stuff
    # yes, it is worth of a WTF like this last one:
    # http://thedailywtf.com/Articles/CompareObjectAsIAlertDocumentOrNullIfNotCastable-and-More.aspx
    # but I plan to buy some bad code offsets anyway
    # http://codeoffsets.com/
    pythonsrc = os.path.join(sys.argv[0],'../../../PythonSrc')
    pythonsrc = os.path.abspath( pythonsrc )
    sys.path.append( pythonsrc )
    from hdf5_getters import *

    # params
    maindir = sys.argv[1]
    artistfile = sys.argv[2]
    dbfile = os.path.abspath(sys.argv[3])

    # check if file exists!
    if os.path.exists(dbfile):
        print dbfile,'already exists! delete or provide a new name'
        sys.exit(0)

    # start time
    t1 = time.time()

     # get all track ids per artist
    trackids = []
    artistids = []
    f = open(artistfile,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        artistids.append( line.split('<SEP>')[0] )
        trackids.append( line.split('<SEP>')[2] )
    f.close()
    print 'found',len(trackids),'artists in file:',artistfile

    # create database
    create_db(dbfile,artistids)

    # open connection
    conn = sqlite3.connect(dbfile)
    
    # iterate over files
    cnt_files = 0
    for trackid in trackids:
        f = os.path.join(maindir,path_from_trackid(trackid))
        fill_from_h5(conn,f)
        cnt_files += 1
        if cnt_files % 500 == 0:
            conn.commit()
    conn.commit()

    # create indices
    add_indices_to_db(conn,verbose=0)

    # close connection
    conn.close()

    # done
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'All done (including indices) in',stimelength
