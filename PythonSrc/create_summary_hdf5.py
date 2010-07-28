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
import glob
# our HDF utils library
import hdf5_utils as HDF5
import hdf5_descriptors as HDF5_DESC


def get_all_files(basedir,pattern='*.h5',relative=False) :
    """
    From a root directory, go through all subdirectories
    and find all files that fit the pattern (usually a specific
    extension). Return the absolute paths in a list, unless
    relative is True, then relative path from basedir.
    """
    allfiles = []
    for root, dirs, files in os.walk(basedir):
        foundfiles = glob.glob(os.path.join(root,pattern))
        for f in foundfiles :
            if not relative:
                allfiles.append( os.path.abspath(f) )
            else:
                allfiles.append( os.path.relpath(f,basedir) )
    return allfiles




def fill_summary_file(summ_hdf5_file,hdf5files,basedir=''):
    """
    Fill a summary file from a list of path to existing song HDF5 files.
    If paths are relative, you must provide base dir so we can find them.
    """
    # open summary file, get tables
    summ_h5 = HDF5.open_h5_file_append(summ_hdf5_file)
    metadata = summ_h5.root.metadata.songs
    analysis = summ_h5.root.analysis.songs
    path = summ_h5.root.path.songs
    path_row = path.row
    # iterate on hdf5 files
    print 'filling summary file with',len(hdf5files),'existing song HDF5 files'
    for h5file in hdf5files:
        # open h5 file
        h5 = HDF5.open_h5_file_read(os.path.join(basedir,h5file))
        # transfer metadata
        for p in h5.root.metadata.songs:
            metadata.append([p[:]])
        # transfer analysis
        for p in h5.root.analysis.songs:
            analysis.append([p[:]])
        # add path
        path_row['path'] = h5file
        path_row.append()
        # close h5 file
        h5.close()
    # iterations done, flush tables
    metadata.flush()
    analysis.flush()
    path.flush()
    # iterations done, close summary file
    summ_h5.close()




def die_with_usage():
    """
    HELP MENU
    """
    print 'create_summary_hdf5.py'
    print 'by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'From a directory of HDF5 encoded songs, create a summary'
    print 'file containing metadata + paths'
    print 'usage:'
    print '  python create_summary_hdf5.py <dirpath> <new hdf5file>'
    print ''
    sys.exit(0)




if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # args and sanity checks
    dirpath = sys.argv[1]
    summ_hdf5_path = sys.argv[2]
    if not os.path.exists(dirpath):
        print 'ERROR: song dir does not exist:',dirpath
        die_with_usage()
    if os.path.exists(summ_hdf5_path):
        print 'ERROR: hdf5 file already exist:',summ_hdf5_path,', delete or choose new path'
        die_with_usage()

    # get all hdf5 paths in dirpath, relative to dirpath
    hdf5files = get_all_files(dirpath,pattern='*.h5',relative=True)

    # create summarized hdf5 file
    HDF5.create_summary_file(summ_hdf5_path)

    # fill summary hdf5 file
    fill_summary_file(summ_hdf5_path,hdf5files,basedir=dirpath)
