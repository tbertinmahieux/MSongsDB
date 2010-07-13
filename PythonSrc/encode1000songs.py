"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code is simply to test and debug by encoding
the Echo Nest analysis of 1000 mp3 songs to hdf5 files.

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
import numpy as np
import traceback
# our HDF utils library
import hdf5_utils as HDF5
# Echo Nest python API
from pyechonest import track as trackEN
from pyechonest import config
try:
    config.ECHO_NEST_API_KEY = os.environ['ECHO_NEST_API_KEY']
except KeyError: # historic reasons
    config.ECHO_NEST_API_KEY = os.environ['ECHONEST_API_KEY']



def die_with_usage():
    """ HELP MENU """
    print 'encode1000songs.py'
    print 'by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'Upload a 1000 mp3 songs to get its analysis, writes each of them'
    print 'to a HDF5 file in the given directory'
    print 'using the Million Song Database format'
    print 'usage:'
    print '  python enpyapi_to_hdf5.py <songdir> <hdf5dir>'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    songdir = sys.argv[1]
    hdf5dir = sys.argv[2]

    # get all mp3
    allmp3s = glob.glob(os.path.join(songdir,'*.mp3'))
    if len(allmp3s) > 1000:
        allmp3s = allmp3s[:1000]

    # create hdf5 files if they don't exist yet
    for k in range(len(allmp3s)):
        # hdf5 file name
        hdf5filename = '0' * (3-len(str(k))) + str(k) + '.h5'
        hdf5filename = os.path.join(hdf5dir,hdf5filename)
        # exists? skip
        if os.path.exists(hdf5filename):
            continue
        # encode
        try:
            track = trackEN.track_from_filename(allmp3s[k])
            HDF5.create_song_file(hdf5filename,force=False)
            h5 = HDF5.open_h5_file_append(hdf5filename)
            HDF5.fill_hdf5_from_track(h5,track)
            h5.close()
        except Exception, msg:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if str(exc_type) == "<type 'exceptions.KeyboardInterrupt'>":
                raise KeyboardInterrupt
            traceback.print_exc()
            print msg
            print 'ERROR with file :',allmp3s[k]
            continue

        # display
        if np.mod(k+1,10) == 0:
            print k+1,'songs encoded'

    # done
    print 'all',len(allmp3s),'songs encoded in dir:',hdf5dir
