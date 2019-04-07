"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code creates a summary file, i.e. an HDF5 file that looks like song
files, except that it contains more than one song and no arrays
(beats, similar artists, tags, ...)

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
import datetime
import hdf5_utils as HDF5
import utils


def die_with_usage():
    """ HELP MENU """
    print 'create_summary_file.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '   tb2332@columbia.edu'
    print ''
    print 'Creates a summary file from all song file (h5 files)'
    print 'in a given directory.'
    print 'Summary files contains many songs and none of the arrays,'
    print 'i.e. no beat/segment data, artist similarity, tags, ...'
    print ''
    print 'usage:'
    print '   python create_summary_file.py <H5 DIR> <OUTPUT.h5>'
    print 'PARAMS'
    print '   H5 DIR     - directory contains h5 files (subdirs are checked)'
    print '   OUTPUT.h5  - filename of the summary file to create'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv)<3:
        die_with_usage()

    # params
    maindir = sys.argv[1]
    output = sys.argv[2]

    # sanity checks
    if not os.path.isdir(maindir):
        print 'ERROR: directory',maindir,'does not exists.'
        sys.exit(0)
    if os.path.isfile(output):
        print 'ERROR: file',output,'exists, delete or provide a new filename.'
        sys.exit(0)

    # start time
    t1 = time.time()

    # get all h5 files
    allh5 = utils.get_all_files(maindir,ext='.h5')
    print 'found',len(allh5),'H5 files.'

    # create summary file
    HDF5.create_aggregate_file(output,expectedrows=len(allh5),
                               summaryfile=True)
    print 'Summary file created, we start filling it.'

    # fill it
    h5 = HDF5.open_h5_file_append(output)
    HDF5.fill_hdf5_aggregate_file(h5,allh5,summaryfile=True)
    h5.close()

    # done!
    stimelength = str(datetime.timedelta(seconds=time.time()-t1))
    print 'Summarized',len(allh5),'files in:',stimelength
    
