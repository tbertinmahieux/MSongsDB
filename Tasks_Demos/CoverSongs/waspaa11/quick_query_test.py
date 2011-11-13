"""
This performs a quick sanity check, e.g. compares covers with randomly
selected songs, and tells which one is closer!

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
import sqlite3
import numpy as np

# hack to get btchromas
try:
    import beat_aligned_feats as BAF
    import cover_hash_table as CHT
    import fingerprint_hash as FH
except ImportError:
    print "Missed some import, might cause problems..."
    
RANDOMSEED = hash('caitlin')
# params
NUM_EXPS = 524
DECAY = .995
WIN = 3
NORMALIZE = True
WEIGHT_MARGIN = .60
MAX_PER_FRAME = 3
COMPRESSION = [2] #(1,2,3,4,8)
LEVELS = [3] # composed jumps, 1 means first order jumps

# BEST (SLOW!) 500 -> .798
#DECAY = 0.96
#WIN = 6
#NORMALIZE = 1
#WEIGHT_MARGIN = 0.50
#MAX_PER_FRAME = 2
#COMPRESSION = [1]
#LEVELS = [1, 4]


def get_cpressed_btchroma(path, compression=1):
    """ to easily play with the btchromas we get """
    # MAIN FUNCTION WITH COMPRESSION / STRETCH
    add_loudness = False
    h5 = BAF.GETTERS.open_h5_file_read(path)
    chromas = BAF.GETTERS.get_segments_pitches(h5)
    segstarts = BAF.GETTERS.get_segments_start(h5)
    if compression >= 1:
        btstarts = BAF.GETTERS.get_beats_start(h5)[::compression]
    elif compression == .5:
        btstarts = BAF.GETTERS.get_beats_start(h5)
        interpvals = np.interp(range(1,len(btstarts)*2-1,2),
                               range(0,len(btstarts)*2,2), btstarts)
        btstarts = np.array(zip(btstarts,interpvals)).flatten()
    else:
        print 'COMPRESSION OF %d NOT IMPLEMENTED YET' % compression
        raise NotImplementedError
    if add_loudness: # loudness specific stuff
        btloudmax = BAF.get_btloudnessmax(h5)
        loudnessmax = BAF.GETTERS.get_segments_loudness_max(h5)
    duration = BAF.GETTERS.get_duration(h5)
    h5.close()
    segstarts = np.array(segstarts).flatten()
    btstarts = np.array(btstarts).flatten()
    # add back loudness and aligning
    chromas = chromas.T
    if add_loudness:
        chromas = (chromas) * BAF.idB(loudnessmax)
        #pass
    btchroma = BAF.align_feats(chromas, segstarts, btstarts, duration)
    if btchroma is None:
        return None
    # can we do something with these?
    if add_loudness:
        #btchroma = btchroma * btloudmax
        # normalize
        btchroma = BAF.dB(btchroma+1e-10)
        btchroma -= btchroma.min()
        #assert not np.isnan(btchroma).any()
        btchroma /= btchroma.max()
        #btchroma = renorm_chroma(btchroma) # EXPERIMENTAL
        # still not correct!
    # Renormalize. Each column max is 1.
    if not add_loudness:
        maxs = btchroma.max(axis=0)
        maxs[np.where(maxs == 0)] = 1.
        btchroma = (btchroma / maxs)
    return btchroma
        

def renorm_chroma(chroma):
    """
    Weird method to put all chroma values between 0 and 1 where
    the max of each column gets 1, the second 1-1/11, ... the last 0
    """
    t1 = time.time()
    assert chroma.shape[0] == 12
    s = np.argsort(chroma, axis=0)
    #chroma = 1. - 1./s  # we create inf, we could do something faster
    #chroma[np.isinf(chroma)] = 1.
    chroma = 1. - 1./(s+1.)
    return chroma


def path_from_tid(maindir, tid):
    """
    Returns a full path based on a main directory and a track id
    """
    p = os.path.join(maindir, tid[2])
    p = os.path.join(p, tid[3])
    p = os.path.join(p, tid[4])
    p = os.path.join(p, tid.upper() + '.h5')
    return p


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


def get_jumps(btchroma, verbose=0):
    """
    Use fingerprinting hash
    """
    landmarks = FH.get_landmarks(btchroma, decay=DECAY, max_per_frame=MAX_PER_FRAME, verbose=verbose)
    jumps = FH.get_jumps(landmarks, win=WIN)
    return jumps


def one_exp(maindir, clique_tid, verbose=0):
    """
    performs one experiment:
      - select two covers
      - select random song
      - computes hashes / jumps
      - return 1 if we return cover correctly, 0 otherwise
    """
    # select cliques
    cliques = sorted(clique_tid.keys())
    np.random.shuffle(cliques)
    cl = cliques[0]
    other_cl = cliques[1]
    # select tracks
    tids = sorted(clique_tid[cl])
    np.random.shuffle(tids)
    query = tids[0]
    good_ans = tids[1]
    len_other_tids = len(clique_tid[other_cl])
    bad_ans = clique_tid[other_cl][np.random.randint(len_other_tids)]
    # create hash table, init
    conn = sqlite3.connect(':memory:')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA journal_mode = OFF;')
    conn.execute('PRAGMA page_size = 4096;')
    conn.execute('PRAGMA cache_size = 250000;')
    CHT.init_db(conn)
    # verbose
    if verbose>0:
        t1 = time.time()
    # compression (still testing)
    for cid, compression in enumerate(COMPRESSION):
        # get btchromas
        query_path = path_from_tid(maindir, query)
        query_btc = get_cpressed_btchroma(query_path, compression=compression)
        good_ans_path = path_from_tid(maindir, good_ans)
        good_ans_btc = get_cpressed_btchroma(good_ans_path, compression=compression)
        bad_ans_path = path_from_tid(maindir, bad_ans)
        bad_ans_btc = get_cpressed_btchroma(bad_ans_path, compression=compression)
        if query_btc is None or good_ans_btc is None or bad_ans_btc is None:
            conn.close()
            return None
        # get hashes (jumps) for good / bad answer
        jumps = get_jumps(query_btc, verbose=verbose)
        cjumps = FH.get_composed_jumps(jumps, levels=LEVELS, win=WIN)
        jumpcodes = map(lambda cj: FH.get_jumpcode_from_composed_jump(cj, maxwin=WIN), cjumps)
        if len(jumpcodes) == 0:
            print 'query has no jumpcode!'
            conn.close()
            return None
        #assert cid == 0
        CHT.add_jumpcodes(conn, query, jumpcodes, normalize=NORMALIZE, commit=False)
        # debug
        if verbose > 0:
            res = conn.execute("SELECT Count(tidid) FROM hashes1")
            print 'query added %d jumps' % res.fetchone()[0]
        # good ans
        jumps = get_jumps(good_ans_btc)
        cjumps = FH.get_composed_jumps(jumps, levels=LEVELS, win=WIN, verbose=verbose)
        jumpcodes = map(lambda cj: FH.get_jumpcode_from_composed_jump(cj, maxwin=WIN), cjumps)
        CHT.add_jumpcodes(conn, good_ans, jumpcodes, normalize=NORMALIZE, commit=False)
        # bad ans
        jumps = get_jumps(bad_ans_btc)
        cjumps = FH.get_composed_jumps(jumps, levels=LEVELS, win=WIN)
        jumpcodes = map(lambda cj: FH.get_jumpcode_from_composed_jump(cj, maxwin=WIN), cjumps)
        CHT.add_jumpcodes(conn, bad_ans, jumpcodes, normalize=NORMALIZE, commit=False)
    conn.commit()
    # indices
    q = "CREATE INDEX tmp_idx1 ON hashes1 ('jumpcode', 'weight')"
    conn.execute(q)
    q = "CREATE INDEX tmp_idx2 ON hashes1 ('tidid')"
    conn.execute(q)
    conn.commit()
    # verbose
    if verbose > 0:
        print 'Extracted/added jumps and indexed the db in %f seconds.' % (time.time()-t1)
    # get query
    #q = "SELECT jumpcode, weight FROM hashes WHERE tid='" + query + "'"
    #res = conn.execute(q)
    #res = res.fetchall()
    #jumps = map(lambda x: x[0], res)
    #weights = map(lambda x: x[1], res)
    jumps = None; weights = None
    # do the actual query
    tids = CHT.select_matches(conn, jumps, weights,
                              weight_margin=WEIGHT_MARGIN,
                              from_tid=query,
                              verbose=verbose)
    #assert tids[0] == query
    assert len(tids) < 4
    for t in tids:
        assert t in (query, bad_ans, good_ans)
    tids = np.array(tids)
    tids = tids[np.where(tids!=query)]
    # close connection
    conn.close()
    # check result
    if len(tids) == 0:
        print '(no matches)'
        return 0
    if tids[0] == good_ans:
        if verbose > 0:
            print 'We got it right!'
        return 1
    assert tids[0] == bad_ans
    if verbose > 0:
        print 'We got it wrong :('
    # DONE
    return 0 # 0 = error


def die_with_usage():
    """ HELP MENU """
    print 'Performs a few quick experiments to easily compare hashing'
    print 'methods without a full experiment.'
    print 'USAGE:'
    print '     python quick_query_test.py <maindir> <coverlist> <OPT: comment>'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    maindir = sys.argv[1]
    coverlistf = sys.argv[2]

    # sanity checks
    if not os.path.isdir(maindir):
        print 'ERROR: %s does not exist.' % maindir
        sys.exit(0)
    if not os.path.isfile(coverlistf):
        print 'ERROR: %s does not exist.' % coverlistf
        sys.exit(0)
    
    # read cliques        
    clique_tid, clique_name = read_cover_list(coverlistf)

    # set random seed
    np.random.seed(RANDOMSEED)

    # params
    print '******************************'
    print 'PARAMS:'
    print 'DECAY = %f' % DECAY
    print 'WIN = %d' % WIN
    print 'NORMALIZE = %d' % NORMALIZE
    print 'WEIGHT_MARGIN = %f' % WEIGHT_MARGIN
    print 'MAX_PER_FRAME = %d' % MAX_PER_FRAME
    print 'COMPRESSION =', COMPRESSION
    print 'LEVELS =', LEVELS
    print '******************************'

    cnt = 0.
    cnt_exps = 0.
    for i_exp in range(NUM_EXPS):
        verbose = 0
        if (cnt_exps + 1) % 25 == 0:
            verbose = 1
        try:
            res = one_exp(maindir, clique_tid, verbose=verbose)
        except KeyboardInterrupt:
            break
        if res is None:
            continue
        assert res >= 0 and res <= 1
        cnt += res
        cnt_exps += 1.
        if (cnt_exps) % 50 == 0:
            print '***** Accuracy after %d tries: %f' % (cnt_exps,
                                                         cnt / cnt_exps)

    # params again
    print '******************************'
    print 'PARAMS:'
    print 'DECAY = %f' % DECAY
    print 'WIN = %d' % WIN
    print 'NORMALIZE = %d' % NORMALIZE
    print 'WEIGHT_MARGIN = %f' % WEIGHT_MARGIN
    print 'MAX_PER_FRAME = %d' % MAX_PER_FRAME
    print 'COMPRESSION =', COMPRESSION
    print 'LEVELS =', LEVELS
    if len(sys.argv) > 3:
        print 'comment:', sys.argv[3]
    print '******************************'
