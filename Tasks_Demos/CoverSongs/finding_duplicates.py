#!/usr/bin/env python
"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code identifies duplicate songs in the database that
are 'easy to find', usually same artist and title or song id.

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
import time
import datetime
import sqlite3
import numpy as np


def create_cliques(data):
    """
    Always receive an array of arrays, each sub array has 3 elements:
        - artist (id or name)
        - song (id or title)
        - track id
    From that, create cluster (or clique) that have the first two
    elements in common. We asusme they are duplicates.
    We rely on the python hash() function, we assume no collisions.
    Returns a dictionary: int -> [tracks], int are arbitrary
    """
    cnt_clique = 0
    clique_tracks = {}
    for d1,d2,tid in data:
        hashval = hash(d1+d2)
        if hashval in clique_tracks.keys():
            clique_tracks[hashval].append(tid)
        else:
            clique_tracks[hashval] = [tid]
    return clique_tracks


def merge_cliques(clique1,clique2):
    """
    Merge two sets of cliques, return a new dictionary
    of clique. As always, dict keys are random.
    """
    # copy clique1 into new one
    new_clique = {}
    new_clique.update( zip( range(1,len(clique1)+1), clique1.values() ) )
    clique_id = len(clique1)
    # reverse index
    tid_clique = {}
    for clique,tids in new_clique.items():
        for tid in tids:
            tid_clique[tid] = clique
    # move on to second one
    for clique,tids in clique2.items():
        clique_ids = []
        for tid in tids:
            if tid in tid_clique.keys():
                c = tid_clique[tid]
                if not c in clique_ids:
                    clique_ids.append( c )
        # new clique
        if len(clique_ids) == 0:
            clique_id += 1
            new_clique[clique_id] = tids
        # easy, add to one clique
        elif len(clique_ids) == 1:
            cid = clique_ids[0]
            for tid in tids:
                if not tid in new_clique[cid]:
                    new_clique[cid].append( tid )
        # merge more than one clique
        else:
            # merge the clique
            cid = min(clique_ids)
            for c in clique_ids:
                if c != cid:
                    tids_to_move = new_clique[c]
                    for t in tids_to_move:
                        tid_clique[t] = cid
                    new_clique[cid].extend(tids_to_move)
                    new_clique.pop(c)
            # add to the clique cid
            for tid in tids:
                if not tid in new_clique[cid]:
                    new_clique[cid].append( tid )
    # done
    return new_clique



def die_with_usage():
    """ HELP MENU """
    print 'finding_duplicates.py'
    print '    by T. Bertin-Mahieux (2011) Columbia University'
    print '       tb2332@columbia.edu'
    print ''
    print 'This code identify a list of duplicate songs in the dataset.'
    print 'These duplicates are easy to find, in the sense that they have'
    print 'the same artist and title. WE DO NOT FIND ALL DUPLICATES!'
    print ''
    print 'USAGE'
    print '   python finding_duplicates.py <tmdb> <output>'
    print 'PARAMS'
    print '     tmdb   - track_metadata.py'
    print '   output   - text file with duplicates'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    tmdb = sys.argv[1]
    outputf = sys.argv[2]

    # sanity checks
    if not os.path.isfile(tmdb):
        print 'ERROR:',tmdb,'does not exist.'
        sys.exit(0)
    if os.path.isfile(outputf):
        print 'ERROR:',outputf,'already exists.'
        sys.exit(0)

    # open sqlite connection
    conn = sqlite3.connect(tmdb)
    
    # get same artist_name, same title
    t1 = time.time()
    q = "CREATE TEMP TABLE tmp_aname_title (aname TEXT, title TEXT, ntid INT)"
    conn.execute(q); conn.commit()
    q = "INSERT INTO tmp_aname_title SELECT artist_name, title, COUNT(track_id)"
    q += " FROM songs GROUP BY artist_name, title"
    conn.execute(q); conn.commit()
    q = "CREATE INDEX idx_tmp_aname_title ON tmp_aname_title ('ntid','aname','title')"
    conn.execute(q); conn.commit()
    q = "SELECT artist_name,songs.title,songs.track_id FROM songs"
    q += " JOIN tmp_aname_title ON aname=artist_name AND songs.title=tmp_aname_title.title"
    q += " WHERE tmp_aname_title.ntid>1"
    res = conn.execute(q)
    data = res.fetchall()
    # get cliques
    cliques1 = create_cliques(data)
    t2 = time.time()
    print '********************************************************'
    print 'Found duplicates artist name / title in',str(datetime.timedelta(seconds=t2-t1))
    print 'We got',sum(map(lambda tids: len(tids), cliques1.values())),'tracks in',len(cliques1),'cliques.'

    # get same artist id, same title
    t1 = time.time()
    q = "CREATE TEMP TABLE tmp_aid_title (aid TEXT, title TEXT, ntid INT)"
    conn.execute(q); conn.commit()
    q = "INSERT INTO tmp_aid_title SELECT artist_id, title, COUNT(track_id)"
    q += " FROM songs GROUP BY artist_id, title"
    conn.execute(q); conn.commit()
    q = "CREATE INDEX idx_tmp_aid_title ON tmp_aid_title ('ntid','aid','title')"
    conn.execute(q); conn.commit()
    q = "SELECT artist_id,songs.title,songs.track_id FROM songs"
    q += " JOIN tmp_aid_title ON aid=artist_id AND songs.title=tmp_aid_title.title"
    q += " WHERE tmp_aid_title.ntid>1"
    res = conn.execute(q)
    data = res.fetchall()
    # get cliques
    cliques2 = create_cliques(data)
    t2 = time.time()
    print '********************************************************'
    print 'Found duplicates artist id / title in',str(datetime.timedelta(seconds=t2-t1))
    print 'We got',sum(map(lambda tids: len(tids), cliques2.values())),'tracks in',len(cliques2),'cliques.'
    final_cliques = merge_cliques(cliques1,cliques2)
    print 'After merge, got',sum(map(lambda tids: len(tids), final_cliques.values())),'tracks in',len(final_cliques),'cliques.'

    # get same artist name, same song id
    t1 = time.time()
    q = "CREATE TEMP TABLE tmp_aname_sid (aname TEXT, sid TEXT, ntid INT)"
    conn.execute(q); conn.commit()
    q = "INSERT INTO tmp_aname_sid SELECT artist_name, song_id, COUNT(track_id)"
    q += " FROM songs GROUP BY artist_name, song_id"
    conn.execute(q); conn.commit()
    q = "CREATE INDEX idx_tmp_aname_sid ON tmp_aname_sid ('ntid','aname','sid')"
    conn.execute(q); conn.commit()
    q = "SELECT artist_name,songs.song_id,songs.track_id FROM songs"
    q += " JOIN tmp_aname_sid ON aname=artist_name AND songs.song_id=tmp_aname_sid.sid"
    q += " WHERE tmp_aname_sid.ntid>1"
    res = conn.execute(q)
    data = res.fetchall()
    # get cliques
    cliques3 = create_cliques(data)
    t2 = time.time()
    print '********************************************************'
    print 'Found duplicates artist name / song id in',str(datetime.timedelta(seconds=t2-t1))
    print 'We got',sum(map(lambda tids: len(tids), cliques3.values())),'tracks in',len(cliques3),'cliques.'
    final_cliques = merge_cliques(final_cliques,cliques3)
    print 'After merge, got',sum(map(lambda tids: len(tids), final_cliques.values())),'tracks in',len(final_cliques),'cliques.'

    # get same artist id, same song id
    t1 = time.time()
    q = "CREATE TEMP TABLE tmp_aid_sid (aid TEXT, sid TEXT, ntid INT)"
    conn.execute(q); conn.commit()
    q = "INSERT INTO tmp_aid_sid SELECT artist_id, song_id, COUNT(track_id)"
    q += " FROM songs GROUP BY artist_id, song_id"
    conn.execute(q); conn.commit()
    q = "CREATE INDEX idx_tmp_aid_sid ON tmp_aid_sid ('ntid','aid','sid')"
    conn.execute(q); conn.commit()
    q = "SELECT artist_id,songs.song_id,songs.track_id FROM songs"
    q += " JOIN tmp_aid_sid ON aid=artist_id AND songs.song_id=tmp_aid_sid.sid"
    q += " WHERE tmp_aid_sid.ntid>1"
    res = conn.execute(q)
    data = res.fetchall()
    # get cliques
    cliques4 = create_cliques(data)
    t2 = time.time()
    print '********************************************************'
    print 'Found duplicates artist id / song id in',str(datetime.timedelta(seconds=t2-t1))
    print 'We got',sum(map(lambda tids: len(tids), cliques4.values())),'tracks in',len(cliques4),'cliques.'
    final_cliques = merge_cliques(final_cliques,cliques4)
    print 'After merge, got',sum(map(lambda tids: len(tids), final_cliques.values())),'tracks in',len(final_cliques),'cliques.'


    # write output
    output = open(outputf,'w')
    output.write('# MILLION SONG DATASET - DUPLICATES\n')
    output.write('#    created by T. Bertin-Mahieux, Columbia University\n')
    output.write('#               tb2332@columbia.edu\n')
    output.write('#       on '+time.ctime()+'\n')
    output.write('# List of duplicates from artist names / artist id and\n')
    output.write('# titles / song id.\n')
    for clique,trackids in final_cliques.items():
        q = "SELECT artist_name,title FROM songs WHERE track_id='"+trackids[0]+"' LIMIT 1"
        res = conn.execute(q)
        aname,title = res.fetchone()
        output.write('%'+str(clique)+' '+aname.encode('utf-8')+' - '+title.encode('utf-8')+'\n')
        for tid in trackids:
            output.write(tid + '\n')
    output.close()

    # close connection
    conn.close()


    
