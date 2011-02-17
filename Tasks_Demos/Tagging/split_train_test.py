"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to split the dataset of Echo Nest tags into train and test.
Since these tags are applied to artists, we split artists.
The split is reproducible as long as the seed does not change.
Assumes we have the SQLite database artist_term.db

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
import time
import glob
import warnings
import numpy as np
import sqlite3

# number of top terms we consider
NTERMS=300
# random seed, note that we actually use hash(RNDSEED) so it can be anything
RNDSEED='caitlin'


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'"+s.replace("'","''")+"'"

def check_constraint(term_freq,top_terms,top_terms_test_freq):
    """
    Check the constraint 12%-30% for the test set
    term_freq is the dictionnary of all term frequencies
    top_terms is the list of terms we care about (first 300?)
    top_terms_freq is an array of frequency of top terms in test set.
    RETURN
      True if constraint satisfied, False otherwise
    """
    return check_constraint_12pc(term_freq,top_terms,top_terms_test_freq) and check_constraint_30pc(term_freq,top_terms,top_terms_test_freq)

def check_constraint_12pc(term_freq,top_terms,top_terms_test_freq):
    """
    Check the constraint >12% for the test set
    term_freq is the dictionnary of all term frequencies
    top_terms is the list of terms we care about (first 300?)
    top_terms_freq is an array of frequency of top terms in test set.
    RETURN
      True if constraint satisfied, False otherwise
    """
    for tidx,t in enumerate(top_terms):
        totalf = term_freq[t]
        testf = top_terms_test_freq[tidx]
        if testf < totalf * .12:
            return False
    return True

def check_constraint_30pc(term_freq,top_terms,top_terms_test_freq):
    """
    Check the constraint <30% for the test set
    term_freq is the dictionnary of all term frequencies
    top_terms is the list of terms we care about (first 300?)
    top_terms_freq is an array of frequency of top terms in test set.
    RETURN
      True if constraint satisfied, False otherwise
    """
    for tidx,t in enumerate(top_terms):
        totalf = term_freq[t]
        testf = top_terms_test_freq[tidx]
        if testf > totalf * .30:
            return False
    return True


def get_terms_for_artist(conn,artistid):
    """
    Returns the list of terms for a given artist ID
    """
    q = "SELECT term FROM artist_term WHERE artist_id='"+artistid+"'"
    res = conn.execute(q)
    return map(lambda x: x[0],res.fetchall())

def get_random_artist_for_term(conn,term,avoid_artists=None):
    """
    Get a random artist that is tagged by a given term.
    If avoid_artists is a list, we exclude these artists.
    """
    q = "SELECT artist_id FROM artist_term WHERE term="+encode_string(term)
    res = conn.execute(q)
    all_artists = sorted( map(lambda x: x[0], res.fetchall()) )
    np.random.shuffle(all_artists)
    if avoid_artists is None:
        return all_artists[0]
    for a in all_artists:
        if not a in subset_artists:
            return a
    raise IndexError('Found no artist for term: '+term+' that is not in the avoid list')


def die_with_usage():
    """ HELP MENU """
    print 'split_train_test.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print 'GOAL'
    print '  split the list of artists into train and test based on terms (Echo Nest tags).'
    print 'USAGE'
    print '  python split_train_test.py <artist_term.db> <train.txt> <test.txt> <top_terms.txt> <subset_tmdb>'
    print 'PARAMS'
    print '  artist_term.db    - SQLite database containing terms per artist'
    print '       train.txt    - list of Echo Nest artist ID'
    print '        test.txt    - list of Echo Nest artist ID'
    print '   top_terms.txt    - list of top terms (top 300)'
    print '     subset_tmdb    - track_metadata for the subset, to be sure all subset artists are in train'
    print ''
    print 'With the current settings, we get 4643 out of 44745 artists in the test set, corresponding to 122125 test tracks.'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 6:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output_train = sys.argv[2]
    output_test = sys.argv[3]
    output_top_terms = sys.argv[4]
    subset_tmdb = sys.argv[5]

    # sanity checks
    if not os.path.isfile(dbfile):
        print 'ERROR: database not found:',dbfile
        sys.exit(0)
    if os.path.exists(output_train):
        print 'ERROR:',output_train,'already exists! delete or provide a new name'
        sys.exit(0)
    if os.path.exists(output_test):
        print 'ERROR:',output_test,'already exists! delete or provide a new name'
        sys.exit(0)
    if os.path.exists(output_top_terms):
        print 'ERROR:',output_top_terms,'already exists! delete or provide a new name'
        sys.exit(0)
    if not os.path.exists(subset_tmdb):
        print 'ERROR:',subset_tmdb,'does not exist.'
        sys.exit(0)

    # open connection
    conn = sqlite3.connect(dbfile)

    # get all artists
    q = "SELECT artist_id FROM artists ORDER BY artist_id"
    res = conn.execute(q)
    allartists = map(lambda x: x[0],res.fetchall())
    print 'found',len(allartists),'distinct artists.'

    # get subset artists
    conn_subtmdb = sqlite3.connect(subset_tmdb)
    res = conn_subtmdb.execute('SELECT DISTINCT artist_id FROM songs')
    subset_artists = map(lambda x: x[0], res.fetchall())
    conn_subtmdb.close()
    print 'found',len(subset_artists),'distinct subset artists.'

    # get all terms
    q = "SELECT DISTINCT term FROM terms ORDER BY term" # DISTINCT useless
    res = conn.execute(q)
    allterms = map(lambda x: x[0],res.fetchall())
    print 'found',len(allterms),'distinct terms.'

    # get frequency
    term_freq = {}
    for t in allterms:
        term_freq[t] = 0
    q = "SELECT term FROM artist_term"
    res = conn.execute(q)
    allterms_nonunique = map(lambda x: x[0],res.fetchall())
    for t in allterms_nonunique:
        term_freq[t] += 1
    ordered_terms = sorted(term_freq, key=term_freq.__getitem__, reverse=True)
    print 'most used terms:',map(lambda x:x.encode('utf-8'), ordered_terms[:5])

    # try plotting
    try:
        warnings.simplefilter("ignore")
        import pylab as P
        P.figure()
        P.plot(map(lambda t: term_freq[t],ordered_terms[:500]))
        P.title('Frequencies of the 500 most used terms')
        P.show(False)
    except ImportError:
        print 'can not plot term frequencies, no pylab?'

    # print basic stats
    print 'term pos\tterm\t\tfrequency'
    print '0\t\t'+ordered_terms[0].encode('utf-8')+'\t\t',term_freq[ordered_terms[0]]
    print '50\t\t'+ordered_terms[50].encode('utf-8')+'\t',term_freq[ordered_terms[50]]
    print '100\t\t'+ordered_terms[100].encode('utf-8')+'\t\t',term_freq[ordered_terms[100]]
    print '200\t\t'+ordered_terms[200].encode('utf-8')+'\t\t',term_freq[ordered_terms[200]]
    print '300\t\t'+ordered_terms[300].encode('utf-8')+'\t\t',term_freq[ordered_terms[300]]
    print '500\t\t'+ordered_terms[500].encode('utf-8')+'\t',term_freq[ordered_terms[500]]

    # give info
    print '*************** METHOD *****************************'
    print 'We cut according to the top 300 terms.'
    print 'We select artists at random, but we make sure that'
    print 'that the test set contains between 12% and 30% of'
    print 'the artists for each of these 300 terms.'
    print 'We stop when that constraint is satisfied.'
    print '****************************************************'

    # top 300 terms
    topterms = np.array( ordered_terms[:NTERMS] )
    test_artists = set()
    test_term_freq = np.zeros(NTERMS)

    # set random seed
    np.random.seed(hash(RNDSEED))

    # heuristic: start filling from 300th and hope it works...
    term_id = NTERMS-1
    while term_id >= 0:
        #print 'term_id =',term_id
        #print '# test artists =',len(test_artists)
        term = topterms[term_id]
        artist = get_random_artist_for_term(conn,term,subset_artists)
        if artist in test_artists:
            continue
        test_artists.add(artist)
        terms = get_terms_for_artist(conn,artist)
        for t in terms:
            pos_t = np.where(topterms==t)[0]
            if len(pos_t)==0: continue
            test_term_freq[pos_t[0]] += 1
        # we check constraint 30%, if False, problem
        res = check_constraint_30pc(term_freq,topterms[term_id:],test_term_freq[term_id:])
        if not res:
            print 'we failed, term_id =',term_id,', term =',term
            break
        # we check constraint 12%, if true, decrement
        res = check_constraint_12pc(term_freq,topterms[term_id:],test_term_freq[term_id:])
        if res:
            term_id -= 1

    # close connection
    conn.close()

    # did we make it?
    good = check_constraint(term_freq,topterms,test_term_freq)
    if not good:
        print 'we did not make it'
        sys.exit(0)
    else:
        print 'IT WORKED, we have',len(test_artists),'/',len(allartists),'in the test set.'

    # we print to test file
    test_artists_list = sorted(list(test_artists))
    f = open(output_test,'w')
    for a in test_artists_list:
        f.write(a+'\n')
    f.close()

    # we print to train file
    train_artists = set()
    for a in allartists:
        if not a in test_artists:
            train_artists.add(a)
    assert len(train_artists) == len(allartists)-len(test_artists),'sanity check failed, check code'
    train_artists_list = sorted(list(train_artists))
    f = open(output_train,'w')
    for a in train_artists_list:
        f.write(a+'\n')
    f.close()

    # we print top terms
    f = open(output_top_terms,'w')
    for t in topterms:
        f.write(t.encode('utf-8')+'\n')
    f.close()

    # keep frequency plot open
    try:
        import pylab as P
        P.show(True)
    except ImportError:
        pass
