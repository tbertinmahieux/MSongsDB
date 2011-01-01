"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates an SQLite database with 5 tables.
One per unique artist, one per unique Echo Nest term,
one per unique musicbrainz tag, then one table
to link artists and terms, and one table to link
artists and mbtags.

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


def create_db(filename,artistlist,termlist,mbtaglist):
    """
    Create a SQLite database with 5 tables
    table1: artists
            contains one column, artist_id
    table2: terms
            contains one column, term (tags)
    table3: artist_term
            contains two columns, artist_id and term
    table4: mbtags
            contains one column, mbtag (musicbrainz tags)
    table5: artist_mbtag
            contains two columns, artist_id and mbtag
    INPUT
    - artistlist    list of all artist Echo Nest IDs
    - term list     list of all terms (Echo Nest tags)
    - mbtag list    list of all music brainz tags
    """
    # creates file
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    # create table 1
    q = "CREATE TABLE artists (artist_id text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    artistlist = np.sort(artistlist)
    for aid in artistlist:
        q = "INSERT INTO artists VALUES ("
        q += encode_string(aid) + ")"
        c.execute(q)
    conn.commit()
    # create table 2, fill with tags
    q = "CREATE TABLE terms (term text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    termlist = np.sort(termlist)
    for t in termlist: 
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
    # create table 4
    q = "CREATE TABLE mbtags (mbtag text PRIMARY KEY)"
    c.execute(q)
    conn.commit()
    mbtaglist = np.sort(mbtaglist)
    for t in mbtaglist: 
        q = "INSERT INTO mbtags VALUES ("
        q += encode_string(t) + ")"
        c.execute(q)
    conn.commit()
    # create table 5
    q = "CREATE TABLE artist_mbtag (artist_id text, mbtag text, "
    q += "FOREIGN KEY(artist_id) REFERENCES artists(artist_id), "
    q += "FOREIGN KEY(mbtag) REFERENCES mbtags(mbtag) )"
    c.execute(q)
    conn.commit()
    # close
    c.close()
    conn.close()


def fill_from_h5(conn,h5path):
    """
    Add information rgarding the artist in that one h5 song file.
    Doesn't commit, doesn't close conn at the end!
    This h5 file must be for a new artist, we can't have twice the
    same artist entered in the database!

    The info is added to tables: artist_term, artist_mbtag
    as many row as term/mbtag are added
    """
    # get info from h5 file
    h5 = open_h5_file_read(h5path)
    artist_id = get_artist_id(h5)
    terms = get_artist_terms(h5)
    mbtags = get_artist_mbtags(h5)
    h5.close()
    # get cursor
    c = conn.cursor()
    # add as many rows as terms in artist_term table
    for t in terms:
        q = "INSERT INTO artist_term VALUES ("
        q += encode_string(artist_id) + "," + encode_string(t)
        q += ")"
        c.execute(q)
    # add as many rows as mtgs in artist_mbtag table
    for t in mbtags:
        q = "INSERT INTO artist_mbtag VALUES ("
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
    # index to search by (artist_id) or (artist_id,term) on artist_term table
    # samething for      (artist_id)    (artist_id,mbtag)   artist_mbtag
    q = "CREATE INDEX idx_artist_id_term ON artist_term ('artist_id','term')"
    if verbose > 0: print q
    c.execute(q)
    q = "CREATE INDEX idx_artist_id_mbtag ON artist_mbtag ('artist_id','mbtag')"
    if verbose > 0: print q
    c.execute(q)
    # index to search by (term) or (term,artist_id) on artist_terms table
    # might be redundant, we probably just need an index on term since the first
    # one can do the join search
    # samehting for (mbtag,artist_id)
    q = "CREATE INDEX idx_term_artist_id ON artist_term ('term','artist_id')"
    if verbose > 0: print q
    c.execute(q)
    q = "CREATE INDEX idx_mbtag_artist_id ON artist_mbtag ('mbtag','artist_id')"
    if verbose > 0: print q
    c.execute(q)
    # we're done, we don't need to add keys to artists and tersm
    # since they have only one column that is a PRIMARY KEY, they have
    # an implicit index
    conn.commit()
    

def die_with_usage():
    """ HELP MENU """
    print 'Command to create the artist_terms SQLite database'
    print 'to launch (it might take a while!):'
    print '   python create_artist_terms_db.py <MillionSong dir> <termlist> <mbtaglist> <artistlist> <artist_term.db>'
    print 'PARAMS'
    print '  MillionSong dir   - directory containing .h5 song files in sub dirs'
    print '  termlist          - list of all possible terms (Echo Nest tags)'
    print '  mbtaglist         - list of all possible musicbrainz tags'
    print '  artist list       - list in form: artistid<SEP>artist_mbid<SEP>track_id<SEP>...'
    print '  artist_terms.db   - filename for the database'
    print ''
    print 'for artist list, check:       /Tasks_Demos/NamesAnalysis/list_all_artists.py'
    print '          or (faster!):       /Tasks_Demos/SQLite/list_all_artists_from_db.py'
    print 'for termlist and mbtaglist:   /Tasks_Demos/Tagging/get_unique_terms.py'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 6:
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
    termfile = sys.argv[2]
    mbtagfile = sys.argv[3]
    artistfile = sys.argv[4]
    dbfile = os.path.abspath(sys.argv[5])

   # check if file exists!
    if os.path.exists(dbfile):
        print dbfile,'already exists! delete or provide a new name'
        sys.exit(0) 

    # start time
    t1 = time.time()

    # get all terms
    allterms = []
    f = open(termfile,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        allterms.append(line.strip())
    f.close()
    print 'found',len(allterms),'terms in file:',termfile

    # get all mbtags
    allmbtags = []
    f = open(mbtagfile,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        allmbtags.append(line.strip())
    f.close()
    print 'found',len(allmbtags),'mbtags in file:',mbtagfile

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
    create_db(dbfile,artistids,allterms,allmbtags)
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
        if cnt_files % 500 == 0:
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

    
