"""
Debugging code
Takes an artist, find all the songs it can from that artist,
create one HDF5 file for each of these songs

T. Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu
"""

import os
import sys
import hdf5_utils as HDF5
from pyechonest import config
#from pyechonest import artist as artistEN
from pyechonest import song as songEN
from pyechonest import track as trackEN

CATALOG='7digital'

def die_with_usage():
    """
    HELP MENU
    """
    print 'Simple code to get all songs from an artist'
    print 'and encode each fo these songs to HDF5 format.'
    print 'Also create the summary file for all these songs.'
    print 'max song lets you encode just the first N songs, for debugging.'
    print 'usage:'
    print '   python artist_to_hdf5.py <artist name> <hdf5 dir> <opt:max song>'
    print 'example:'
    print '   mkdir TEST1'
    print '   python artist_to_hdf5.py Radiohead TEST1'
    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        die_with_usage()

    artist_name = sys.argv[1]
    hdf5dir = sys.argv[2]
    max_song = 1e10
    if len(sys.argv) > 3:
        max_song = int(sys.argv[3])

    # get all songs for that artist, up to 100 for the moment
    # SHOULD ADD try ... except urlerror
    songs = songEN.search(artist=artist_name, buckets=['id:'+CATALOG, 'tracks', 'audio_summary'], limit=True, results=100)
    if len(songs) == 0:
        print 'np songs found, nothing from 7digital? exit'
        sys.exit(0)

    # list of all h5 files created, used for summary file creation
    all_h5_files = []
        
    # for each song, encode to HDF5
    for sidx,song in enumerate(songs):
        # max song
        if sidx >= max_song:
            break
        # invent a proper file name
        hdf5_path = os.path.join(hdf5dir,str(sidx)+'.h5')
        if os.path.exists(hdf5_path):
            print 'file',hdf5_path,'already exists, to be careful we stop.'
            sys.exit(0)
        # get the track
        try:
            tracks = song.get_tracks(CATALOG)
        except IndexError:
            print 'should not happen with new API!!!!'
            continue
        track = trackEN.track_from_id(tracks[0]['id'])
        print 'track name:',track
        # create HDF5 file, open it and get it
        HDF5.create_song_file(hdf5_path)
        h5 = HDF5.open_h5_file_append(hdf5_path)
        # fill in with songs
        HDF5.fill_hdf5_from_song(h5,song)
        # fill in with track
        HDF5.fill_hdf5_from_track(h5,track)
        # close h5 file
        h5.close()
        # add filename to list
        all_h5_files.append( hdf5_path )

    # individual files done, create summary
    print 'ALL SONGS ENCODED, WE CREATE SUMMARY'
    hdf5_summary_path = os.path.join(hdf5dir,'summary.h5')
    HDF5.create_summary_file(hdf5_summary_path)
    h5 = HDF5.open_h5_file_append(hdf5_summary_path)
    HDF5.fill_hdf5_summary_file(h5,all_h5_files)
    h5.close()



