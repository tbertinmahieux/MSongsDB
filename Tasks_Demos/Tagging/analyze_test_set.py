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
    print 'analyze_test_set.py'
    print '    by T. Bertin-Mahieux (2011) Columbia University'
    print '       tb2332@columbia.edu'
    print ''
    print 'Code to analyze the test set, and give a benchmark result for'
    print 'automatic tagging based on tag stats (no audio analysis)'
    print ''
    print 'USAGE'
    print '   python analyze_test_set.py [FLAGS] <artist_test.txt> <track_metadata.db> <artist_term.db>'
    print 'PARAM'
    print '    artist_test.txt  - list of artists in the test set'
    print '  track_metadata.db  - SQLite database with metadata per track'
    print '     artist_term.db  - SQLite database with Echo Nest terms per artist'
    print 'FLAG'
    print '   -predictionlen n  - number of terms we use to tag every test artist.'
    print '                       interesting to find the best F-1 score'
    print '                       By default, we use the average number of top300 terms'
    print '                       of artists in train se, which is 19.'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # flags
    forced_avgnterm = -1
    while True:
        if sys.argv[1] == '-predictionlen':
            forced_avgnterm = int(sys.argv[2])
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

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
    # create tmp table with test artists in track_metadata connection
    q = "CREATE TEMP TABLE test_artists (artist_id TEXT PRIMARY KEY)"
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

    # create tmp table with top 300 terms
    q = "CREATE TEMP TABLE top300 (term TEXT PRIMARY KEY)"
    conn_at.execute(q)
    for t in top300:
        q = "INSERT INTO top300 VALUES(" + encode_string(t) + ")"
        conn_at.execute(q)
    conn_at.commit()

    # create temp table with test_artists in artist_term conection
    q = "CREATE TEMP TABLE test_artists (artist_id TEXT PRIMARY KEY)"
    conn_at.execute(q)
    conn_at.commit()
    for artist in test_artists:
        q = "INSERT INTO test_artists VALUES('%s')" % artist
        conn_at.execute(q)
    conn_at.commit()

    # in train artists, find avgnterm average number of tags within top 300
    q = "SELECT artist_term.artist_id,Count(artist_term.term) FROM artist_term"
    q += " JOIN top300 ON artist_term.term=top300.term"
    q += " GROUP BY artist_term.artist_id"
    res = conn_at.execute(q)
    artist_count_top300 = filter(lambda x: not x[0] in test_artists, res.fetchall())
    print 'got count for',len(artist_count_top300),'artists'
    assert len(artist_count_top300)+len(test_artists) <= n_artists_with_term,'incoherence'
    print n_artists_with_term-len(test_artists)-len(artist_count_top300),'artists have terms but none in top 300.'
    avgnterm = np.average(map(lambda x: x[1],artist_count_top300))
    print 'In train set, an artist has on average',avgnterm,'terms from top 300 terms.'
    print '************ NOTE **********'
    print 'We ignore artists in train set with no term from top 300.'
    print 'The way the test set was built, test artists are guaranteed'
    print 'to have at least one termfrom top 300.'
    print '****************************'

    # tag test artists with the top avgnterm tags
    avgnterm = int(avgnterm)
    if forced_avgnterm >= 0:
        print 'INSTEAD OF',avgnterm,'TERMS, WE USE PREDICTIONS OF LENGTH',forced_avgnterm
        avgnterm = forced_avgnterm
    tagging_prediction = top300[:avgnterm]
    print 'METHOD: we will tag every test artists with the top',avgnterm,'terms, i.e.:'
    print map(lambda x: x.encode('utf-8'),tagging_prediction)

    # measure precision
    # - For terms in my tagging prediction, I retrieve every test artists, therefore precision
    # is the proportion of artists that were actually tagged with it.
    # - For terms not in my tagging prediction, I retrieve no artists, therefore precision is
    # set to 0
    acc_prop = 0
    for t in tagging_prediction:
        q = "SELECT Count(test_artists.artist_id) FROM test_artists"
        q += " JOIN artist_term ON artist_term.artist_id=test_artists.artist_id"
        q += " WHERE artist_term.term="+encode_string(t)
        res = conn_at.execute(q)
        acc_prop += res.fetchone()[0] * 1. / len(test_artists)
    precision = acc_prop / 300.
    print 'precision is:',precision

    # measure recall
    # - For terms in my tagging prediction, I retrieve every artists, therefore recall is 1.
    # - For terms not in my tagging prediction, I retrieve no artists, therefore recall is 0.
    recall = avgnterm / 300.
    print 'recall is:',recall

    # f-1 score
    print 'F-1 score is:',(precision + recall)/2.
    
    # close connections
    conn_tm.close()
    conn_at.close()
    
