"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains a set of routines to create HDF5 files containing
features and metadata of a song.

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
# code relies on pytables, see http://www.pytables.org
import tables
import hdf5_descriptors as DESC



def fill_hdf5_from_track(h5,track,verbose=0):
    """
    Fill an open hdf5 using all the content in a track object
    from the Echo Nest python API
    Put verbose to 2 or higher to see details.
    """
    # get the metadata table, fill it
    metadata = h5.root.metadata.songs.row
    metadata['artist'] = track.artist
    if verbose > 1:
        print "metadata['artist'] = ",metadata['artist']
    metadata['duration'] = track.duration
    if verbose > 1:
        print "metadata['duration'] = ",metadata['duration']
    metadata['end_of_fade_in'] = track.end_of_fade_in
    if verbose > 1:
        print "metadata['end_of_fade_in'] = ",metadata['end_of_fade_in']
    metadata['id'] = track.id
    if verbose > 1:
        print "metadata['id'] = ",metadata['id']
    metadata['sample_md5'] = track.sample_md5
    if verbose > 1:
        print "metadata['sample_md5'] = ",metadata['sample_md5']
    metadata.append()
    # get the analysis table, fill it
    analysis = h5.root.analysis.songs.row
    analysis['duration'] = track.duration
    if verbose > 1:
        print "analysis['duration'] = ",analysis['duration']
    analysis['key'] = track.key
    if verbose > 1:
        print "analysis['key'] = ",analysis['key']
    analysis['key_confidence'] = track.key_confidence
    if verbose > 1:
        print "analysis['key_confidence'] = ",analysis['key_confidence']
    analysis['loudness'] = track.loudness
    if verbose > 1:
        print "analysis['loudness'] = ",analysis['loudness']
    analysis['mode'] = track.mode
    if verbose > 1:
        print "analysis['mode'] = ",analysis['mode']
    analysis['mode_confidence'] = track.mode_confidence
    if verbose > 1:
        print "analysis['mode_confidence'] = ",analysis['mode_confidence']
    analysis.append()
    raise NotImplementedError


def create_song_file(h5filename,title='H5 Song File',force=False):
    """
    Create a new HDF5 file for a new song.
    If force=False, refuse to overwrite an existing file
    Raise a ValueError if it's the case.
    Other optional param is the H5 file.

    Setups the groups, each containing a table 'songs':
    - metadata
    - analysis
    """
    # check if file exists
    if not force:
        if os.path.exists(h5filename):
            raise ValueError('file exists, can not create HDF5 song file')
    # create the H5 file
    h5 = tables.openFile(h5filename, mode='w', title='H5 Song File')
    # setup the groups and tables
        # group metadata
    group = h5.createGroup("/",'metadata','metadata about the song')
    table = h5.createTable(group,'songs',DESC.SongMetaData,'table of metadata for one song')
        # group analysis
    group = h5.createGroup("/",'analysis','Echo Nest analysis of the song')
    table = h5.createTable(group,'songs',DESC.SongAnalysis,'table of Echo Nest analysis for one song')
    # close it, done
    h5.close()


def open_h5_file_read(h5filename):
    """
    Open an existing H5 in read mode.
    """
    return tables.openFile(h5filename, mode='r')

def open_h5_file_append(h5filename):
    """
    Open an existing H5 in append mode.
    """
    return tables.openFile(h5filename, mode='a')



def die_with_usage():
    """ HELP MENU """
    print 'hdf5_utils.py'
    print 'by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'should be used as a library, contains functions to create'
    print 'HDF5 files for the Million Song Dataset project'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    die_with_usage()


