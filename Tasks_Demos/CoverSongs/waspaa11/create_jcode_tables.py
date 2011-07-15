"""
Creates one table per hashcode, containing track IDs.

SHOULD BE REPLACE BY A PROPER KEYSTORE!!!!
hashcode -> tids
it could fit in memory and be so much faster!

Copyright 2011, Thierry Bertin-Mahieux <tb2332@columbia.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import datetime
import sqlite3
import numpy as np



def die_with_usage():
    """ HELP MENU """
    print 'create one table per code!'
    print 'USAGE:'
    print '   python create_jcode_tables.py <db>'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # params
    dbpath = sys.argv[1]
    if not os.path.isfile(dbpath):
        print 'ERROR: %s does not exist.' % dbpath
        sys.exit(0)
    print 'We will add tables to %s' % dbpath

    # connect, pragma
    conn = sqlite3.connect(dbpath)
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA journal_mode = OFF;') # no ROLLBACK!
    conn.execute('PRAGMA cache_size = 10000000;') # page_size=1024

    # get nuber of tables
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]

    # get all jcodes
    t1 = time.time()
    jcodes = []
    for tablecnt in range(1, num_tables + 1):
        table_name = 'hashes' + str(tablecnt)
        q = "SELECT DISTINCT jumpcode FROM " + table_name
        res = conn.execute(q)
        jcodes = np.unique(list(jcodes) + map(lambda x: x[0], res.fetchall()))
        print 'After %d tables, we have %d unique jcodes' % (tablecnt,
                                                             len(jcodes))
    t2 = time.time()
    strtime = str(datetime.timedelta(seconds=t2 - t1))
    print 'Jumpcodes extracted in %s' % strtime

    #add jcodes
    q = "CREATE TABLE jcodes (jcode INT PRIMARY KEY)"
    conn.execute(q)
    for jcode in jcodes:
        q = "INSERT INTO jcodes VALUES (" + str(jcode) + ")"
        conn.execute(q)
    conn.commit()
    print 'All unique jcode added into jcodes table'
    
    # create tables
    print 'We start creating tables'
    for jidx in xrange(len(jcodes)):
        jcode = jcodes[jidx]
        s_jcode = str(jcode)
        # create table
        jtable_name = 'hashes_jcode_' + s_jcode
        q = "CREATE TABLE " + jtable_name + " (tidid INT, weight FLOAT)"
        conn.execute(q)
        # fill it
        for tablecnt in range(1, num_tables + 1):
            table_name = 'hashes' + str(tablecnt)
            q = "INSERT INTO " + jtable_name
            q += " SELECT tidid, weight FROM " + table_name
            q += " WHERE jumpcode=" + s_jcode
            conn.execute(q)
        conn.commit()
        # index
        q = "CREATE INDEX idx_jcode_" + s_jcode + " ON " + jtable_name
        q += " (weight)"
        conn.execute(q)
        conn.commit()
        # verbose
        if (jidx + 1) % 5000 == 0:
            strtime = str(datetime.timedelta(seconds=time.time() - t2))
            print 'We did %d jumpcodes (/%d) tables in %s' % (jidx + 1, len(jcodes), strtime)

    # done!
    conn.close()
    print 'Done!'

