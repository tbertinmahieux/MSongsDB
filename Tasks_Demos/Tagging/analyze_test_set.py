"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to analyze the test set, and give a benchmark result
for automatic tagging based on no audio analysis.

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
import glob
import time
import numpy as np
import sqlite3



def die_with_usage():
    """ HELP MENU """
    print 'analyze_test_set.py'
    print '    by T. Bertin-Mahieux (2011) Columbia University'
    print '       tb2332@columbia.edu'
    print ''
    print 'Code to analyze the test set, and give a benchmark result for'
    print 'automatic tagging based on tag stats (no audio analysis)'
    print ''
    print 'USAGE'
    print '   python analyze_test_set.py <artist_test.txt> <track_metadata.db> <artist_term.db>'
    print 'PARAM'
    print '    artist_test.txt  - list of artists in the test set'
    print '  track_metadata.db  - SQLite database with metadata per track'
    print '     artist_term.db  - SQLite database with Echo Nest terms per artist'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # params
    artist_test_file = sys.argv[1]
    track_metadata_db_file = sys.argv[2]
    artist_term_db_file = sys.argv[3]

    # sanity check
    if not os.path.isfile(artist_test_file):
        print 'ERROR: file',artist_test_file,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(track_metadata_db_file):
        print 'ERROR: file',track_metadata_db_file,'does not exist.'
        sys.exit(0)
    if not os.path.isfile(artist_term_db_file):
        print 'ERROR: file',artist_term_db_file,'does not exist.'
        sys.exit(0)
    
