"""
Code to create fingerprints out of a chroma matrix.

Code inspired by D. Ellis fingerprinting MATLAB code

For chroma, we probably simply have a decay factor,
and no 'local pitch' decay (unlike a freq band)

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
import sqlite3
import numpy as np
import cover_hash_table as CHT



def landmarks_pass(btchroma, decay, max_per_frame):
    """
    Performs a forward pass to find landmarks
    PARAMS
       btchroma       - we know what this is
       decay          - same as get_landmarks
       max_per_frame  - how many landmarks we allow in 1 col
    RETURN
       binary matrix, same size as btchroma, with ones
       for landmarks
    """
    # find number of beats
    nbeats = btchroma.shape[1]
    # return matrix
    landmarks = np.zeros(btchroma.shape, dtype='int')
    # initiate threshold, there's probably better than that
    #sthresh = btchroma[:,:10].max()
    sthresh = btchroma[:,:10].max(axis=1) # one threshold per pitch
    # iterate over beats
    # FORWARD PASS
    for b in range(nbeats):
        s_this = btchroma[:,b]
        sdiff = s_this - sthresh
        sdiff[sdiff<0] = 0.
        # sort
        peak_order = np.argsort(sdiff)[-1::-1][:max_per_frame]
        # iterate over max peaks
        for pidx, p in enumerate(peak_order):
            if s_this[p] > sthresh[p]:
                # debug
                landmarks[p, b] = 1
                # this following part is not understood
                #eww = np.square(np.exp(-0.5 * p / 1.));
                #sthresh = max(sthresh, s_this[p] * eww);
                sthresh[p] = s_this[p]
                if pidx == 0:
                    sthresh[sthresh<s_this[p] * decay] = s_this[p] * decay
        # decay sthresh
        sthresh *= decay
    # done
    return landmarks


def get_landmarks(btchroma, decay, max_per_frame=3, verbose=0):
    """
    Returns a set of landmarks extracted from btchroma.
    """
    if verbose > 0:
        t1 = time.time()
    # forward pass
    landmarks_fwd = landmarks_pass(btchroma, decay=decay, max_per_frame=max_per_frame)
    # backward pass
    landmarks_bwd = landmarks_pass(btchroma[:,-1::-1],
                                   decay=decay, max_per_frame=max_per_frame)[:,-1::-1]
    # merge landmarks
    landmarks_fwd *= landmarks_bwd
    # verbose
    if verbose > 0:
        print 'Landmarks (fwd & bwd) computed in %f seconds.' % (time.time() - t1)
    # done?
    return landmarks_fwd


def get_jumps(landmarks, win=12):
    """
    Receives a binary matrix containing landmarks.
    Computes pairs over a window of size 'win'
    ONLY ONE MAX PER COL IS ALOUD
    ONLY JUMPS BETWEEN TWO POINTS ARE CONSIDERED
    RETURN
       list of [tdiff, pdiff, toffset, poffset]
    """
    assert landmarks.shape[0] == 12, 'What?'
    nbeats = landmarks.shape[1]
    # jumps
    jumps = []
    # get all the positive points in a dict
    # faster if there are few landmarks
    lmks_d = {}
    tmp = np.where(landmarks==1)
    for i in range(len(tmp[0])):
        if tmp[1][i] in lmks_d:
            lmks_d[tmp[1][i]].append(tmp[0][i])
        else:
            lmks_d[tmp[1][i]] = [tmp[0][i]]
    #lmks_d.update(zip(tmp[1],tmp[0]))
    #assert len(lmks_d) == len(tmp[0]),'more than one max per col'
    # iterate over beats (until -win, faster than -1, does not change much)
    for b in range(nbeats-win):
        b_lmks = lmks_d.get(b, [])
        if len(b_lmks) == 0:
            continue
        for w in range(b,b+win):
            w_lmks = lmks_d.get(w, [])
            if len(w_lmks) == 0:
                continue
            for b_lmk in b_lmks:
                for w_lmk in w_lmks:
                    if w == b and b_lmk >= w_lmk:
                        continue
                    # tdiff = w-b
                    # toffset = b
                    # poffset = b_lmks
                    pdiff = (w_lmk - b_lmk + 12) % 12
                    jumps.append([w-b, pdiff, b, b_lmk])
    # done
    return jumps

# COMPOSED JUMPS *********************************************


def get_jumpcode_from_composed_jump(jump, maxwin=15, slowdebug=False):
    """
    Compute a jumpcode from a set of jumps
    The jump here is the output of 'get_composed_jumps(...)'
    It's a list of (t,p,t,p,t,p...), eventually with a -1 value at the end
    """
    nlmks = int(len(jump) / 2)
    assert nlmks > 1
    maxcode = 12 * 12 * (maxwin + 1) # max code for a level 1 jump (2 lmks)
    finalcode = 0
    # add each jump, with a power of maxcode
    for j in range(0, nlmks * 2 - 2, 2):
        tdiff = jump[j+2] - jump[j]
        assert tdiff >= 0
        poffset = jump[j+1]
        pdiff = (jump[j+3] - jump[j+1] + 12) % 12
        jcode = get_jump_code(tdiff, pdiff, poffset)
        jcode_norot = jcode - (jcode % 12)
        if j == 0:
            first_rot = jcode - jcode_norot
        finalcode += jcode_norot * np.power(maxcode, j/2)
    # add first rotation
    finalcode += first_rot
    #***********************************
    # MEGA TEST
    if slowdebug:
        rndoffset = np.random.randint(1,12)
        jump2 = list(copy.deepcopy(jump))
        for j in range(1, len(jump2), 2):
            jump2[j] = (jump2[j] + rndoffset) % 12
        finalcode2 = get_jumpcode_from_composed_jump(jump2, maxwin=maxwin, slowdebug=False)
        #print 'finalcode = %d and finalcode2 = %d' % (finalcode, finalcode2)
        assert finalcode2 - (finalcode2 % 12) == finalcode - (finalcode % 12)
    #***********************************
    # done! we think...
    return finalcode


def get_jump_code(tdiff, pdiff, poffset):
    """
    Encode a jump based on a time difference and a pitch difference.
    The encoding is the following:
      pdiff = (pdiff + 12) % 12
      code = tdiff * 12 + pdiff
    tdiff of zero are accepted!
    """
    pdiff = (pdiff + 12) % 12
    # sanity checks, should be removed for speed
    assert tdiff >= 0
    assert pdiff >= 0 and pdiff < 12
    assert poffset >= 0 and poffset < 12
    # return code
    return (tdiff * 12 * 12) + pdiff * 12 + poffset


def compose_jump_code(code1, code2):
    """
    We want to avoid collision, and rotation must still be done
    by %12 and adding rotation
    """
    code1_rot = code1 % 12
    code1_norot = code1 - code1_rot
    code2_norot = code2 - (code2 % 12)
    # combine code norot
    mult = 12 * np.power(10, max(int(np.log10(code1_norot)), int(np.log10(code2_norot))) + 1)
    code = code1_norot * 12 + code2_norot
    # add back rotation1
    code += code1_rot
    # sanity checks
    assert not np.isinf(code), 'oops, our encoding degenerated'
    assert code < sys.maxint, 'oops, our encoding degenerated'
    assert code > 0, 'oops, our encoding degenerated'
    # done
    return code


def add_nlmk2_jumps_to_db(conn, jumps, nocopy=False):
    """
    Get the output of 'get_jumps' and add it to a proper
    database that can be use to compose_jumps later
    """
    # create table
    q = "CREATE TEMP TABLE jumps_level1 (t0 INT, p0 INT, t1 INT, p1 INT, jumpcode INT)"
    conn.execute(q)
    # add jumps
    for tdiff, pdiff, t0, p0 in jumps:
        t1 = t0 + tdiff
        p1 = (p0 + pdiff) % 12
        q = "INSERT INTO jumps_level1 VALUES (" + str(t0) + ", " + str(p0)
        q += ", " + str(t1) + ", " + str(p1) + ", -1)"
        conn.execute(q)
    conn.commit()
    if nocopy:
        return
    # copy
    q = "CREATE TEMP TABLE jumps_level1_bis (t0 INT, p0 INT, t1 INT, p1 INT, jumpcode INT)"
    conn.execute(q)
    q = "INSERT INTO jumps_level1_bis SELECT * FROM jumps_level1"
    conn.execute(q)
    conn.commit()
    # INDEXING
    # (we only need t0/p0 since we add level1 jumps AFTER current jumps)
    # t1 is useful for checking win size
    q = "CREATE INDEX idx_level1_bis ON jumps_level1_bis ('t0', 'p0', 't1')"
    conn.execute(q)
    conn.commit()
    # DONE
    

def compose_jumps(conn, win, level=2, verbose=0):
    """
    Receives a database of jumps that have been composed up to
    the ('level'-1) level
    level1 means jumps between 2 landmarks, so we do at least level 2 here..
    Composed jumps have to have a maximum lenght of size 'win'
    """
    assert level >= 2
    # name of current (level under) table
    curr_table_name = "jumps_level" + str(level-1)
    # add indexing to the current table (end of jumps)
    q = "CREATE INDEX idx_level" + str(level-1)
    q += " ON " + curr_table_name
    q += "('t" + str(level-1) + "', 'p" + str(level-1) + "', 't0')"
    conn.execute(q)
    conn.commit()
    # create new table
    new_table_name = "jumps_level" + str(level)
    q = "CREATE TEMP TABLE " + new_table_name + " ("
    for n in range(level+1):
        q += "t" + str(n) + " INT, p" + str(n) + " INT,"
    q += " jumpcode INT)"
    if verbose > 0:
        print q
    conn.execute(q)
    # add proper new jumps to it, by adding a first level jump AFTER
    q = "INSERT INTO " + new_table_name + " SELECT "
    for n in range(level):
        q += curr_table_name + ".t" + str(n) + ", "
        q += curr_table_name + ".p" + str(n) + ", "
    q += "jumps_level1_bis.t1, jumps_level1_bis.p1, -1" # -1 is jumpcode for the moment
    q += " FROM " + curr_table_name + " JOIN jumps_level1_bis"
    q += " ON " + curr_table_name + ".t" + str(level-1) + "=jumps_level1_bis.t0"
    q += " AND " + curr_table_name + ".p" + str(level-1) + "=jumps_level1_bis.p0"
    q += " WHERE jumps_level1_bis.t1-" + curr_table_name + ".t0<=" + str(win)
    if verbose > 0 :
        print q
    conn.execute(q)
    conn.commit()
    # NEVER USEFUL TO ADD JUMP BEFORE, AFTER IS ENOUGH
    

def get_composed_jumps(jumps, levels, win, verbose=0):
    """
    Take the output of get_jumps (from landmarks)
    Compose the jumps, return them as an array of array.
    If intermediate=True, we return the jumps for intermediary levels,
    not just the requested one.
    We use a temporary sqlite3 connection to work.
    """
    assert len(levels) > 0
    maxlevel = max(levels)
    assert maxlevel >= 1, 'level 1 min, it means jumps between two landmarks'
    # verbose
    if verbose>0:
        t1 = time.time()
    # open temporary connection
    #      IT IS FAST!
    #      timeit.Timer("import sqlite3; conn = sqlite3.connect(':memory:'); conn.close()").timeit(10000)
    #      Out[35]: 0.49553799629211426
    conn = sqlite3.connect(':memory:')
    # special case: level = 1
    if maxlevel == 1:
        add_nlmk2_jumps_to_db(conn, jumps, nocopy=True)
        q = "SELECT * FROM jumps_level1"
        res = conn.execute(q)
        composed_jumps = res.fetchall()
        conn.close()
        if verbose > 0:
            print 'Composed jumps (max lvl = %d) obtained in %f seconds.' % (maxlevel, time.time() - t1)
        return composed_jumps
    # enters level1 jumps
    add_nlmk2_jumps_to_db(conn, jumps)
    # do upper levels
    for lvl in range(2, maxlevel+1):
        compose_jumps(conn, win, level=lvl)
    # what do we return?
    composed_jumps = []
    for lvl in levels:
        q = "SELECT * FROM jumps_level" + str(lvl)
        res = conn.execute(q)
        composed_jumps.extend(res.fetchall())
    # done
    conn.close()
    # verbose
    if verbose > 0:
        print 'Composed jumps (max lvl = %d) obtained in %f seconds.' % (maxlevel, time.time() - t1)
    return composed_jumps

# ************************************************************




def die_with_usage():
    """ HELP MENU """
    print 'fingerprint_hash.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print ''
    print 'This code should mostly be used as a library'
    print 'Creates landmarks similar to D. Ellis fingerprinting code.'
    print 'USAGE (debugging):'
    print '    python fingerprint_hash.py <hdf5 song file> <decay>'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # debugging
    print 'DEBUGGING'

    # params
    songfile = sys.argv[1]
    decay = .9
    if len(sys.argv) > 2:
        decay = float(sys.argv[2])

    # sanity checks
    if not os.path.isfile(songfile):
        print 'ERROR: %s does not exist.' % songfile
        sys.exit(0)

    # tbm path, import stuff
    import beat_aligned_feats as BAF
    import pylab as P
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)

    # get chroma
    btchroma = BAF.get_btchromas_loudness(songfile)
    btchroma_db = np.log10(BAF.get_btchromas_loudness(songfile)) * 20.
    btchroma_normal = BAF.get_btchromas(songfile)

    # get landmarks
    landmarks = get_landmarks(btchroma, decay=decay)
    landmarks_normal = get_landmarks(btchroma_normal, decay=decay)

    # plot
    pargs = {'aspect': 'auto',
             'cmap': P.cm.gray_r,
             'interpolation': 'nearest',
             'origin': 'lower'}
    P.subplot(4, 1, 1)
    P.imshow(btchroma, **pargs)
    P.subplot(4, 1, 2)
    P.imshow(landmarks_normal, **pargs)

    # plot landmarks
    P.subplot(4, 1, 3)
    P.imshow(btchroma, **pargs)
    #landmarksY, landmarksX = np.where(landmarks==1)
    landmarksY, landmarksX = np.where(landmarks_normal==1)
    for k in range(len(landmarksX)):
        x = landmarksX[k]
        y = landmarksY[k]
        P.scatter(x,y,s=12,c='r',marker='o')
    # plot groups
    P.subplot(4, 1, 4)

    # plot groups
    def my_groups(btchroma):
        #landmarks = get_landmarks(btchroma, decay=decay)
        jumps = get_jumps(landmarks_normal, win=12)
        unzip = lambda l:tuple(zip(*l)) # magic function!
        tdiff,pdiff,toff,poff = unzip(jumps)
        groups = [None] * len(tdiff)
        for i in range(len(tdiff)):
            x0 = toff[i]
            x1 = toff[i] + tdiff[i]
            y0 = poff[i]
            y1 = (poff[i] + pdiff[i]) % 12
            groups[i] = [[x0,y0], [x1,y1]]
        return groups

    import plot_covers as PC
    groups = my_groups(btchroma)
    PC.plot_landmarks(landmarks, None, None, groups=groups,
                      noshow=True, xlim=None)

    P.show(True)

    
