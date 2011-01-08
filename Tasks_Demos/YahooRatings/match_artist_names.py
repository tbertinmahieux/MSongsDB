"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code matches artist names with artists from the million
song dataset.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.

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
import copy
import datetime
import numpy as np
import sqlite3
try:
    import Levenshtein
except ImportError:
    print 'You need the code for Levenshtein edit distance:'
    print 'http://code.google.com/p/pylevenshtein/'
    sys.exit(0)

def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'"+s.replace("'","''")+"'"


def purge_yahoo_artists(yartists_dict,done_artists):
    """
    Takes a dictionnary 'modified name' -> 'original Yahoo name'
    and removes the ones that are done
    """
    for k in yartists_dict.keys():
        if yartists_dict[k] in done_artists:
            del yartists_dict[k]

def remove_small_chars(s):
    """
    Remove , . and similar things, includind spaces
    """
    s = s.replace(' ','')
    s = s.replace('.','')
    s = s.replace(',','')
    s = s.replace('"','')
    s = s.replace("'",'')
    s = s.replace('\\','')
    s = s.replace('?','')
    s = s.replace('%','')
    s = s.replace('#','')
    s = s.replace('/','')
    s = s.replace('*','')
    s = s.replace('&','')
    return s


def die_with_usage():
    """ HELP MENU """
    print 'match_artist_names.py'
    print '  by T. Bertin-Mahieux (2011) Columbia University'
    print '     tb2332@columbia.edu'
    print ''
    print 'This code try to find matches between artists in Yahoo Ratings'
    print 'and artists in the Million Song Dataset'
    print ''
    print 'USAGE:'
    print '  python match_artist_names.py <track_metadata.db> <yahoo_artists.txt> <output.txt> (OPT: unmatched.txt)'
    print 'PARAMS:'
    print '  track_metadata.db   - SQLite database with all the Million Song Dataset tracks'
    print "  yahoo_artists.txt   - file 'ydata-ymusic-artist-names-v1_0.txt' in Yahoo dataset R1"
    print '             output   - text file with result: yahoo name, Echo Nest name, Echo Nest ID'
    print '      unmatched.txt   - list artists that were not matched'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # flags
    startfile = ''
    startstep = 0
    while True:
        if sys.argv[1] == '-startf':
            startfile = sys.argv[2]
            sys.argv.pop(1)
        elif sys.argv[1] == '-startstep':
            startstep = int(sys.argv[2])
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # params
    dbfile = sys.argv[1]
    yahoofile = sys.argv[2]
    output = sys.argv[3]
    out_unmatched = ''
    if len(sys.argv) >= 5:
        out_unmatched = sys.argv[4]

    # sanity checks
    if not os.path.isfile(dbfile):
        print 'ERROR: file',dbfile,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(yahoofile):
        print 'ERROR: file',yahoofile,'does not exist.'
        sys.exit(0)
    if os.path.isfile(output):
        print 'ERROR: file',output,'exists, delete or provide a new one.'
        sys.exit(0)
    if out_unmatched != '' and os.path.isfile(out_unmatched):
        print 'ERROR: file',out_unmatched,'exists, delete or provide a new one.'
        sys.exit(0)

    # read yahoo data
    f = open(yahoofile,'r')
    lines = f.readlines()
    f.close()
    yartists = map(lambda l: l.strip().split('\t')[1],lines)

    # remove 'Not Applicable' and 'Unknown Artist'
    if yartists[0] == 'Not Applicable' and yartists[1] == 'Unknown Artist':
        yartists = yartists[2:]

    print 'Found',len(yartists),'Yahoo artists:',yartists[:3],'...'
    nya = len(yartists)

    # get artist names from the Million Song Dataset
    t1 = time.time()
    q = "SELECT DISTINCT artist_name,artist_id FROM songs"
    conn = sqlite3.connect(dbfile)
    res = conn.execute(q)
    msd_artists = res.fetchall()
    conn.close()
    stimelength = str(datetime.timedelta(seconds=time.time()-t1))
    print 'Found',len(msd_artists),'artists from the Million Song Dataset in',stimelength

    # dict of name -> Echo Nest ID, names are all lower case
    name_enid = {}
    for p in msd_artists:
        name_enid[p[0].lower().encode('utf-8')] = p[1]

    # set of yahoo artists
    yartists_dict = {}
    for a in yartists:
        yartists_dict[a.lower()] = a

    # dictionary of done artists
    done_artists = {}

    # start file?
    if startfile != '':
        f = open(startfile,'r')
        lines = f.readlines()
        done_data = map(lambda x: x.strip().split('<SEP>'),lines)
        for dd in done_data:
            done_artists[dd[0]] = [dd[1],dd[2]]
        f.close()
        purge_yahoo_artists(yartists_dict, done_artists.keys())
        print 'Found',len(done_data),'done artists from the start file.'

    # exact matches
    print '************* EXACT MATCHES ********************'
    if startstep <= 1:
        cnt_exact = 0
        t1 = time.time()
        ya_set = yartists_dict.keys()
        msda_set = name_enid.keys()
        for ya in ya_set:
            if ya in msda_set:
                done_artists[ yartists_dict[ya] ] = [name_enid[ya],ya]
                cnt_exact += 1
                del yartists_dict[ya]
        stimelength = str(datetime.timedelta(seconds=time.time()-t1))
        print 'found',cnt_exact,'exact matches in',stimelength            

    # remove little characters . ' " % and spaces
    print '************* REMOVE SPACES AND SMALL CHAR *****'
    if startstep <= 2:
        purge_yahoo_artists(yartists_dict, done_artists.keys())
        cnt_smallchar = 0
        lower_ya = copy.deepcopy(yartists_dict.keys())
        for a in lower_ya:
            yartists_dict[ remove_small_chars(a) ] = yartists_dict[a]
        lower_msda = copy.deepcopy(name_enid.keys())
        for a in lower_msda:
            name_enid[ remove_small_chars(a) ] = name_enid[a]
        t1 = time.time()
        for ya in yartists_dict.keys():
            if ya in name_enid.keys():
                done_artists[ yartists_dict[ya] ] = [name_enid[ya],ya]
                cnt_smallchar += 1
                del yartists_dict[ya]
        stimelength = str(datetime.timedelta(seconds=time.time()-t1))
        print 'found',cnt_smallchar,'exact matches in',stimelength            
        

    # write matches
    f = open(output,'a')
    for ya in done_artists.keys():
        f.write(ya+'<SEP>'+done_artists[ya][0]+'<SEP>')
        f.write(done_artists[ya][1]+'\n')
    f.close()

    
    # print unmatched
    if out_unmatched != '':
        purge_yahoo_artists(yartists_dict, done_artists.keys())
        unique_a = set()
        for a in yartists_dict.values():
            unique_a.add( a )
        f = open(out_unmatched,'w')
        for a in unique_a:
            f.write(a+'\n')
        f.close()
