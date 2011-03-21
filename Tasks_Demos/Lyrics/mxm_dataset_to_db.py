#!/usr/bin/env python
"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code puts the musiXmatch dataset (format: 2 text files)
into a SQLite database for ease of use.

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
import sqlite3


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'" + s.replace("'", "''") + "'"


def die_with_usage():
    """ HELP MENU """
    print 'mxm_dataset_to_db.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print 'This code puts the musiXmatch dataset into an SQLite database.'
    print ''
    print 'USAGE:'
    print '  ./mxm_dataset_to_db.py <train> <test> <output.db>'
    print 'PARAMS:'
    print '      <train>  - mXm dataset text train file'
    print '       <test>  - mXm dataset text test file'
    print '  <output.db>  - SQLite database to create'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # params
    trainf = sys.argv[1]
    testf = sys.argv[2]
    outputf = sys.argv[3]

    # sanity checks
    if not os.path.isfile(trainf):
        print 'ERROR: %s does not exist.' % trainf
        sys.exit(0)
    if not os.path.isfile(testf):
        print 'ERROR: %s does not exist.' % testf
        sys.exit(0)
    if os.path.exists(outputf):
        print 'ERROR: %s already exists.' % outputf
        sys.exit(0)

    # open output SQLite file
    conn = sqlite3.connect(outputf)

    # create tables -> words and lyrics
    q = "CREATE TABLE words (word TEXT PRIMARY KEY)"
    conn.execute(q)
    q = "CREATE TABLE lyrics (track_id,"
    q += " mxm_tid INT,"
    q += " word TEXT,"
    q += " count INT,"
    q += " is_test INT,"
    q += " FOREIGN KEY(word) REFERENCES words(word))"
    conn.execute(q)

    # get words, put them in the words table
    f = open(trainf, 'r')
    for line in f.xreadlines():
        if line == '':
            continue
        if line[0] == '%':
            topwords = line.strip()[1:].split(',')
            f.close()
            break
    for w in topwords:
        q = "INSERT INTO words VALUES("
        q += encode_string(w) + ")"
        conn.execute(q)
    conn.commit()
    # sanity check, make sure the words were entered according
    # to popularity, most popular word should have ROWID 1
    q = "SELECT ROWID, word FROM words ORDER BY ROWID"
    res = conn.execute(q)
    tmpwords = res.fetchall()
    assert len(tmpwords) == len(topwords), 'Number of words issue.'
    for k in range(len(tmpwords)):
        assert tmpwords[k][0] == k + 1, 'ROWID issue.'
        assert tmpwords[k][1].encode('utf-8') == topwords[k], 'ROWID issue.'
    print "'words' table filled, checked."

    # we put the train data in the dataset
    f = open(trainf, 'r')
    cnt_lines = 0
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        if line[0] in ('#', '%'):
            continue
        lineparts = line.strip().split(',')
        tid = lineparts[0]
        mxm_tid = lineparts[1]
        for wordcnt in lineparts[2:]:
            wordid, cnt = wordcnt.split(':')
            q = "INSERT INTO lyrics"
            q += " SELECT '" + tid + "', " + mxm_tid + ", "
            q += " words.word, " + cnt + ", 0"
            q += " FROM words WHERE words.ROWID=" + wordid
            conn.execute(q)
        # verbose
        cnt_lines += 1
        if cnt_lines % 15000 == 0:
            print 'Done with %d train tracks.' % cnt_lines
            conn.commit()
    f.close()
    conn.commit()
    print 'Train lyrics added.'

    # we put the test data in the dataset
    # only difference from train: is_test is now 1
    f = open(testf, 'r')
    cnt_lines = 0
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        if line[0] in ('#', '%'):
            continue
        lineparts = line.strip().split(',')
        tid = lineparts[0]
        mxm_tid = lineparts[1]
        for wordcnt in lineparts[2:]:
            wordid, cnt = wordcnt.split(':')
            q = "INSERT INTO lyrics"
            q += " SELECT '" + tid + "', " + mxm_tid + ", "
            q += " words.word, " + cnt + ", 1"
            q += " FROM words WHERE words.ROWID=" + wordid
            conn.execute(q)
        # verbose
        cnt_lines += 1
        if cnt_lines % 15000 == 0:
            print 'Done with %d test tracks.' % cnt_lines
            conn.commit()
    f.close()
    conn.commit()
    print 'Test lyrics added.'

    # create indices
    q = "CREATE INDEX idx_lyrics1 ON lyrics ('track_id')"
    conn.execute(q)
    q = "CREATE INDEX idx_lyrics2 ON lyrics ('mxm_tid')"
    conn.execute(q)
    q = "CREATE INDEX idx_lyrics3 ON lyrics ('word')"
    conn.execute(q)
    q = "CREATE INDEX idx_lyrics4 ON lyrics ('count')"
    conn.execute(q)
    q = "CREATE INDEX idx_lyrics5 ON lyrics ('is_test')"
    conn.execute(q)
    conn.commit()
    print 'Indices created.'

    # close output SQLite connection
    conn.close()
