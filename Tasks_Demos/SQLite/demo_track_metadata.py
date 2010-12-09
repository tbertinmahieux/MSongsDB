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




def die_with_usage():
    """ HELP MENU """
    print 'demo_track_metadata.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print '     tb2332@columbia.edu'
    print 'This codes gives example on how to query the database track_metadata.db'
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

    # query for all the artists Echo Nest ID
    # the column name is 'artist_id'
    # DISTINCT makes sure you get each ID returned only once
    q = "SELECT DISTINCT artist_id FROM " + TABLENAME
    print 'query =',q
    res = c.execute(q)
    artists = res.fetchall() # does the actual job of searching the db
    print '* found',len(artists),'unique artist IDs, response looks like:'
    print artists[:3]

    # more cumbersome, get unique artist ID but with one track ID for each.
    # very usefull, it gives you a HDF5 file to query if you want more
    # information about this artist
    q = "SELECT artist_id,track_id FROM songs GROUP BY artist_id HAVING ( COUNT(artist_id) = 1 )"
    res = c.execute(q)
    artist_track_pair = res.fetchone()
    print '* one unique artist with some track (chosen at random) associated with it:'
    print artist_track_pair

    # get artists with no musicbrainz ID
    # of course, we want only once each artist
    # for demo purpose, we ask for only one at RANDOM
    q = "SELECT artist_id,artist_mbid FROM songs WHERE artist_mbid=''"
    q += " GROUP BY artist_id HAVING ( COUNT(artist_id) = 1 )"
    q += " ORDER BY RANDOM LIMIT 1"
    res = c.execute(q)
    print res.fetchone()
    

    # close the cursor and the connection
    # (if for some reason you added stuff to the db or alter
    #  a table, you need to also do a conn.commit())
    c.close()
    conn.close()


    
