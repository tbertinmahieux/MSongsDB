"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code takes a list of Yahoo artists matched with
Echo Nest ID, and look at the ratings in the Yahoo Dataset R1
to see how many ratings are covered by these artists.

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
import numpy as np



def die_with_usage():
    """ HELP MENU """
    print 'count_ratings_known_artists.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print ''
    print 'Checks how many ratings from the Yahoo Dataset R1 we cover'
    print 'with known Echo Nest artist IDs'
    print ''
    print 'USAGE:'
    print '   python count_ratings_known_artists.py <y_artist_id> <a_map_file> <y_user_ratings>'
    print 'PARAMS:'
    print '     y_artist_id   - file "ydata-ymusic-artist-names-v1_0.txt" from Yahoo Dataset R1'
    print '      a_map_file   - artist mapping file, format: Yahoo Name<SEP>Echo Nest artist ID<SEP>...'
    print '  y_user_ratings   - file "ydata-ymusic-user-artist-ratings-v1_0.txt" from Yahoo Dataset R1'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # params
    y_artist_id = sys.argv[1]
    a_map_file = sys.argv[2]
    y_user_ratings = sys.argv[3]

    # sanity checks
    if not os.path.isfile(y_artist_id):
        print 'ERROR: file',y_artist_id,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(a_map_file):
        print 'ERROR: file',a_map_file,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(y_user_ratings):
        print 'ERROR: file',y_user_ratings,'does not exist.'
        sys.exit(0)

    # initial time
    t1 = time.time()

    # read mapping, keep list of known Yahoo artist ID
    known_y_artist_names = set()
    f = open(a_map_file,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        yname = line.split('<SEP>')[0]
        known_y_artist_names.add(yname)
    f.close()
    print 'Found',len(known_y_artist_names),'Yahoo artist names that we know.'

    # read yahoo artist_id - artist_names to see which ID we know
    known_y_artist_id = set()
    f = open(y_artist_id,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        yid,yname = line.strip().split('\t')
        if yname in known_y_artist_names:
            known_y_artist_id.add(int(yid))
    f.close()
    print 'Found',len(known_y_artist_id),'Yahoo artist id that we know.'

    # count ratings belonging to one of these artists
    cnt_lines = 0
    cnt_ratings = 0
    f = open(y_user_ratings,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        cnt_lines += 1
        y_aid = int(line.strip().split('\t')[1])
        if y_aid in known_y_artist_id:
            cnt_ratings += 1
    f.close()
    print 'Found',cnt_ratings,'ratings for known artists out of',cnt_lines,'ratings.'
    print 'This means we cover',str(int(cnt_ratings * 10000. / cnt_lines)/100.)+'% of the ratings.'
    stimelen = str(datetime.timedelta(seconds=time.time()-t1))
    print 'All done in',stimelen
