"""
This code tries to implement an efficient hash table for cover
songs using python.
The goal is to receive hashes (defined elsewhere) and store them
so we can do easy retireval.
It's actually more of a big lookup table or a fast NN than a full
hashing system.

NOT EFFICIENT! Doing it over, we would use a big dictionary or some
keystore, not an SQL database! Especially for the query part.

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
import itertools
import numpy as np
from operator import itemgetter

INDEX_NAMES = 'idx_jumpcodes_'
NEEDS_REINDEXING = True
MAX_ROWS = 1e7   # max number rows in 'hashes' before using a second table

# FOR DEBUGGING
WIN=3
DECAY=.995
NORMALIZE=True
WEIGHT_MARGIN=.60
MAX_PER_FRAME=3
LEVELS = [3]
COMPRESSION=2

# SLOW (SLIGHTLY BETTER) SET OF HASHES
#WIN=6
#DECAY=.96
#NORMALIZE=True
#WEIGHT_MARGIN=.50
#MAX_PER_FRAME=2
#LEVELS = [1,4]
#COMPRESSION=1


import fingerprint_hash as FH

def get_jump_code(tdiff, pdiff, poffset):
    """
    Encode a jump based on a time difference and a pitch difference.
    The encoding is the following:
      pdiff = (pdiff + 12) % 12
      code = tdiff * 12 + pdiff
    tdiff of zero are accepted!
    """
    return FH.get_jump_code(tdiff, pdiff, poffset)


def rotate_jump_code(jumpcode, rotation):
    """
    From a given jumpcode, and a pitch rotation (0 -> 11)
    return a new jumpcode
    """
    assert rotation >= 0 and rotation < 12
    if rotation == 0:
        return jumpcode
    original_offset = jumpcode % 12
    new_offset = (original_offset + rotation) % 12
    return jumpcode - original_offset + new_offset


def rotate_jump_code_sql(jumpcode, rotation):
    """
    Create a piece of SQL command that rotates the jumpcode
    to the right value
    """
    q = str(jumpcode) + "-" + str(jumpcode) + "%12"
    q += "+(" + str(jumpcode) + "%12+" +str(rotation) + ")%12"
    return q


def init_db(conn_or_path):
    """
    Init the hash table using an open sqlite3 connection.
    If the argument is a string, we create/open the database.
    In both case, we return the connection object.
    """
    # open / get connection
    is_file = type(conn_or_path).__name__ == 'str'
    if is_file:
        conn = sqlite3.connect(conn_or_path)
    else:
        conn = conn_or_path
    # create tables
    q = "CREATE TABLE hashes1 (tidid INT, weight FLOAT, jumpcode INT)"
    conn.execute(q)
    conn.commit()
    q = "CREATE TABLE tids (tid TEXT PRIMARY KEY)"
    conn.execute(q)
    conn.commit()
    q = "CREATE TABLE num_hash_tables (cnt INT PRIMARYKEY)"
    conn.execute(q)
    conn.commit()
    q = "INSERT INTO num_hash_tables VALUES (1)"
    conn.execute(q)
    conn.commit()
    # done, return connection
    return conn

def get_current_hash_table(conn):
    """
    Get the name of the current hash_table
    """
    # get the number
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]
    return 'hashes' + str(num_tables + 1)


def add_hash_table(conn, verbose=1):
    """
    Add a new hash table ebcause the previous one is full,
    i.e. passed the number of max rows
    RETURN NEW NAME
    """
    # get actual number of tables
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]
    if verbose > 0:
        print 'We currently have %d hash tables, we will add a new one.' % num_tables
    # create new table
    table_name = 'hashes' + str(num_tables + 1)
    q = "CREATE TABLE " + table_name + " (tidid INT, weight FLOAT, jumpcode INT)"
    conn.execute(q)
    conn.commit()
    # update number in appropriate table
    q = "DELETE FROM num_hash_tables"
    conn.execute(q)
    q = "INSERT INTO num_hash_tables VALUES (" + str(num_tables + 1) +  ")"
    conn.execute(q)
    conn.commit()
    if verbose > 0:
        print 'Table %s created.' % table_name
    return table_name


def reindex(conn, verbose=1):
    """
    Reindex all hash tables
    """
    # get number of hash tables
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]
    # reindex each table
    for tablecnt in range(1, num_tables+1):
        table_name = 'hashes' + str(tablecnt)
        tableverbose = verbose and (tablecnt == 1 or tablecnt == num_tables)
        reindex_table(conn, table_name, verbose=tableverbose)
    # no needs for further reindexing (do we still use that?)
    NEEDS_REINDEXING = False

def reindex_table(conn, table_name, verbose=0):
    """
    Called by reindex
    Create or recreate the index on hashcodes
    """
    t1 = time.time()
    # check if index exists, delete if needed
    try:
        q = "DROP INDEX " + INDEX_NAMES + table_name + '_1'
        conn.execute(q)
    except sqlite3.OperationalError, e:
        #print 'sqlite error:', e
        pass
    try:
        q = "DROP INDEX " + INDEX_NAMES + table_name + '_2'
        conn.execute(q)
    except sqlite3.OperationalError, e:
        #print 'sqlite error:', e
        pass
    # create index on jump codes
    q = "CREATE INDEX " + INDEX_NAMES + table_name + '_1'
    q += " ON " + table_name + " (jumpcode ASC, weight ASC)"
    conn.execute(q)
    conn.commit()
    if verbose > 0:
        strtime = str(datetime.timedelta(seconds=time.time() - t1))
        print 'REINDEXED THE TABLE %s (jumpcode,weight) IN %s' % (table_name, strtime)
        t2 = time.time()
    # create index on tids
    q = "CREATE INDEX " + INDEX_NAMES + table_name + '_2'
    q += " ON " + table_name + " (tidid ASC)"
    conn.execute(q)
    conn.commit()
    # verbose
    if verbose > 0:
        strtime = str(datetime.timedelta(seconds=time.time() - t2))
        print 'REINDEXED THE TABLE %s (tidid) IN %s' % (table_name, strtime)


# important if we start having many tables
current_hash_table = 'hashes1'

def add_hash(conn, tid, hashcode, weight=1., tid_is_in=False):
    """
    Add a given hashcode (jumpcode) in the hashtable,
    possibly with a given weight (default=1.)
    To makes things faster if we know the tid is already in the tids table,
    set tid_is_in to True
    If tid_is_in is False, we also check for the current hash_table, eventually
    we create a new one
    """
    global current_hash_table
    # we mention we need reindexing
    #NEEDS_REINDEXING = True
    # check for inf
    if np.isinf(weight):
        print 'We got INF weight for tid:', tid
        return []
    # do we know that tid already? insert if not, then get rowid
    if not tid_is_in:
        q = "INSERT OR IGNORE INTO tids VALUES ('" + tid + "')" # the OR IGNORE might be slow....
        conn.execute(q)
        conn.commit()
        # should we still be using the same table?
        q = "SELECT MAX(ROWID) FROM " + current_hash_table
        res = conn.execute(q)
        num_rows = res.fetchone()[0]
        if num_rows > MAX_ROWS:
            current_hash_table = add_hash_table(conn, verbose=1)
    # get tid
    q = "SELECT ROWID FROM tids WHERE tid='" + tid + "'"
    res = conn.execute(q)
    tidid = res.fetchone()[0]
    # add the hashcode / jumpcode
    q = "INSERT INTO " + current_hash_table + " VALUES (" + str(tidid) + ", " + str(weight)
    q += ", " + str(hashcode) + ")"
    conn.execute(q)


def add_jumpcodes(conn, tid, jumpcodes, normalize=False, commit=False):
    """
    From a list of jumps (time diff / pitch diff / pitch offset), add
    them to the hashes table
    PARAMS
        codeoffset    - add some offset to the code,
                        can be useful for different sets of codes
    """
    #weights = np.zeros(MAX_JUMP_CODE + 1, dtype='float')
    weights = {}
    # convert to codes, sum weights
    for code in jumpcodes:
        if code not in weights:
            weights[code] = 1.
        else:
            weights[code] += 1.
    # normalize by... norm?
    if normalize:
        #weights = weights * np.sqrt(np.square(weights).sum())
        wsum = float(np.sum(weights.values()))
        for k in weights.keys():
            #weights[k] /= np.sqrt(wsum) # this works well
            weights[k] /= np.log10(wsum) # this works better
            #weights[k] /= wsum
    # add to table
    for cid, c in enumerate(weights.keys()):
        #if weights[c] > 0.:
        if cid == 0:
            add_hash(conn, tid, c, weights[c])
        else:
            add_hash(conn, tid, c, weights[c], tid_is_in=True)
    # commit
    if commit:
       conn.commit() 
    

def retrieve_hash(conn,hashcode):
    """
    Given a hashcode/jumpcode, returns a list of track_id and weight
    that fit.
    RETURN
       list of (tid, weight)
    """
    # need reindexing?
    #if NEEDS_REINDEXING:
    #    reindex(conn)
    # query
    raise NotImplementedError
    q = "SELECT tid, weight FROM hashes WHERE jumpcode="
    q += str(hashcode)
    res = conn.execute(q)
    # done
    return res.fetchall()



def select_matches(conn, jumps, weights, weight_margin=.1, from_tid=None, verbose=0):
    """
    Select possible cover songs based on a set of jumpcodes and weights.
    PARAMS
       weight_margin    - we look for weights that are within that many
                          percent of the original
       tid_in_db        - if the tid is already in the db, we don't need
                          jumps and weights, we take it from db
    """
    # get number of hash tables
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]
    # create temp table (delete previous one if needed)
    if verbose > 0:
        t1 = time.time()
    conn.execute("DROP INDEX IF EXISTS idx_tmp_j_w")
    try:
        conn.execute("DELETE FROM tmpjumpweights")
    except sqlite3.OperationalError, e:
        #print 'sqlite error:', e
        q = "CREATE TEMP TABLE tmpjumpweights (weight weight FLOAT, jumpcode INT, rotation INT)"
        conn.execute(q)
    try:
        conn.execute("DELETE FROM tmpmatches")
    except sqlite3.OperationalError, e:
        if verbose > 0:
            print 'sqlite error:', e
        q = "CREATE TEMP TABLE tmpmatches (tidid INT, rotation INT, cnt INT)"
        conn.execute(q)
    try:
        conn.execute("DELETE FROM tmpmatchesperrot")
    except sqlite3.OperationalError, e:
        if verbose > 0:
            print 'sqlite error:', e
        q = "CREATE TEMP TABLE tmpmatchesperrot (tidid INT, rotation INT, cnt INT)"
        conn.execute(q)
    conn.commit()
    # add jumps and weights
    if from_tid is None:
        for jump, weight in zip(jumps, weights):
            for rotation in range(12):
                q = "INSERT INTO tmpjumpweights VALUES ("
                q += str(weight) + ", " + str(jump) + ", "
                q += rotate_jump_code_sql(jump, rotation) + ")"
                #print q
                conn.execute(q)
    else: # WAY FASTER for one hash table...
        q = "SELECT ROWID FROM tids WHERE tid='" + from_tid + "'"
        res = conn.execute(q)
        tidid = res.fetchone()
        if tidid is None:
            print 'We dont find the tid:', from_tid
            return []
        tidid = tidid[0]
        for tablecnt in range(1, num_tables + 1):
            table_name = 'hashes' + str(tablecnt)
            for rotation in range(12):
                q = "INSERT INTO tmpjumpweights SELECT"
                q += " weight, " + rotate_jump_code_sql("jumpcode", rotation)
                q += ", " + str(rotation) + " FROM " + table_name
                q += " WHERE tidid=" + str(tidid)
                conn.execute(q)
    conn.commit()
    if verbose > 0:
        t1bis = time.time()
        print 'Jumps / weights added in %f seconds.' % (t1bis - t1)
        sys.stdout.flush()
    #q = "CREATE INDEX idx_tmp_j_w ON tmpjumpweights ('jumpcode', 'weight')"
    #conn.execute(q)
    #conn.commit()
    if verbose > 0:
        t2 = time.time()
        print 'Jumps / weights indexed in %f seconds.' % (t2 - t1bis)
        sys.stdout.flush()
    # select proper tids for all rotations
    for tablecnt in range(1, num_tables + 1):
        #if tablecnt>1:
        #    print 'DEBUG WE BREAK AFTER 1 TABLE!!!'
        #    break
        table_name = 'hashes' + str(tablecnt)
        #"""
        #q = "INSERT INTO tmpmatches"
        #q += " SELECT " + table_name + ".tidid, " + table_name + ".weight, "
        #q += table_name + ".jumpcode, tmpjumpweights.rotation"
        #q += " FROM tmpjumpweights JOIN " + table_name + " ON "
        #q += table_name + ".jumpcode=tmpjumpweights.jumpcode"
        #if weight_margin > 0.:
        #    q += " AND ABS(" + table_name + ".weight-tmpjumpweights.weight)<tmpjumpweights.weight*" + str(weight_margin)
        #"""
        q = "INSERT INTO tmpmatches"
        q += " SELECT " + table_name + ".tidid, tmpjumpweights.rotation, COUNT(" + table_name + ".ROWID)"
        q += " FROM tmpjumpweights JOIN " + table_name + " ON "
        q += table_name + ".jumpcode=tmpjumpweights.jumpcode"
        if weight_margin > 0.:
            #q += " WHERE ABS(" + table_name + ".weight-tmpjumpweights.weight)<tmpjumpweights.weight*" + str(weight_margin)
            q += " WHERE " + table_name + ".weight BETWEEN tmpjumpweights.weight*(1.-"+ str(weight_margin)
            q += ") AND tmpjumpweights.weight*(1.+" + str(weight_margin) + ")"
        q += " GROUP BY " + table_name + ".tidid, tmpjumpweights.rotation"
        conn.execute(q)
        conn.commit() # we might have >50K new rows
        if verbose > 0 and tablecnt == 1:
            print 'Jumps / weights with TID from 1st hash table selected in %f seconds.' % (time.time() - t2)
            sys.stdout.flush()
    conn.commit()
    if verbose > 0:
        t3 = time.time()
        print 'Jumps / weights with TID selected in %f seconds.' % (t3 - t2)
        res = conn.execute("SELECT MAX(cnt) FROM tmpmatches")
        print 'Max cnt is: %d' % res.fetchone()[0]
        sys.stdout.flush()
    # count the number of tid per rotation
    #"""
    #q = "INSERT INTO tmpmatchesperrot"
    #q += " SELECT tidid, rotation, COUNT(tidid) FROM tmpmatches GROUP BY tidid, rotation"
    #conn.execute(q)
    #conn.commit()
    #"""
    q = "INSERT INTO tmpmatchesperrot"
    q += " SELECT tidid, rotation, SUM(cnt) FROM tmpmatches GROUP BY tidid, rotation"
    conn.execute(q)
    conn.commit()
    # index on tids, cnt?
    # ...
    # get max over all rotations
    q = "SELECT tids.tid FROM tmpmatchesperrot"
    q += " JOIN tids ON tids.ROWID=tmpmatchesperrot.tidid"
    q += " GROUP BY tmpmatchesperrot.tidid ORDER BY MAX(tmpmatchesperrot.cnt) DESC"
    res = conn.execute(q)
    conn.commit()
    tids = map(lambda x: x[0], res.fetchall())
    # verbose / debug
    if verbose > 0:
        t5 = time.time()
        print 'Selected TID for all rotations; ordered the %d tids in %f seconds.' % (len(tids),(t5 - t3))
        s = 'Selecting matches, best TID scores were: '
        for tid in tids[:3]:
            q = "SELECT ROWID FROM tids WHERE tid='" + tid + "'"
            res = conn.execute(q)
            tidid = res.fetchone()[0]
            q = "SELECT MAX(cnt) FROM tmpmatchesperrot WHERE tidid=" + str(tidid)
            res = conn.execute(q)
            s += str(res.fetchone()[0]) + ', '
        print s
        sys.stdout.flush()
    # done
    return tids


_KNOWN_JCODES = set()
_ALL_TIDS = []

def select_matches2(conn, weight_margin=.1, from_tid=None, verbose=0):
    """
    Select possible cover songs based on a set of jumpcodes and weights.
    ASSUME WE HAVE ONE TABLE PER JUMPCODE
    PARAMS
       weight_margin    - we look for weights that are within that many
                          percent of the original
       tid_in_db        - if the tid is already in the db, we don't need
                          jumps and weights, we take it from db
    """
    global _ALL_TIDS
    # get number of hash tables
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]
    # create temp table (delete previous one if needed)
    try:
        conn.execute("DELETE FROM tmpjumpweights")
    except sqlite3.OperationalError, e:
        #print 'sqlite error:', e
        q = "CREATE TEMP TABLE tmpjumpweights (weight FLOAT, jumpcode INT, rotation INT)"
        conn.execute(q)
    conn.commit()
    # known jcodes
    if len(_KNOWN_JCODES) == 0:
        q = "SELECT jcode FROM jcodes"
        res = conn.execute(q)
        for jcode in res.fetchall():
            _KNOWN_JCODES.add(jcode[0])
        print 'We know of %d jcodes' % len(_KNOWN_JCODES)
        # let's also do all tids
        q = "SELECT tid FROM tids ORDER BY ROWID ASC"
        res = conn.execute(q)
        _ALL_TIDS = np.concatenate([['tid_error'], np.array(map(lambda x: str(x[0]), res.fetchall()))])
    # start time
    if verbose > 0:
        t1 = time.time()
    # test mega table
    table_tidid_rot = np.zeros((1000000,12), dtype='int')
    if verbose > 0:
        print 'Mega table created'
    # add jumps and weights
    q = "SELECT ROWID FROM tids WHERE tid='" + from_tid + "'"
    res = conn.execute(q)
    tidid = res.fetchone()
    if tidid is None:
        print 'We dont find the tid:', from_tid
        return []
    tidid = tidid[0]
    if verbose > 0:
        print 'tidid =', tidid
    for tablecnt in range(1, num_tables + 1):
        table_name = 'hashes' + str(tablecnt)
        for rotation in range(12):
            q = "INSERT INTO tmpjumpweights SELECT"
            q += " weight, " + rotate_jump_code_sql("jumpcode", rotation)
            q += ", " + str(rotation) + " FROM " + table_name
            q += " WHERE tidid=" + str(tidid)
            conn.execute(q)
    conn.commit()
    if verbose > 0:
        t2 = time.time()
        if verbose > 0:
            print 'Jumps / weights indexed in %f seconds.' % (t2 - t1)
        sys.stdout.flush()
    # get all jumpcodes
    res = conn.execute("SELECT jumpcode, weight, rotation FROM tmpjumpweights")
    jumpcode_weight_r = res.fetchall()
    if verbose > 0:
        print 'Found %d jumpcodes and weights' % len(jumpcode_weight_r)
        sys.stdout.flush()
    # for each jumpcode, get all tids
    t_core_query = 0
    for jumpcode, weight, rotation in jumpcode_weight_r:
        if not jumpcode in _KNOWN_JCODES:
            continue
        # get matching tidid
        jcode_table = 'hashes_jcode_' + str(jumpcode)
        jcode_idx = "idx_jcode_" + str(jumpcode)
        #q = "INSERT INTO tmpmatches "
        #q += "SELECT tidid, weight, " + str(rotation)
        q = "SELECT tidid"#, weight, " + str(rotation)
        q += " FROM (" + jcode_table + " INDEXED BY '" + jcode_idx + "')"
        if weight_margin > 0.:
            #q += " WHERE ABS(" + jcode_table + ".weight-" + str(weight) + ")<" + str(weight * weight_margin)
            w_up = str(weight * (1. + weight_margin))
            w_down = str(max(0, weight * (1. - weight_margin)))
            q += " WHERE " + jcode_table + ".weight BETWEEN " + w_down
            q += " AND " + w_up
        t_before = time.time()
        res = conn.execute(q)
        #for tidid in res.fetchall():
        #    table_tidid_rot[tidid[0], rotation] += 1
        tidids = map(lambda x: x[0], res.fetchall())
        table_tidid_rot[tidids,[rotation]*len(tidids)] += 1
        conn.commit()
        t_core_query += time.time() - t_before
    if verbose > 0:
        t3 = time.time()
        print 'Jumps / weights with TID selected in %f seconds.' % (t3 - t2)
        if verbose > 0:
            print 'Time spend on core queries: %d seconds.' % t_core_query
        sys.stdout.flush()
    # count the number of tid per rotation
    max_per_tidid = np.max(table_tidid_rot,axis=1)
    if verbose > 0:
        print 'Best tidid has a max cnt of = ', np.max(max_per_tidid)
    tidid_ordered = np.argsort(max_per_tidid)[-1::-1]
    tidid_ordered = tidid_ordered[:np.where(max_per_tidid[tidid_ordered]==0)[0][0]]
    # get back tids
    tids = _ALL_TIDS[tidid_ordered]
    # done
    return tids
    

def die_with_usage():
    """ HELP MENU """
    print 'cover_hash_table.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print ''
    print 'This should be mostly used as a library, but you can'
    print 'launch some debugging code using:'
    print '   python cover_hash_table.py [FLAGS] <datadir> <coverlist> <tmp_db>'
    print 'FLAGS'
    print '  -fulldata    load every file in datadir'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # debugging
    print 'DEBUGGING!'

    # flags
    fulldata = False
    while True:
        if sys.argv[1] == '-fulldata':
            fulldata = True
        else:
            break
        sys.argv.pop(1)

    # params
    maindir = sys.argv[1]
    coverlistf = sys.argv[2]
    tmp_db = sys.argv[3]

    # sanity checks
    if not os.path.isdir(maindir):
        print 'ERROR: %s is not a directory.' % maindir
        sys.exit(0)
    if not os.path.isfile(coverlistf):
        print 'ERROR: %s does not exist.' % coverlistf
        sys.exit(0)
    use_existing_db = False
    if os.path.isfile(tmp_db):
        print 'CAREFUL: we use existing db: %s' % tmp_db
        time.sleep(5)
        use_existing_db = True

    # import hash code
    try:
        import beat_aligned_feats as BAF
        import cover_hash as CH
        import fingerprint_hash as FH
        import plot_covers as PC
        import quick_query_test as QQT
    except ImportError:
        print 'missing packages for debugging.'
        print 'Should not be needed!'

    # try to get data in as fast as possible
    clique_tid, clique_name = PC.read_cover_list(coverlistf)

    def get_jumps1(btchroma):
        """
        Use fingerprinting hash
        """
        landmarks = FH.get_landmarks(btchroma, decay=DECAY, max_per_frame=MAX_PER_FRAME)
        jumps = FH.get_jumps(landmarks, win=WIN)
        # done
        return jumps

    # load everything!
    if fulldata:
        all_h5_files = CH.get_all_files(maindir)
        all_tids = map(lambda x: os.path.split(os.path.splitext(x)[0])[1], all_h5_files)
    else:
        all_tids = []
        for ts in clique_tid.values():
            all_tids.extend(ts)
    print 'GOAL: add %d tids in the db' % len(all_tids)

    # open connection, init
    conn = sqlite3.connect(tmp_db)
    # pragma magic
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA page_size = 4096;')
    conn.execute('PRAGMA cache_size = 500000;') # page_size=4096, 500000 -> 2GB
    conn.execute('PRAGMA journal_mode = OFF;') # no ROLLBACK!
    print 'We added PRAGMA magic'
    # initialize tables
    if not use_existing_db:
        print 'initalizing...'
        init_db(conn)
        print 'DB initialized'
        sys.stdout.flush()

    
    # for each clique, add jumps
    cnt_tid_added = 0
    for tid in all_tids:
        # the db is already full?
        if use_existing_db:
            break
        # get paths
        filepath = PC.path_from_tid(maindir,tid)
        # get btchromas
        #btchromas = map(lambda p: BAF.get_btchromas(p), filepaths)
        btchroma = QQT.get_cpressed_btchroma(filepath, compression=COMPRESSION)
        # add jumps
        if btchroma is None:
            continue
        # get jumps
        jumps = get_jumps1(btchroma)
        cjumps = FH.get_composed_jumps(jumps, levels=LEVELS, win=WIN)
        # add them
        jumpcodes = map(lambda cj: FH.get_jumpcode_from_composed_jump(cj, maxwin=WIN), cjumps)
        add_jumpcodes(conn, tid, jumpcodes, normalize=NORMALIZE, commit=False)
        cnt_tid_added += 1
        # commit
        #if cnt_tid_added == 10:
        #    reindex(conn)
        if cnt_tid_added % 1000 == 0:
            conn.commit()
        # debug
        if cnt_tid_added % 500 == 0:
            print 'We added %d tid in the hash table(s).' % cnt_tid_added

        # DEBUG!!!!!!!
        #if cnt_tid_added > 500:
        #    print 'DEBUG!!!! we stop adding'
        #    break

    # commit
    print 'done, added %d tids, we commit...' % cnt_tid_added
    conn.commit()
    print 'done'

    # index
    if not use_existing_db:
        reindex(conn)

    # verbose / debugging
    q = "SELECT cnt FROM num_hash_tables LIMIT 1"
    res = conn.execute(q)
    num_tables = res.fetchone()[0]
    print 'We got %d hash tables' % num_tables
    count_entries = 0
    for tablecnt in range(1, num_tables + 1):
        table_name = 'hashes' + str(tablecnt)
        q = "SELECT Count(tidid) FROM " + table_name
        res = conn.execute(q)
        count_entries += res.fetchone()[0]
    print 'We got a total of %d entries in table: hashes' % count_entries
    q = "SELECT Count(tid) FROM tids"
    res = conn.execute(q)
    print 'We got a total of %d unique tid in table: tids' % res.fetchone()[0]

    # we launch testing!
    total_tids = sum(map(lambda x: len(x), clique_tid.values()))
    res_pos = 0.
    n_queries = 0
    cnt_not_matched = 0
    print 'we got %d total tids from train file.' % total_tids
    for cliqueid, tids in clique_tid.items():
        for tid in tids:
            # get closest match!
            jumps = None; weights = None
            matches = np.array(select_matches(conn, jumps, weights,
                                              weight_margin=WEIGHT_MARGIN, from_tid=tid))
            if len(matches) == 0:
                print 'no matches for tid:',tid
                continue
            # check for known covers
            for tid2 in tids:
                if tid2 == tid:
                    continue
                try:
                    pos = np.where(matches==tid2)[0][0]
                except IndexError:
                    pos = int(len(matches) + (total_tids - len(matches)) * .5)
                    cnt_not_matched += 1
                if pos < 5:
                    print '!!! amazing result for %s and %s! (pos=%d)' % (tid, tid2, pos)
                n_queries += 1
                res_pos += pos
                # verbose
                if n_queries % 500 == 0:
                    print 'After %d queries / %d cliques, we got an average pos of: %f/%d' % (n_queries,
                                                                                              cliqueid,
                                                                                              res_pos * 1. / n_queries,
                                                                                              total_tids)
                    print '(for %d queries the right answer was not a candidate)' % cnt_not_matched
    # close connection
    conn.close()
