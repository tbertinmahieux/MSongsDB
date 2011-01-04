"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to analyze the test set, and give a benchmark result
for automatic tagging based on no audio analysis.

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
import numpy as np
import sqlite3



def die_with_usage():
    """ HELP MENU """
    print 'analyze_test_set.py'
    print '    by T. Bertin-Mahieux (2011) Columbia University'
    print '       tb2332@columbia.edu'
    print ''
    print 'Code to analyze the test set, and give a benchmark result for'
    print 'automatic tagging based on tag stats (no audio analysis)'
    print ''
    print 'USAGE'
    print '   python analyze_test_set.py <artist_test.txt> <track_metadata.db> <artist_term.db>'
    print 'PARAM'
    print '    artist_test.txt  - list of artists in the test set'
    print '  track_metadata.db  - SQLite database with metadata per track'
    print '     artist_term.db  - SQLite database with Echo Nest terms per artist'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # params
    artist_test_file = sys.argv[1]
    track_metadata_db_file = sys.argv[2]
    artist_term_db_file = sys.argv[3]

    # sanity check
    if not os.path.isfile(artist_test_file):
        print 'ERROR: file',artist_test_file,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(track_metadata_db_file):
        print 'ERROR: file',track_metadata_db_file,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(artist_term_db_file):
        print 'ERROR: file',artist_term_db_file,'does not exist.'
        sys.exit(0)

    # load artists
    test_artists = set()
    f = open(artist_test_file,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        test_artists.add(line.strip())
    f.close()
    print 'Found',len(test_artists),'unique test artists.'

    # open connections
    conn_tm = sqlite3.connect(track_metadata_db_file)
    conn_at = sqlite3.connect(artist_term_db_file)

    # get total number of artists
    q = "SELECT Count(artist_id) FROM artists"
    res = conn_at.execute(q)
    n_total_artists = res.fetchone()[0]
    print 'Found',n_total_artists,'artists total.'
    q = "SELECT DISTINCT artist_id FROM artist_term"
    res = conn_at.execute(q)
    n_artists_with_term = len(res.fetchall())
    print 'Found',n_artists_with_term,'artists with at least one term.'

    # count number of files/tracks in the test set
    q = "CREATE TEMP TABLE test_artists (artist_id TEXT)"
    conn_tm.execute(q)
    conn_tm.commit()
    for artist in test_artists:
        q = "INSERT INTO test_artists VALUES('%s')" % artist
        conn_tm.execute(q)
    conn_tm.commit()
    q = "SELECT track_id FROM songs INNER JOIN test_artists"
    q += " ON test_artists.artist_id=songs.artist_id"
    res = conn_tm.execute(q)
    test_tracks = res.fetchall()
    print 'Found',len(test_tracks),'from the test artists.'
    
    # get 300 most used tags
    q = "SELECT term,Count(artist_id) FROM artist_term GROUP BY term"
    res = conn_at.execute(q)
    term_freq_list = res.fetchall()
    term_freq = {}
    for k in term_freq_list:
        term_freq[k[0]] = int(k[1])
    ordered_terms = sorted(term_freq, key=term_freq.__getitem__, reverse=True)
    top300 = ordered_terms[:300]
    print 'Top 300 hundred terms are:',top300[:3],'...',top300[298:]

    # in train artists, find N average number of tags within top 300

    # tag test artists with the top N tags

    # measure precision / recall
    
    # close connections
    conn_tm.close()
    conn_at.close()

    raise NotImplementedError
