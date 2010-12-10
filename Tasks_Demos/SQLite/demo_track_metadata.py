"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code demo the use of the track_metadata.db
To create the db, see create_track_metadata_db.py

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
    print 'demo_track_metadata.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print '     tb2332@columbia.edu'
    print 'This codes gives examples on how to query the database track_metadata.db'
    print 'To first create this database, see: create_track_metadata_db.py'
    print 'usage:'
    print '   python demo_track_metadata.py <database path>'
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

    # so there is no confusion, the table name is 'songs'
    TABLENAME = 'songs'

    print '*************** GENERAL SQLITE DEMO ***************************'

    # list all tables in that dataset
    # note that sqlite does the actual job when we call fetchall() or fetchone()
    q = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    res = c.execute(q)
    print "* tables contained in that SQLite file/database (should be only 'songs'):"
    print res.fetchall()

    # list all columns names from table 'songs'
    q = "SELECT sql FROM sqlite_master WHERE tbl_name = 'songs' AND type = 'table'"
    res = c.execute(q)
    print '* get info on columns names (original table creation command):'
    print res.fetchall()[0][0]

    # list all indices
    q = "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='songs' ORDER BY name"
    res = c.execute(q)
    print '* one of the index we added to the table to make things faster:'
    print res.fetchone()

    # find the PRIMARY KEY of a query
    # by default it's called ROWID, it would have been redefined if our primary key
    # was of type INTEGER
    q = "SELECT ROWID FROM songs WHERE artist_name='The Beatles'"
    res = c.execute(q)
    print '* get the primary key (row id) of one entry where the artist is The Beatles:'
    print res.fetchone()
    
    # find an entry with The Beatles as artist_name
    # returns all info (the full table row)
    q = "SELECT * FROM songs WHERE artist_name='The Beatles' LIMIT 1"
    res = c.execute(q)
    print '* get all we have about one track from The Beatles:'
    print res.fetchone()

    print '*************** DEMOS AROUND ARTIST_ID ************************'

    # query for all the artists Echo Nest ID
    # the column name is 'artist_id'
    # DISTINCT makes sure you get each ID returned only once
    q = "SELECT DISTINCT artist_id FROM " + TABLENAME
    res = c.execute(q)
    artists = res.fetchall() # does the actual job of searching the db
    print '* found',len(artists),'unique artist IDs, response looks like:'
    print artists[:3]

    # more cumbersome, get unique artist ID but with one track ID for each.
    # very usefull, it gives you a HDF5 file to query if you want more
    # information about this artist
    q = "SELECT artist_id,track_id FROM songs GROUP BY artist_id"
    res = c.execute(q)
    artist_track_pair = res.fetchone()
    print '* one unique artist with some track (chosen at random) associated with it:'
    print artist_track_pair

    # get artists having only one track in the database
    q = "SELECT artist_id,track_id FROM songs GROUP BY artist_id HAVING ( COUNT(artist_id) = 1 )"
    q += " ORDER BY RANDOM()"
    res = c.execute(q)
    artist_track_pair = res.fetchone()
    print '* one artist that has only one track in the dataset:'
    print artist_track_pair

    # get artists with no musicbrainz ID
    # of course, we want only once each artist
    # for demo purpose, we ask for only two at RANDOM
    q = "SELECT artist_id,artist_mbid FROM songs WHERE artist_mbid=''"
    q += " GROUP BY artist_id ORDER BY RANDOM() LIMIT 2"
    res = c.execute(q)
    print '* two random unique artists with no musicbrainz ID:'
    print res.fetchall()


    print '*************** DEMOS AROUND NAMES ****************************'

    # get all tracks by artist The Beatles
    # artist name must be exact!
    # the encode_string function simply deals with ' (by doubling them)
    # and add ' after and before the string.
    q = "SELECT track_id FROM songs WHERE artist_name="
    q += encode_string('The Beatles')
    res = c.execute(q)
    print "* two track id from 'The Beatles', found by looking up the artist by name:"
    print res.fetchall()[:2]

    # we find all release starting by letter 'T'
    # T != t, we're just looking at albums starting with capital T
    # here we use DISTINCT instead of GROUP BY artist_id
    # since its fine that we find twice the same artist, as long as it is not
    # the same (artist,release) pair
    q = "SELECT DISTINCT artist_name,release FROM songs WHERE SUBSTR(release,1,1)='T'"
    res = c.execute(q)
    print '* one unique artist/release pair where album starts with capital T:'
    print res.fetchone()


    print '*************** DEMOS AROUND FLOATS ***************************'

    # get all artists whose artist familiarity is > .8
    q = "SELECT DISTINCT artist_name, artist_familiarity FROM songs WHERE artist_familiarity>.8"
    res = c.execute(q)
    print '* one artist having familiaryt >0.8:'
    print res.fetchone()

    # get one artist with the highest artist_familiarity but no artist_hotttnesss
    # notice the alias af and ah, makes things more readable
    q = "SELECT DISTINCT artist_name, artist_familiarity as af, artist_hotttnesss as ah"
    q += " FROM songs WHERE ah<0 ORDER BY af"
    res = c.execute(q)
    print '* get the artist with the highest familiarity that has no computed hotttnesss:'
    print res.fetchone()

    # close the cursor and the connection
    # (if for some reason you added stuff to the db or alter
    #  a table, you need to also do a conn.commit())
    c.close()
    conn.close()


    
