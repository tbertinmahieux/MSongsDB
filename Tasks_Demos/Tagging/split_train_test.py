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
import numpy as np
import sqlite3


def die_with_usage():
    """ HELP MENU """
    print 'get_unique_terms_from_db.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print 'GOAL'
    print '  split the list of artists into train and test based on terms (Echo Nest tags).'
    print 'USAGE'
    print '  python get_unique_terms_from_db.py <artist_term.db> <train.txt> <test.txt>'
    print 'PARAMS'
    print '  artist_term.db    - SQLite database containing terms per artist'
    print '       train.txt    - list of Echo Nest artist ID'
    print '        test.txt    - list of Echo Nest artist ID'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output_train = sys.argv[2]
    output_test = sys.argv[3]


