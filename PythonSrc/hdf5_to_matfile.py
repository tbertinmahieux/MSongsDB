"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code transforms a HDF5 file to a matlab file, with
the same information (as much as possible!)

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
try:
    import scipy.io as sio
    import numpy as np
except ImportError:
    print 'ERROR: you need scipy and numpy to create matfiles!'
    print 'both freely available at: http://www.scipy.org/'
    raise
# project code
import hdf5_getters
import hdf5_utils



def get_all_files(basedir,ext='.h5') :
    """
    From a root directory, go through all subdirectories
    and find all files with the given extension.
    Return all absolute paths in a list.
    """
    allfiles = []
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files :
            allfiles.append( os.path.abspath(f) )
    return allfiles



def die_with_usage():
    """ HELP MENU """
    print 'hdf5_to_matfile.py'
    print 'Transform a song file in HDF5 format to a matfile'
    print 'with the same information.'
    print ' '
    print 'usage:'
    print '   python hdf5_to_matfile.py <DIR/FILE>'
    print 'PARAM'
    print '   <DIR/FILE>   if a file TR123.h5, creates TR123.mat in the same dir'
    print '                if a dir, do it for all .h5 files in every subdirectory'
    print ' '
    print 'REQUIREMENTS'
    print '   as usual: HDF5 C library, numpy/scipy, pytables'
    print ' '
    print 'copyright: T. Bertin-Mahieux (2010) Columbia University'
    print 'tb2332@columbia.edu'
    print 'Million Song Dataset project with LabROSA and the Echo Nest'
    sys.exit(0)

if __name__ == '__main__':

    # HELP MENU
    if len(sys.argv) < 2:
        die_with_usage()

    # GET DIR/FILE
    if not os.path.exists(sys.argv[1]):
        print 'file or dir:',sys.argv[1],'does not exist.'
        sys.exit(0)
    if os.path.isfile(sys.argv[1]):
        if os.path.splitext(sys.argv[1])[1] != '.h5':
            print 'we expect a .h5 extension for file:',sys.argv[1])
            sys.exit(0)
        allh5files = [ os.path.abspath(sys.argv[1]) ]
    elif not os.path.isdir(sys.argv[1]):
        print sys.argv[1],"is neither a file nor a directory? confused... a link? c'est klug?"
        sys.exit(0)
    allh5files = get_all_files(sys.argv[1],ext='.h5')

    # final sanity checks
    for f in allh5files:
        assert os.path.splitext(f)[1] == '.h5','file with wrong extension? should have been caught earlier... file='+f
    nFiles = len(allh5files)
    if nFiles > 1000:
        print 'you are creating',nFiles,'new matlab files, hope you have the space and time!'

    # let's go!
    


    
