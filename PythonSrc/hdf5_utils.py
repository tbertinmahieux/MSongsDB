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
import numpy as np
# code relies on pytables, see http://www.pytables.org
import tables
import hdf5_descriptors as DESC



def fill_hdf5_from_song(h5,song):
    """
    Fill an open hdf5 using all the content in a song object
    from the Echo Nest python API.
    Usually, fill_hdf5_from_track() will have been called first.
    """
    # get the metadata table, fill it
    metadata = h5.root.metadata.songs
    metadata.cols.artist_familiarity[0] = song.artist_familiarity
    metadata.cols.artist_hotttness[0] = song.artist_hotttness
    metadata.cols.artist_id[0] = song.artist_id
    metadata.cols.artist_latitude[0] = song.artist_location.latitude
    metadata.cols.artist_location[0] = song.artist_location.location
    metadata.cols.artist_longitude[0] = song.artist_location.longitude
    metadata.cols.artist_name[0] = song.artist_name
    metadata.flush()
    # get the analysis table
    analysis = h5.root.analysis.songs
    analysis.cols.tempo[0] = song.audio_summary.tempo
    analysis.flush()
    raise NotImplementedError

    

def fill_hdf5_from_track(h5,track):
    """
    Fill an open hdf5 using all the content in a track object
    from the Echo Nest python API
    """
    # get the metadata table, fill it
    metadata = h5.root.metadata.songs
    metadata.cols.analyzer_version[0] = track.analyzer_version
    metadata.cols.artist[0] = track.artist
    metadata.cols.audio_md5[0] = track.audio_md5
    metadata.cols.bitrate[0] = track.bitrate
    metadata.cols.duration[0] = track.duration
    metadata.cols.id[0] = track.id
    metadata.cols.release[0] = track.release
    metadata.cols.sample_md5[0] = track.sample_md5
    metadata.cols.samplerate[0] = track.samplerate
    metadata.cols.title[0] = track.title
    metadata.flush()
    # get the analysis table, fill it
    analysis = h5.root.analysis.songs
    analysis.cols.duration[0] = track.duration
    analysis.cols.end_of_fade_in[0] = track.end_of_fade_in
    analysis.cols.key[0] = track.key
    analysis.cols.key_confidence[0] = track.key_confidence
    analysis.cols.loudness[0] = track.loudness
    analysis.cols.mode[0] = track.mode
    analysis.cols.mode_confidence[0] = track.mode_confidence
    analysis.cols.start_of_fade_out[0] = track.start_of_fade_out
    analysis.cols.time_signature[0] = track.time_signature
    analysis.cols.time_signature_confidence[0] = track.time_signature_confidence
    analysis.flush()
    group = h5.root.analysis
    # analysis arrays (segments)
    h5.createArray(group,'segments_start',np.array(map(lambda x : x['start'],track.segments)),'array of start times of segments')
    h5.createArray(group,'segments_confidence',np.array(map(lambda x : x['confidence'],track.segments)),'array of confidence of segments')
    h5.createArray(group,'segments_pitches',np.array(map(lambda x : x['pitches'],track.segments)).transpose(),'array of pitches of segments')
    h5.createArray(group,'segments_timbre',np.array(map(lambda x : x['timbre'],track.segments)).transpose(),'array of timbre of segments')
    h5.createArray(group,'segments_loudness_max',np.array(map(lambda x : x['loudness_max'],track.segments)),'array of max loudness of segments')
    h5.createArray(group,'segments_loudness_max_time',np.array(map(lambda x : x['loudness_max_time'],track.segments)).transpose(),'array of max loudness time of segments')
    h5.createArray(group,'segments_loudness_start',np.array(map(lambda x : x['loudness_start'],track.segments)).transpose(),'array of loudness of segments at start time')    
    # analysis arrays (sections)
    h5.createArray(group,'sections_start',np.array(map(lambda x : x['start'],track.sections)),'array of start times of sections')
    h5.createArray(group,'sections_confidence',np.array(map(lambda x : x['confidence'],track.sections)),'array of confidence of sections')
    # analysis arrays (beats)
    h5.createArray(group,'beats_start',np.array(map(lambda x : x['start'],track.beats)),'array of start times of beats')
    h5.createArray(group,'beats_confidence',np.array(map(lambda x : x['confidence'],track.beats)),'array of confidence of beats')
    # analysis arrays (bars)
    h5.createArray(group,'bars_start',np.array(map(lambda x : x['start'],track.bars)),'array of start times of bars')
    h5.createArray(group,'bars_confidence',np.array(map(lambda x : x['confidence'],track.bars)),'array of confidence of bars')
    # analysis arrays (tatums)
    h5.createArray(group,'tatums_start',np.array(map(lambda x : x['start'],track.tatums)),'array of start times of tatums')
    h5.createArray(group,'tatums_confidence',np.array(map(lambda x : x['confidence'],track.tatums)),'array of confidence of tatums')    
    # DONE


def create_song_file(h5filename,title='H5 Song File',force=False):
    """
    Create a new HDF5 file for a new song.
    If force=False, refuse to overwrite an existing file
    Raise a ValueError if it's the case.
    Other optional param is the H5 file.

    Setups the groups, each containing a table 'songs' with one row:
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
    r = table.row
    r.append()
    table.flush()
        # group analysis
    group = h5.createGroup("/",'analysis','Echo Nest analysis of the song')
    table = h5.createTable(group,'songs',DESC.SongAnalysis,'table of Echo Nest analysis for one song')
    r = table.row
    r.append()
    table.flush()
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


