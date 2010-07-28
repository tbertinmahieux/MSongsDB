"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains is a standalone that creates a 'summary' file
(originally intended in SQLite) that contains all the metadata of
the songs and path to their respective HDF5 file.


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
# our HDF utils library
import hdf5_utils as HDF5











def die_with_usage():
    """
    HELP MENU
    """
    print 'create_summarized_hdf5.py'
    print 'by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'From a directory of HDF5 encoded songs, create a summarized'
    print 'file containing metadata + paths'
    print 'usage:'
    print '  python create_summarized_hdf5.py <dirpath> <new hdf5file>'
    print ''
    sys.exit(0)




if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # args and sanity checks
    dirpath = sys.argv[1]
    summ_hdf5_path = sys.arg[2]
    if not os.path.exists(dirpath):
        print 'ERROR: song dir does not exist:',dirpath
        die_with_usage()
    if os.path.exists(summ_hdf5_path):
        print 'ERROR: hdf5 file already exist:',summ_hdf5_path,', delete or choose new path'
        die_with_usage()
