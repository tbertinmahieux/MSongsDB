"""
Code to query a filled hash_cover table
(using compute_hashcodes_mprocess most likely)
from a set of cliques (the SHS train or test set)

For the help menu, simply launch the code:
    python query_for_covers_mprocess.py

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
import copy
import time
import tables
import sqlite3
import datetime
import numpy as np
import multiprocessing


WEIGHT_MARGIN=.6
CACHE_SIZE=3500000 # per thread, '1000000'-> 1GB
                   # if page_size==4096, we divide by 4


def read_cover_list(filename):
    """
    Read shs_dataset_train.txt or similarly formatted file.
    Return
      * clique -> tids dict
      * clique -> name
    clique are random integer numbers
    """
    clique_tid = {}
    clique_name = {}
    f = open(filename, 'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '' or line[0] == '#':
            continue
        if line[0] == '%':
            clique_id = len(clique_tid) + 1
            clique_name[clique_id] = line.strip()
            continue
        tid = line.strip().split('<SEP>')[0]
        if clique_id in clique_tid.keys():
            clique_tid[clique_id].append(tid)
        else:
            clique_tid[clique_id] = [tid]
    num_tids = sum(map(lambda a: len(a), clique_tid.values()))
    print 'Found %d cliques for a total of %d tids in %s.' % (len(clique_tid), num_tids,
                                                              filename)
    return clique_tid, clique_name


def init_h5_result_file(h5, expectedrows=50000):
    """
    Receives a h5 file that has just been created,
    creates the proper arrays:
     - query
     - target
     - position
     - n_results
    """
    group = h5.createGroup("/",'results','general, sole group')
    h5.createEArray(group,'query',tables.StringAtom(18,shape=()),(0,),
                    'tid of the query',
                    expectedrows=expectedrows)
    h5.createEArray(group,'target',tables.StringAtom(18,shape=()),(0,),
                    'tid of the target',
                    expectedrows=expectedrows)
    h5.createEArray(group,'pos',tables.IntAtom(shape=()),(0,),
                    'position of the target in the result list',
                    expectedrows=expectedrows)
    h5.createEArray(group,'n_results',tables.IntAtom(shape=()),(0,),
                    'lenght of the result list returned by query',
                    expectedrows=expectedrows)
    # done
    return


def query_one_thread(dbpath=None, clique_tid=None, outputf=None):
    """
    Query the database given a set of queries, put the result
    in a... HDF5 file?
    """
    assert not dbpath is None
    assert not clique_tid is None
    assert not outputf is None
    # verbose
    n_cover_songs = sum(map(lambda l: len(l), clique_tid.values()))    
    print 'For tmp output %s, we got %d cliques (%d cover songs).' % (outputf,
                                                                      len(clique_tid),
                                                                      n_cover_songs)
    print 'dbpath = %s' % dbpath
    # import cover_hash_table with code to query
    import cover_hash_table as CHT
    # create tmp output
    h5 = tables.openFile(outputf, 'a')
    expectedrows = sum(map(lambda l: len(l) * (len(l) - 1),
                           clique_tid.values()))
    init_h5_result_file(h5, expectedrows=expectedrows)
    # get toal_tids
    conn = sqlite3.connect(dbpath)
    q = "SELECT DISTINCT tid FROM tids"
    res = conn.execute(q)
    total_tids = len(res.fetchall())
    conn.close()
    # query every clique
    n_queries = 0
    cnt_not_matched = 0
    cnt_cliques = 0
    # start time
    for cliqueid, tids in clique_tid.items():
        # open connection, add pragma stuff
        conn = sqlite3.connect(dbpath)
        conn.execute('PRAGMA temp_store = MEMORY;') # useless?
        conn.execute('PRAGMA synchronous = OFF;') # useless?
        conn.execute('PRAGMA journal_mode = OFF;') # useless?
        res = conn.execute('PRAGMA page_size;')
        page_size = res.fetchone()[0]
        cache_size = CACHE_SIZE
        if page_size == 4096:
            cache_size /= 4
        conn.execute('PRAGMA cache_size = ' + str(cache_size) +';') # default=2000, page_size=1024
        t1 = time.time()
        cnt_cliques += 1
        for tid in tids:
            # get closest match!
            jumps = None; weights = None
            #matches = np.array(CHT.select_matches(conn, jumps, weights,
            #                                      weight_margin=WEIGHT_MARGIN, from_tid=tid))
            verbose = 1 if tid == tids[0] else 0
            matches = np.array(CHT.select_matches2(conn,
                                                   weight_margin=WEIGHT_MARGIN,
                                                   from_tid=tid,
                                                   verbose=verbose))
            if len(matches) == 0:
                print 'no matches for tid:',tid
                #continue
            # check for known covers
            for tid2 in tids:
                if tid2 == tid:
                    continue
                try:
                    pos = np.where(matches==tid2)[0][0]
                except IndexError:
                    pos = int(len(matches) + (total_tids - len(matches)) * .5)
                    cnt_not_matched += 1
                n_queries += 1
                # add to h5
                h5.root.results.query.append([tid])
                h5.root.results.target.append([tid2])
                h5.root.results.pos.append([pos])
                h5.root.results.n_results.append([len(matches)])
            if tid == tids[0]:
                print '[we finished 1st clique query for ouput %s in %d seconds.]' % (outputf, time.time()-t1)
        conn.close()
        h5.flush()
        # verbose
        if cnt_cliques < 20 or cnt_cliques % 5 == 0:
            print 'we did %d cliques for ouput %s' % (cnt_cliques, outputf)
            sys.stdout.flush()
    # done
    h5.flush()
    h5.close()



# error passing problems
class KeyboardInterruptError(Exception):
    pass


# for multiprocessing
def query_one_thread_wrapper(args):
    """ wrapper function for multiprocessor, calls run_steps """
    try:
        query_one_thread(**args)
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


def die_with_usage():
    """ HELP MENU """
    print 'query_for_covers_mprocess.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print 'query a filled database with cliques of covers'
    print 'i.e. the SHS train or test set'
    print ''
    print 'USAGE'
    print '   python query_for_covers_mprocess.py <db> <SHS set> <output> <nthreads>'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 5:
        die_with_usage()

    # params
    dbpath = sys.argv[1]
    coverlistf = sys.argv[2]
    outputf = sys.argv[3]
    nthreads = int(sys.argv[4])
    
    # sanity checks
    if not os.path.isfile(dbpath):
        print 'ERROR:  %s does not exist.' % dbpath
        sys.exit(0)
    if not os.path.isfile(coverlistf):
        print 'ERROR: %s does not exist.' % coverlistf
        sys.exit(0)
    if os.path.exists(outputf):
        print 'ERROR: %s already exists.' % outputf
        sys.exit(0)
    if nthreads < 1 or nthreads > 8:
        print 'Really? %d threads? come on.' % nthreads
        sys.exit(0)

    # read the cliques
    clique_tid, clique_name = read_cover_list(coverlistf)
    print 'We got %d cliques' % len(clique_tid)
    n_cover_songs = sum(map(lambda l: len(l), clique_tid.values()))
    print 'We got %d cover songs' % n_cover_songs

    # FIRST PASS, ITERATE OVER ALL CLIQUES
    # number of processes
    NPROC = 20
    # temp h5 list
    tmph5s = map(lambda n: outputf + '_tmp' + str(n) + '.h5', range(NPROC))
    for th5 in tmph5s:
        if os.path.exists(th5):
            print 'ERROR: tmp h5 %s already exists.' % th5
            sys.exit(0)
    # list all cliques
    cliques = clique_tid.keys()
    n_cliques_per_thread = int(len(cliques) * 1. / NPROC + 1.)
    print 'That gives us ~%d cliques per thread.' % n_cliques_per_thread
    # params
    db_paths = [dbpath]
    for k in range(10):
        copied_db = dbpath + '_' + str(k) + '.db'
        if os.path.isfile(copied_db):
            db_paths.append(copied_db)
    print 'We have %d db copies!' % len(db_paths)
    params_list = []
    for k in range(NPROC):
        # cliques specific to that thread
        thread_c_t = {}
        for c in cliques[n_cliques_per_thread * k: n_cliques_per_thread * (k + 1)]:
            thread_c_t[c] = copy.deepcopy(clique_tid[c])
        # params for one specific thread
        p = {'dbpath': db_paths[k % len(db_paths)],
             'outputf': copy.deepcopy(tmph5s[k]),
             'clique_tid': thread_c_t}
        params_list.append(p)
    # create pool, launch using the list of params
    # we underuse multiprocessing, we will have as many processes
    # as jobs needed
    pool = multiprocessing.Pool(processes=nthreads)
    try:
        pool.map(query_one_thread_wrapper, params_list)
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

    # SECOND PHASE, AGGREGATE

    # open output
    h5 = tables.openFile(outputf, 'a')
    expectedrows = sum(map(lambda l: len(l) * (len(l) - 1),
                           clique_tid.values()))
    init_h5_result_file(h5, expectedrows=expectedrows)

    # iterate over temp h5
    for th5 in tmph5s:
        h5_tmp = tables.openFile(th5, 'r')
        h5.root.results.query.append(np.array(h5_tmp.root.results.query))
        h5.root.results.target.append(np.array(h5_tmp.root.results.target))
        h5.root.results.pos.append(np.array(h5_tmp.root.results.pos))
        h5.root.results.n_results.append(np.array(h5_tmp.root.results.n_results))
        h5_tmp.close()
    h5.flush()
    h5.close()

    # done
    print 'DONE! you should remove tmp files:'
    print tmph5s
    
