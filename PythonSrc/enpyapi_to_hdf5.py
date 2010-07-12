"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains is a standalone (and debugging tool)
that uploads a song to the Echo Nest API and creates a HDF5 with it.

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
# Echo Nest python API
from pyechonest import song as songEN
from pyechonest import track as trackEN
from pyechonest import config
try:
    config.ECHO_NEST_API_KEY = os.environ['ECHO_NEST_API_KEY']
except KeyError: # historic reasons
    config.ECHO_NEST_API_KEY = os.environ['ECHONEST_API_KEY']








def die_with_usage():
    """ HELP MENU """
    print 'enpyapi_to_hdf5.py'
    print 'by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'Upload a song to get its analysis, writes it to a HDF5 file'
    print 'using the Million Song Database format'
    print 'usage:'
    print '  python enpyapi_to_hdf5.py <songpath> <hdf5file>'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # inputs + sanity checks
    songfile = sys.argv[1]
    hdf5file = sys.argv[2]
    if not os.path.exists(songfile):
        print 'ERROR: song file does not exist:',songfile
        die_with_usage()
    if os.path.exists(hdf5file):
        print 'ERROR: hdf5 file already exist:',hdf5file,', delete or choose new path'
        die_with_usage()

    raise NotImplementedError
