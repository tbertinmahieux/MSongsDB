"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code demo the use of the artist_term.db
To create the db, see create_artist_term_db.py
To view a more basic demo on SQLite, start with
demo_artist_term.py

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


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'"+s.replace("'","''")+"'"


def die_with_usage():
    """ HELP MENU """
    print 'demo_artist_term.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print '     tb2332@columbia.edu'
    print 'This codes gives examples on how to query the database artist_term.db'
    print 'To first create this database, see: create_artist_term_db.py'
    print 'Note that you should first check: demo_track_metadata.py if you are not'
    print 'familiar with SQLite.'
    print 'usage:'
    print '   python demo_artist_term.py <database path>'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # params
    dbfile = sys.argv[1]

    # connect to the SQLite database
    conn = sqlite3.connect(dbfile)

    # from that connection, get a cursor to do queries
    c = conn.cursor()

    # SCHEMA OVERVIEW
    # we got 3 tables
    # table1: name=artists      #cols=1   (artist_id text)
    #    One row per artists, no duplicates, usually alphabetical order
    # table2: name=terms        #cols=1   (term text)
    #    One row per term, no duplicates, usually alphabetical order
    # table3: name=artist_term  #cols=2   (artist_id text, term text)
    #    One row per pair artist_id/term, no duplicate pairs
    #    Entries in table3 are constrained by table1 and table2,
    # e.g. an artist_id must exist in table1 before it is used in table3.
    # NOT ALL ARTISTS HAVE TERMS. They will still all be in table1, but
    # some artists are not in table3 at all.

    print '*************** GENERAL SQLITE DEMO ***************************'

    # list all tables in that dataset
    # note that sqlite does the actual job when we call fetchall() or fetchone()
    q = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    res = c.execute(q)
    print "* tables contained in that SQLite file/database (there should be 3):"
    print res.fetchall()

    # list all indices
    q = "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
    res = c.execute(q)
    print '* indices in the database to make reads faster:'
    print res.fetchall()


    print '*************** ARTISTS TABLE DEMO ****************************'

    # list all artists
    q = "SELECT * FROM artists"
    res = c.execute(q)
    print '* list all known artists in the database (display first 3):'
    print res.fetchall()[:3]

    # list all artists that id starts with ARB
    q = "SELECT artist_id FROM artists WHERE SUBSTR(artist_id,1,3)='ARB' LIMIT 2"
    res = c.execute(q)
    print '* list artists whose ID starts with ARB (we ask for 2 of them):'
    print res.fetchall()


    print '*************** TERMS TABLE DEMO ******************************'

    # list all terms (=tags)
    q = "SELECT * FROM terms"
    res = c.execute(q)
    print '* list all known terms in the database (display first 3):'
    print res.fetchall()[:3]

    # list all terms that start with 'indie'
    q = "SELECT term FROM terms WHERE SUBSTR(term,1,5)='indie' LIMIT 3"
    res = c.execute(q)
    print "* list terms that start with 'indie' (we ask for 3 of them):"
    print res.fetchall()

    # get one badly encoded, fix it...
    # is it a problem only when we write to file???
    # we want to show the usage of t.encode('utf-8')  with t a term


    print '*************** ARTIST / TERM TABLE DEMO **********************'

    #



    
    # DONE
    # close the cursor and the connection
    # (if for some reason you added stuff to the db or alter
    #  a table, you need to also do a conn.commit())
    c.close()
    conn.close()
