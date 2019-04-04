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
import time
import glob
try:
    import scipy.io as sio
    import numpy as np
except ImportError:
    print 'ERROR: you need scipy and numpy to create matfiles!'
    print 'both freely available at: http://www.scipy.org/'
    raise
# project code
import hdf5_getters
import utils


def transfer(h5path,matpath=None,force=False):
    """
    Transfer an HDF5 song file (.h5) to a matfile (.mat)
    If there are more than one song in the HDF5 file, each
    field name gets a number happened: 1, 2, 3, ...., numfiles
    PARAM
        h5path  - path to the HDF5 song file
        matpath - path to the new matfile, same as HDF5 path
                  with a different extension by default
        force   - if True and matfile exists, overwrite
    RETURN
        True if the file was transfered, False if there was
        a problem.
        Could also raise an IOException
    NOTE
        All the data has to be loaded in memory! be careful
        if one file contains tons of songs!
    """
    # sanity checks
    if not os.path.isfile(h5path):
        print 'path to HF5 files does not exist:',h5path
        return False
    if not os.path.splitext(h5path)[1] == '.h5':
        print 'expecting a .h5 extension for file:',h5path
        return False
    # check matfile
    if matpath is None:
        matpath = os.path.splitext(h5path)[0] + '.mat'
    if os.path.exists(matpath):
        if force:
            print 'overwriting file:',matpath
        else:
            print 'matfile',matpath,'already exists (delete or force):'
            return False
    # get all getters! we assume that all we need is in hdf5_getters.py
    # further assume that they have the form get_blablabla and that's the
    # only thing that has that form
    getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
    getters.remove("get_num_songs") # special case
    # open h5 file
    h5 = hdf5_getters.open_h5_file_read(h5path)
    # transfer
    nSongs = hdf5_getters.get_num_songs(h5)
    matdata = {'transfer_note':'transferred on '+time.ctime()+' from file: '+h5path}
    try:
        # iterate over songs
        for songidx in xrange(nSongs):
            # iterate over getter
            for getter in getters:
                gettername = getter[4:]
                if nSongs > 1:
                    gettername += str(songidx+1)
                data = hdf5_getters.__getattribute__(getter)(h5,songidx)
                matdata[gettername] = data
    except MemoryError:
        print 'Memory Error with file:',h5path
        print 'All data has to be loaded in memory before being saved as matfile'
        print 'Is this an aggregated / summary file with tons of songs?'
        print 'This code is optimized for files containing one song,'
        print 'but write me an email! (TBM)'
        raise
    finally:
        # close h5
        h5.close()
    # create
    sio.savemat(matpath,matdata)
    # all good
    return True



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
    print 'NOTE: the main function is "transfer", you can use it in your script,'
    print 'for instance if you come up with a subset of all songs that are of'
    print 'interest to you, just pass in each song path.'
    print 'Also, data for each song is loaded in memory, can be heavy if you have'
    print 'an aggregated / summary HDF5 file.'
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
            print 'we expect a .h5 extension for file:',sys.argv[1]
            sys.exit(0)
        allh5files = [ os.path.abspath(sys.argv[1]) ]
    elif not os.path.isdir(sys.argv[1]):
        print sys.argv[1],"is neither a file nor a directory? confused... a link? c'est klug?"
        sys.exit(0)
    else:
        allh5files = utils.get_all_files(sys.argv[1],ext='.h5')
    if len(allh5files) == 0:
        print 'no .h5 file found, sorry, check directory you gave us:',sys.argv[1]

    # final sanity checks
    for f in allh5files:
        assert os.path.splitext(f)[1] == '.h5','file with wrong extension? should have been caught earlier... file='+f
    nFiles = len(allh5files)
    if nFiles > 1000:
        print 'you are creating',nFiles,'new matlab files, hope you have the space and time!'

    # let's go!
    cnt = 0
    for f in allh5files:
        filedone = transfer(f)
        if filedone:
            cnt += 1

    # summary report
    print 'we did',cnt,'files out of',len(allh5files)
    if cnt == len(allh5files):
        print 'congratulations!'
    

    
