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
# postgresql
try:
    import pg
except ImportError:
    print "You don't have the 'pg' module, can't use musicbrainz server"
try:
    import multiprocessing
except ImportError:
    print "You can't use multiprocessing"
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

# for multiprocessing
class KeyboardInterruptError(Exception):pass

def convert_one_song(audiofile,output,mbconnect=None,verbose=0,DESTROYAUDIO=False):
    """
    PRINCIPAL FUNCTION
    Converts one given audio file to hdf5 format (saved in 'output')
    by uploading it to The Echo Nest API
    INPUT
         audiofile   - path to a typical audio file (wav, mp3, ...)
            output   - nonexisting hdf5 path
         mbconnect   - if not None, open connection to musicbrainz server
           verbose   - if >0 display more information
      DESTROYAUDIO   - Careful! deletes audio file if everything went well
    RETURN
       1 if we think a song is created, 0 otherwise
    """
    # inputs + sanity checks
    if not os.path.exists(audiofile):
        print 'ERROR: song file does not exist:',songfile
        return 0
    if os.path.exists(output):
        print 'ERROR: hdf5 output file already exist:',output,', delete or choose new path'
        return 0
    # get EN track / song / artist for that song
    if verbose>0: print 'get analysis for file:',audiofile
    track = trackEN.track_from_filename(audiofile)
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
    if verbose>0: print 'create HDF5 file:',output
    HDF5.create_song_file(output,force=False)
    # fill hdf5 file from track
    if verbose>0:
        if mbconnect is None:
            print 'fill HDF5 file with info from track/song/artist'
        else:
            print 'fill HDF5 file with info from track/song/artist/musicbrainz'
    h5 = HDF5.open_h5_file_append(output)
    HDF5.fill_hdf5_from_artist(h5,artist)
    HDF5.fill_hdf5_from_song(h5,song)
    HDF5.fill_hdf5_from_track(h5,track)
    if not mbconnect is None:
        HDF5.fill_hdf5_from_musicbrainz(h5,mbconnect)
    h5.close()
    # done
    if DESTROYAUDIO:
        if verbose>0: print 'We remove audio file:',audiofile
        os.remove(audiofile)
    return 1


def convert_one_song_wrapper(args):
    """ for multiprocessing """
    mbconnect = None
    if args['usemb']:
        if verbose>0: print 'fill HDF5 file using musicbrainz'
        mbconnect = pg.connect('musicbrainz_db','localhost',-1,None,None,
                               args['mbuser'],args['mbpasswd'])
    try:
        convert_one_song(args['audiofile'],args['output'],
                         mbconnect=mbconnect,verbose=args['verbose'],
                         DESTROYAUDIO=args['DESTROYAUDIO'])
    except KeyboardInterrupt:
        raise KeyboardInterruptError()
    except Exception, e:
        print 'ERROR with file:',args['audiofile']+':',e
    finally:
        if not mbconnect is None:
            mbconnect.close()


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
    print ' OR'
    print '  python enpyapi_to_hdf5.py [FLAGS] -dir <inputdir>'
    print 'PARAMS'
    print '  songpath      - path a song in a usual format, e.g. MP3'
    print '  new hdf5file  - output, e.g. mysong.h5'
    print '      inputdir  - in that mode, converts every known song (mp3,wav,au,ogg)'
    print '                  in all subdirectories, outputpath is songpath + .h5 extension'
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
    inputdir = ''
    nthreads = 1
    DESTROYAUDIO=False # let's not advertise that flag in the help menu
    while True:
        if len(sys.argv) < 2: # happens with -dir option
            break
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
        elif sys.argv[1] == '-dir':
            inputdir = sys.argv[2]
            sys.argv.pop(1)
        elif sys.argv[1] == '-nthreads':
            nthreads = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-DESTROYAUDIO':
            DESTROYAUDIO = True
        else:
            break
        sys.argv.pop(1)

    # if we only do one file!
    if inputdir == '':
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
        # musicbrainz
        mbconnect = None
        if usemb:
            if verbose>0: print 'fill HDF5 file using musicbrainz'
            mbconnect = pg.connect('musicbrainz_db','localhost',-1,None,None,mbuser,mbpasswd)
        # transform
        convert_one_song(songfile,hdf5file,mbconnect=mbconnect,verbose=verbose)
        # close connection
        if not mbconnect is None:
            mbconnect.close()
        # verbose
        if verbose > 0:
            t2 = time.time()
            print 'From audio:',songfile,'we created hdf5 file:',hdf5file,'in',str(int(t2-t1)),'seconds.'

    # we have an input dir, one thread
    elif nthreads == 1:
        # sanity check
        if not os.path.isdir(inputdir):
            print 'ERROR: input directory',inputdir,'does not exist.'
            print '********************************'
            die_with_usage()
        # musicbrainz
        mbconnect = None
        if usemb:
            if verbose>0: print 'fill HDF5 file using musicbrainz'
            mbconnect = pg.connect('musicbrainz_db','localhost',-1,None,None,mbuser,mbpasswd)
        # iterate
        cnt_songs = 0
        cnt_done = 0
        for root,dirs,files in os.walk(inputdir):
            files = filter(lambda x: os.path.splitext(x)[1] in ('.wav','.ogg','.au','.mp3'),
                           files)
            files = map(lambda x: os.path.join(root,x), files)
            for f in files:
                cnt_songs += 1
                if cnt_songs % 100 == 0:
                    if verbose>0: print 'DOING FILE #'+str(cnt_songs)
                try:
                    cnt_done += convert_one_song(f,f+'.h5',mbconnect=mbconnect,verbose=verbose,
                                                 DESTROYAUDIO=DESTROYAUDIO)
                except KeyboardInterrupt:
                    raise
                except Exception, e:
                    print 'ERROR with file:',f+':',e
        # iteration done
        if verbose>0:
            print 'Converted',str(cnt_done)+'/'+str(cnt_songs),'in all subdirectories of',inputdir
            t2 = time.time()
            print 'All conversions took:',str(int(t2-t1)),'seconds.'
        # close musicbrainz
        if not mbconnect is None:
            mbconnect.close()


    # input dir, many threads
    # YOU SHOULD NOT USE THIS FUNCTION UNLESS YOU HAVE MORE THAN 1000 FILES
    else:
        assert nthreads > 0,'negative or null number of threads? come one!'
        # get all songs
        allsongs = []
        for root,dirs,files in os.walk(inputdir):
            files = filter(lambda x: os.path.splitext(x)[1] in ('.wav','.ogg','.au','.mp3'),
                           files)
            files = map(lambda x: os.path.join(root,x), files)
            allsongs.extend( files )
        if verbose>0: print 'We found',len(allsongs),'songs.'
        # musicbrainz
        mbconnect = None
        if usemb:
            if verbose>0: print 'fill HDF5 file using musicbrainz'
            mbconnect = pg.connect('musicbrainz_db','localhost',-1,None,None,mbuser,mbpasswd)
        # prepare params
        params_list = map(lambda x: {'verbose':verbose,'DESTROYAUDIO':DESTROYAUDIO,
                                     'audiofile':x,'output':x+'.h5','usemb':usemb,
                                     'mbuser':mbuser,'mbpasswd':mbpasswd},allsongs)
        # launch, run all the jobs
        pool = multiprocessing.Pool(processes=nthreads)
        try:
            pool.map(convert_one_song_wrapper, params_list)
            pool.close()
            pool.join()
        except KeyboardInterruptError:
            print 'MULTIPROCESSING'
            print 'stopping multiprocessing due to a keyboard interrupt'
            pool.terminate()
            pool.join()
        except Exception, e:
            print 'MULTIPROCESSING'
            print 'got exception: %r, terminating the pool' % (e,)
            pool.terminate()
            pool.join()
        # musicbrainz
        if not mbconnect is None:
            mbconnect.close()
        # all done!
        if verbose>0:
            t2 = time.time()
            print 'Program ran for:',str(int(t2-t1)),'seconds with',nthreads,'threads.'
