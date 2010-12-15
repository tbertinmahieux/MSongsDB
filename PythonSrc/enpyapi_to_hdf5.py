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
import time
# our HDF utils library
import hdf5_utils as HDF5
# Echo Nest python API
from pyechonest import artist as artistEN
from pyechonest import song as songEN
from pyechonest import track as trackEN
from pyechonest import config
try:
    config.ECHO_NEST_API_KEY = os.environ['ECHO_NEST_API_KEY']
except KeyError: # historic reasons
    config.ECHO_NEST_API_KEY = os.environ['ECHONEST_API_KEY']
# musicbrainz
DEF_MB_USER = 'gordon'
DEF_MB_PASSWD = 'gordon'



def die_with_usage():
    """ HELP MENU """
    print 'enpyapi_to_hdf5.py'
    print 'by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'Upload a song to get its analysis, writes it to a HDF5 file'
    print 'using the Million Song Database format'
    print 'NO GUARANTEE THAT THE FILE IS KNOWN! => no artist or song name'
    print 'Note that we do not catch errors like timeouts, etc.'
    print ''
    print 'To have every fields filled, you need a local copy of the'
    print "musicbrainz server with recent dumps. It concerns fields 'year'"
    print "'mbtags' and 'mbtags_count'"
    print ''
    print 'usage:'
    print '  python enpyapi_to_hdf5.py [FLAGS] <songpath> <new hdf5file>'
    print 'PARAMS'
    print '  songpath      - path a song in a usual format, e.g. MP3'
    print '  new hdf5file  - output, e.g. mysong.h5'
    print 'FLAGS'
    print '  -verbose v    - set it to 0 to remove printouts'
    print '  -usemb        - use musicbrainz, e.g. you have a local copy'
    print '  -mbuser U P   - specify the musicbrainz user and password'
    print "                  (default: user='gordon' passwd='gordon')"
    print '                  (you can also change the default values in the code)'
    print ''
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # start time
    t1 = time.time()

    # flags
    mbuser = DEF_MB_USER
    mbpasswd = DEF_MB_PASSWD
    usemb = False
    verbose = 1
    while True:
        if sys.argv[1] == '-verbose':
            verbose = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-usemb':
            usemb = True
        elif sys.argv[1] == '-mbuser':
            mbuser = sys.argv[2]
            mbpasswd = sys.argv[3]
            sys.argv.pop(1)
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # inputs + sanity checks
    songfile = sys.argv[1]
    hdf5file = sys.argv[2]
    if not os.path.exists(songfile):
        print 'ERROR: song file does not exist:',songfile
        print '********************************'
        die_with_usage()
    if os.path.exists(hdf5file):
        print 'ERROR: hdf5 file already exist:',hdf5file,', delete or choose new path'
        print '********************************'
        die_with_usage()

        
    # get EN track / song / artist for that song
    if verbose>0: print 'get analysis for file:',songfile
    track = trackEN.track_from_filename(songfile)
    song_id = track.song_id
    song = songEN.Song(song_id)
    if verbose>0: print 'found song:',song.title,'(',song_id,')'
    artist_id = song.artist_id
    artist = artistEN.Artist(artist_id)
    if verbose>0: print 'found artist:',artist.name,'(',artist_id,')'

    # hack to fill missing values
    try:
        track.foreign_id
    except AttributeError:
        track.__setattr__('foreign_id','')
        if verbose>0: print 'no track foreign_id found'
    try:
        track.foreign_release_id
    except AttributeError:
        track.__setattr__('foreign_release_id','')
        if verbose>0: print 'no track foreign_release_id found'
    
    # create HDF5 file
    if verbose>0: print 'create HDF5 file:',hdf5file
    HDF5.create_song_file(hdf5file,force=False)

    # fill hdf5 file from track
    if verbose>0: print 'fill HDF5 file with info from track/song/artist'
    h5 = HDF5.open_h5_file_append(hdf5file)
    HDF5.fill_hdf5_from_artist(h5,artist)
    HDF5.fill_hdf5_from_song(h5,song)
    HDF5.fill_hdf5_from_track(h5,track)
    if usemb:
        if verbose>0: print 'fill HDF5 file using musicbrainz'
        import pg
        connect = pg.connect('musicbrainz_db','localhost',-1,None,None,mbuser,mbpasswd)
        HDF5.fill_hdf5_from_musicbrainz(h5,connect)
        connect.close()
    h5.close()

    # done
    t2 = time.time()
    if verbose > 0:
        print 'From audio:',songfile,'we created hdf5 file:',hdf5file,'in',str(int(t2-t1)),'seconds.'
    
