"""
Code to compute and aggregate hashcodes over a large collection
of data, e.g. the whole million song dataset, using multiple
processes.

Many parameters are hard-coded!

For the help menu, simply launch the code:
    python compute_hashcodes_mprocess.py

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
import glob
import time
import copy
import sqlite3
import datetime
import multiprocessing
import numpy as np

# hash codes params
WIN=3
DECAY=.995
NORMALIZE=True
WEIGHT_MARGIN=.60
MAX_PER_FRAME=3
LEVELS = [3]
COMPRESSION=2


def get_all_files(basedir,ext='.h5') :
    """
    From a root directory, go through all subdirectories
    and find all files with the given extension.
    Return all absolute paths in a list.
    """
    allfiles = set()
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files :
            allfiles.add( os.path.abspath(f) )
    return list(allfiles)


def aggregate_dbs(conn, tmpdbpath):
    """
    Aggregate the data from a filled, temporary database,
    to a main one already initialized.
    """
    try:
        CHT.__name__
    except NameError:
        #print 'We import cover hash table'
        import cover_hash_table as CHT
    t1 = time.time()
    conn_tmp = sqlite3.connect(tmpdbpath)
    # get number of hashes tables
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn_tmp.execute(q)
    num_tables = res.fetchone()[0]
    # get all tids
    q = "SELECT ROWID, tid FROM tids"
    res = conn_tmp.execute(q)
    tidid_tid_pairs = res.fetchall()
    # iterate over all these tids
    for tidid, tid in tidid_tid_pairs:
        # iterate over all tables
        for tablecnt in range(1, num_tables + 1):
            table_name = 'hashes' + str(tablecnt)
            q = "SELECT jumpcode, weight FROM " + table_name
            q += " WHERE tidid=" + str(tidid)
            res = conn_tmp.execute(q)
            jcode_weight_pairs = res.fetchall()
            tid_is_in = False
            for jcode, weight in jcode_weight_pairs:
                CHT.add_hash(conn, tid, jcode, weight, tid_is_in=tid_is_in)
                tid_is_in = True
        # commit
        conn.commit()
    # done
    conn_tmp.close()
    # verbose
    timestr = str(datetime.timedelta(seconds=time.time()-t1))
    print 'Aggregated %s in %s.' % (tmpdbpath, timestr)


def my_vacuum(dbpathnew, dbpathold):
    """
    My own vacuum function on cover_hash_table.
    It works by copying and is slow!
    My main use, transform the page size to 4096
    Here because of its use of 'aggregate_dbs'
    """
    if os.path.exists(dbpathnew):
        print 'ERROR: %s already exists.' % dbpathnew
        return
    if not os.path.isfile(dbpathold):
        print 'ERROR: %s is not a file.' % dbpathold
        return
    # create new db
    import cover_hash_table as CHT
    conn = sqlite3.connect(dbpathnew)
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA journal_mode = OFF;') # no ROLLBACK!
    conn.execute('PRAGMA page_size = 4096;')
    conn.execute('PRAGMA cache_size = 500000;') # page_size=4096, 500000->2GB
    CHT.init_db(conn)
    # copy
    aggregate_dbs(conn, dbpathold)
    # reindex
    CHT.reindex(conn)
    # done
    conn.commit()
    conn.close()
    

def create_fill_one_partial_db(filelist=None, outputdb=None):
    """
    This is the main function called by each process
    """
    # assert we have the params
    assert (not filelist is None) and (not outputdb is None), "internal arg passing error...!"
    # must be imported there... maybe... because of local num_hash_tables count
    import cover_hash_table as CHT
    # other imports
    import quick_query_test as QQT # should be replaced in the future
    import fingerprint_hash as FH
    # create output db, including PRAGMA
    conn = sqlite3.connect(outputdb)
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA journal_mode = OFF;') # no ROLLBACK!
    conn.execute('PRAGMA cache_size = 1000000;') # default=2000, page_size=1024
    CHT.init_db(conn)
    # iterate over files
    cnt_tid_added = 0
    for filepath in filelist:
        # get bthcroma
        btchroma = QQT.get_cpressed_btchroma(filepath, compression=COMPRESSION)
        if btchroma is None:
            continue
        # get tid from filepath (faster than querying h5 file, less robust)
        tid = os.path.split(os.path.splitext(filepath)[0])[1]
        # get jumps
        landmarks = FH.get_landmarks(btchroma, decay=DECAY, max_per_frame=MAX_PER_FRAME)
        jumps = FH.get_jumps(landmarks, win=WIN)
        cjumps = FH.get_composed_jumps(jumps, levels=LEVELS, win=WIN)
        # add them
        jumpcodes = map(lambda cj: FH.get_jumpcode_from_composed_jump(cj, maxwin=WIN), cjumps)
        CHT.add_jumpcodes(conn, tid, jumpcodes, normalize=NORMALIZE, commit=False)
        cnt_tid_added += 1
        if cnt_tid_added % 1000 == 0:
            conn.commit()
        # debug
        if cnt_tid_added % 500 == 0:
            print 'We added %d tid in the hash table(s) of %s.' % (cnt_tid_added,
                                                                   outputdb)
    # we index
    CHT.reindex(conn)
    # close connection
    conn.close()
    # done
    return

# error passing problems
class KeyboardInterruptError(Exception):
    pass

# for multiprocessing
def create_fill_one_partial_db_wrapper(args):
    """ wrapper function for multiprocessor, calls run_steps """
    try:
        create_fill_one_partial_db(**args)
    except KeyboardInterrupt:
        raise KeyboardInterruptError()
    

def die_with_usage():
    """ HELP MENU """
    print 'compute_hashcodes_mprocess.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print ''
    print 'Code to extract all hashcodes from a give folder of'
    print 'data, e.g. the whole millin song dataset.'
    print 'Creates as many db as process, then aggregate them into one'
    print 'USAGE'
    print '   python compute_hashcodes_mprocess.py <maindir> <output.db> <nthreads>'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # params
    maindir = sys.argv[1]
    outputdb = sys.argv[2]
    nthreads = int(sys.argv[3])

    # sanity checks
    if not os.path.isdir(maindir):
        print 'ERROR: %s is not a directory.' % maindir
        sys.exit(0)
    if os.path.exists(outputdb):
        print 'ERROR: %s already exists.' % outputdb
        sys.exit(0)
    if nthreads < 1 or nthreads > 8:
        print 'REALLY? %d processes?' % nthreads
        sys.exit(0)
    
    # FIRST PASS, ITERATE OVER ALL FILES
    # temp db list
    if nthreads == 1:
        tmpdbs = [outputdb]
    else:
        tmpdbs = map(lambda n: outputdb + '_tmp' + str(n) + '.db', range(nthreads))
        for tdb in tmpdbs:
            if os.path.exists(tdb):
                print 'ERROR: tmp db %s already exists.' % tdb
                sys.exit(0)
    # list all files
    allfiles = get_all_files(maindir)
    print 'We got %d h5 files.' % len(allfiles)
    files_per_thread = int(len(allfiles) * 1. / nthreads + 1.)
    print 'That gives us ~%d files per thread.' % files_per_thread
    # params
    params_list = []
    for k in range(nthreads):
        # params for one specific thread
        p = {'outputdb': copy.deepcopy(tmpdbs[k]),
             'filelist': copy.deepcopy(allfiles[files_per_thread * k:
                                                files_per_thread * (k + 1)])}
        params_list.append(p)
    # create pool, launch using the list of params
    # we underuse multiprocessing, we will have as many processes
    # as jobs needed
    pool = multiprocessing.Pool(processes=nthreads)
    try:
        pool.map(create_fill_one_partial_db_wrapper, params_list)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print 'MULTIPROCESSING'
        print 'stopping multiprocessing due to a keyboard interrupt'
        pool.terminate()
        pool.join()
    except Exception, e:
        print 'MULTIPROCESSING'
        print 'got exception: %r, terminating the pool' % (e,)
        pool.terminate()
        pool.join()

    # SECOND PASS, AGGREGATE (ONE THREAD)
    if nthreads == 1:
        print 'We are done (there was one thread, no aggregation!)'
        sys.exit(0)
    # create final output
    import cover_hash_table as CHT
    conn = sqlite3.connect(outputdb)
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA journal_mode = OFF;') # no ROLLBACK!
    conn.execute('PRAGMA page_size = 4096;')
    conn.execute('PRAGMA cache_size = 500000;') # page_size=4096, 500000->2GB
    CHT.init_db(conn)
    print 'Final db initialized (including PRAGMA settings)'

    # iterate over temporary dbs
    for tdb in tmpdbs:
        aggregate_dbs(conn, tdb)
    # index the final db
    CHT.reindex(conn)
    # all done
    conn.commit()
    conn.close()
    print 'ALL DONE! you should delete the temporary databases...'
    print tmpdbs
