#!/usr/bin/env python
"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code splits the full musiXmatch dataset into train and
test using the same split as for automatic tagging.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.
http://labrosa.ee.columbia.edu/millionsong/

Copyright 2011, Thierry Bertin-Mahieux

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
import sqlite3


def die_with_usage():
    """ HELP MENU """
    print 'split_mxm_dataset.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print 'This code splits the full musiXmatch dataset based on the'
    print 'artist split used for automatic music tagging.'
    print 'This code is provided more as a demo than anything else,'
    print 'you should have received the musiXmatch dataset alredy split.'
    print ''
    print 'USAGE:'
    print '  ./split_mxm_dataset.py <mxmset> <tmdb> <test_aids> <train> <test>'
    print 'PARAMS:'
    print '     <mxmset>  - full musiXmatch dataset'
    print '       <tmdb>  - SQLite database track_metadata.db'
    print '  <test_aids>  - list of test artist IDs (for automatic tagging)'
    print '      <train>  - output train file'
    print '       <test>  - output test file'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 6:
        die_with_usage()

    # params
    mxm_dataset = sys.argv[1]
    tmdb = sys.argv[2]
    testartistsf = sys.argv[3]
    trainf = sys.argv[4]
    testf = sys.argv[5]

    # sanity checks
    if not os.path.isfile(mxm_dataset):
        print 'ERROR: %s does not exist.' % mxm_dataset
        sys.exit(0)
    if not os.path.isfile(tmdb):
        print 'ERROR: %s does not exist.' % tmdb
        sys.exit(0)
    if not os.path.isfile(testartistsf):
        print 'ERROR: %s does not exist.' % testartistsf
        sys.exit(0)
    if os.path.isfile(trainf):
        print 'ERROR: %s already exists.' % trainf
        sys.exit(0)
    if os.path.isfile(testf):
        print 'ERROR: %s already exists.' % testf
        sys.exit(0)

    # open connection to track_metadata.db
    conn = sqlite3.connect(tmdb)

    # load test artists, put them in the database
    q = "CREATE TEMP TABLE testaids (aid TEXT PRIMARY KEY)"
    conn.execute(q)
    f = open(testartistsf, 'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '' or line[0] == '#':
            continue
        q = "INSERT INTO testaids VALUES ('" + line.strip() + "')"
        conn.execute(q)
    f.close()
    conn.commit()
    # verbose: check number of artists
    q = "SELECT aid FROM testaids"
    res = conn.execute(q)
    print 'We have %d test artists.' % len(res.fetchall())

    def is_test(tid):
        """
        Create simple function to decide if a song is from a test artist
        based on its track ID
        """
        q = "SELECT testaids.aid FROM testaids JOIN songs"
        q += " ON testaids.aid=songs.artist_id"
        q += " WHERE songs.track_id='" + tid + "'"
        q += " LIMIT 1"
        res = conn.execute(q)
        if len(res.fetchall()) == 0:
            return False
        return True

    # we open dataset and output files and start writing
    fIn = open(mxm_dataset, 'r')
    train = open(trainf, 'w')
    test = open(testf, 'w')

    # write intro to output file
    train.write('# TRAINING SET\n')
    test.write('# TESTING SET\n')

    # stats for verbose / debugging
    cnt_train = 0
    cnt_test = 0

    # iterate over lines in the full musiXmatch dataset
    for line in fIn.xreadlines():
        if line == '' or line.strip() == '':
            continue
        # comment
        if line[0] == '#':
            train.write(line)
            test.write(line)
            continue
        # list of words
        if line[0] == '%':
            train.write(line)
            test.write(line)
            continue
        # normal line (lyrics for one track)
        tid = line.split(',')[0]
        if is_test(tid):
            cnt_test += 1
            test.write(line)
        else:
            cnt_train += 1
            train.write(line)

    # we close the files
    fIn.close()
    train.close()
    test.close()

    # close SQLite connection to track_metadata.db
    conn.close()

    # done
    print 'DONE! We have %d train tracks and %d test tracks' % (cnt_train,
                                                                cnt_test)
