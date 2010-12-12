"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code contains code used when creating the actual MSong dataset,
i.e. functions to create a song HDF5 at the right place, with proper
locks for multithreading.

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
import thread
import time
import shutil
import numpy.random as npr
import hdf5_utils as HDF5


# pyechonest objects
# API_KEY should be found automatically, if not, set pyechonest.config
import pyechonest
from pyechonest import artist as artistEN
from pyechonest import song as songEN
from pyechonest import track as trackEN
CATALOG='7digital'

# posgresql import and info for musicbrainz dataset
import pg
MBUSER='gordon'
MBPASSWD='gordon'

# HOW LONG DO WE WAIT WHEN SOMETHING GOES WRONG
SLEEPTIME = 15 # in seconds

# lock to access the set of tracks being treated
# getting a track on the lock means having put the EN id
# of that track in the set TRACKSET
# use: get_lock_song
#      release_lock_song
TRACKSET_LOCK = thread.allocate_lock()
TRACKSET = set()
TRACKSET_CLOSED = False # use to end the process, nothing can get a
                        # track lock if this is turn to True


def close_trackset():
    """
    When terminating the thread, nothing can add anything
    to TRACKSET anymore
    """
    global TRACKSET_CLOSED
    TRACKSET_CLOSED = True

def get_lock_track(trackid):
    """
    Get the lock for the creation of one particular file
    Returns True if you got, False otherwise (meaning
    someone else just got it
    This is a blocking call.
    """
    got_lock = TRACKSET_LOCK.acquire(1) # blocking=1
    if not got_lock:
        print 'ERROR: could not get TRACKSET_LOCK lock?'
        return False
    if TRACKSET_CLOSED:
        TRACKSET_LOCK.release()
        return False
    if trackid in TRACKSET:
        TRACKSET_LOCK.release()
        return False
    TRACKSET.add( trackid )
    TRACKSET_LOCK.release()
    return True

def release_lock_track(trackid):
    """
    Release the lock for the creation of one particular file.
    Should always return True, unless there is a problem
    Releasing a song that you don't have the lock on is dangerous.
    """
    got_lock = TRACKSET_LOCK.acquire(1) # blocking=1
    if not got_lock:
        print 'ERROR: could not get TRACKSET_LOCK lock?'
        return False
    if TRACKSET_CLOSED:
        TRACKSET_LOCK.release()
        return False
    if not trackid in TRACKSET:
        TRACKSET_LOCK.release()
        print 'WARNING: releasing a song you dont own'
        return False
    TRACKSET.remove(trackid)
    TRACKSET_LOCK.release()
    return True
        

def path_from_trackid(trackid):
    """
    Returns the typical path, with the letters[2-3-4]
    of the trackid (starting at 0), hence a song with
    trackid: TRABC1839DQL4H... will have path:
    A/B/C/TRABC1839DQL4H....h5
    """
    p = os.path.join(trackid[2],trackid[3])
    p = os.path.join(p,trackid[4])
    p = os.path.join(p,trackid+'.h5')
    return p


def count_h5_files(basedir):
    """
    Return the number of hdf5 files contained in all
    subdirectories of base
    """
    cnt = 0
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*.h5'))
        cnt += len(files)
    return cnt


def create_track_file(maindir,trackid,track,song,artist,mbconnect=None):
    """
    Main function to create an HDF5 song file.
    You got to have the track, song and artist already.
    If you pass an open connection to the musicbrainz database, we also use it.
    Returns True if song was created, False otherwise.
    False can mean another thread is already doing that song.
    We also check whether the path exists.
    """
    hdf5_path = os.path.join(maindir,path_from_trackid(trackid))
    if os.path.exists( hdf5_path ):
        return False # file already exists, no stress
    hdf5_path_tmp = hdf5_path + '_tmp'
    # lock the file
    got_lock = get_lock_track(trackid)
    if not got_lock:
        return False # someone is taking care of that file
    if os.path.exists( hdf5_path ):
        release_lock_track(trackid)
        return False # got the lock too late, file exists
    # create file and fill it
    try:
        while True: # try until we make it work!
            try:
                if not os.path.isdir( os.path.split(hdf5_path)[0] ):
                    os.makedirs( os.path.split(hdf5_path)[0] )
                # check / delete tmp file if exist
                if os.path.isfile(hdf5_path_tmp):
                    os.remove(hdf5_path_tmp)
                # create tmp file
                HDF5.create_song_file(hdf5_path_tmp)
                h5 = HDF5.open_h5_file_append(hdf5_path_tmp)
                HDF5.fill_hdf5_from_artist(h5,artist)
                HDF5.fill_hdf5_from_song(h5,song)
                HDF5.fill_hdf5_from_track(h5,track)
                if mbconnect is not None:
                    HDF5.fill_hdf5_from_musicbrainz(h5,mbconnect)
                # TODO billboard? lastfm? ...?
                h5.close()
            except KeyboardInterrupt:
                raise
            # we dont panic, delete file, wait and retry
            except Exception as e:
                # close hdf5
                try:
                    h5.close()
                except NameError,ValueError:
                    pass
                # delete path
                try:
                    os.remove( hdf5_path_tmp )
                except IOError:
                    pass
                # print and wait
                print 'ERROR creating track:',trackid,'on',time.ctime()
                print e
                print '(try again in',SLEEPTIME,'seconds)'
                time.sleep(SLEEPTIME)
                continue
            # move tmp file to real file
            shutil.move(hdf5_path_tmp, hdf5_path)
            # release lock
            release_lock_track(trackid)
            break
    # KeyboardInterrupt, we delete file, clean things up
    except KeyboardInterrupt:
        close_trackset()
        # close hdf5
        try:
            h5.close()
        except NameError,ValueError:
            pass
        # delete path
        try:
            if os.path.isfile( hdf5_path_tmp ):
                os.remove( hdf5_path_tmp )
            if os.path.isfile( hdf5_path ):
                os.remove( hdf5_path )
        except IOError:
            pass
        raise
    # IF WE GET HERE WE'RE GOOD
    return True



def create_track_file_from_trackid(maindir,trackid,song,artist,mbconnect=None):
    """
    Get a track from a track id and calls for its creation.
    We assume we already have song and artist.
    We can have a connection to musicbrainz as an option.
    This function should create only one file!
    GOAL: mostly, it checks if we have the track already created before
          calling EchoNest API. It saves some calls/time
          Also, handles some errors.
    INPUT
        maindir    - MillionSongDataset root directory
        trackid    - Echo Nest track ID (string: TRABC.....)
        song       - pyechonest song object for that track
        artist     - pyechonest artist object for that song/track
        mbconnect  - open musicbrainz pg connection
    RETURN
        true if a song file is created, false otherwise
    """
    # do we already have this track in the dataset?
    track_path = os.path.join(maindir,path_from_trackid(trackid))
    if os.path.exists(track_path):
        return False
    # get that track!
    while True:
        try:
            track = trackEN.track_from_id(trackid)
            break
        except KeyboardInterrupt:
            raise
        except Exception,e:
            print type(e),':',e
            print 'at time',time.ctime(),'in create_track_file_from_trackid, tid=',trackid,'(we wait',SLEEPTIME,'seconds)'
            time.sleep(SLEEPTIME)
            continue
    # we have everything, launch create track file
    return create_track_file(maindir,trackid,track,song,artist,mbconnect=mbconnect)



def create_track_file_from_song(maindir,song,artist,mbconnect=None):
    """
    Get tracks from a song, choose the first one and calls for its creation.
    We assume we already have song and artist.
    We can have a connection to musicbrainz as an option.
    This function should create only one file!
    GOAL: handles some errors.
    INPUT
        maindir    - MillionSongDataset root directory
        song       - pyechonest song object for that track
        artist     - pyechonest artist object for that song/track
        mbconnect  - open musicbrainz pg connection
    RETURN
        true if a song file is created, false otherwise
    """
    # get that track id
    while True:
        try:
            tracks = song.get_tracks(CATALOG)
            trackid = tracks[0]['id']
            break
        except IndexError:
            return False # should not happen according to EN guys, but still does...
        except KeyboardInterrupt:
            raise
        except Exception,e:
            print type(e),':',e
            print 'at time',time.ctime(),'in create_track_file_from_song, sid=',song.id,'(we wait',SLEEPTIME,'seconds)'
            time.sleep(SLEEPTIME)
            continue
    # we got the track id, call for its creation
    # if a file for that trackid already exists, it will be caught immediately in the next function
    return create_track_file_from_trackid(maindir,trackid,song,artist,mbconnect=mbconnect)


def create_track_file_from_song_noartist(maindir,song,mbconnect=None):
    """
    After getting the artist, get tracks from a song, choose the first one and calls for its creation.
    We assume we already have a song.
    We can have a connection to musicbrainz as an option.
    This function should create only one file!
    GOAL: handles some errors.
    INPUT
        maindir    - MillionSongDataset root directory
        song       - pyechonest song object for that track
        mbconnect  - open musicbrainz pg connection
    RETURN
        true if a song file is created, false otherwise
    """
    # get that artist
    while True:
        try:
            artist = artistEN.artist(song.artist_id)
            break
        except KeyboardInterrupt:
            raise
        except pyechonest.util.EchoNestAPIError,e:
            print 'MAJOR ERROR, wrong artist id?'
            print e # means the ID does not exist
            return False
        except Exception,e:
            print type(e),':',e
            print 'at time',time.ctime(),'in create_track_files_from_song_noartist, sid=',song.id,'(we wait',SLEEPTIME,'seconds)'
            time.sleep(SLEEPTIME)
            continue
    # get his songs, creates his song files, return number of actual files created
    return create_track_file_from_song(maindir,song,artist,mbconnect=mbconnect)


def create_track_files_from_artist(maindir,artist,mbconnect=None,maxsongs=100):
    """
    Get all songs from an artist, for each song call for its creation
    We assume we already have artist.
    We can have a connection to musicbrainz as an option.
    This function should create only one file!
    GOAL: handles some errors.
    INPUT
        maindir    - MillionSongDataset root directory
        artist     - pyechonest artist object for that song/track
        mbconnect  - open musicbrainz pg connection
        maxsongs   - maximum number of files retrieved, default=100, should be 500 or 1k
    RETURN
        number fo files created, 0<=...<=1000?
    """
    assert maxsongs <= 1000,'dont think we can query for more than 1K songs per artist'
    if maxsongs==100:
        print 'WARNING,create_track_files_from_artist, start param should be implemented'
    # get all the songs we want
    allsongs = []
    while True:
        try:
            n_missing = maxsongs - len(allsongs)
            n_askfor = min(n_missing,100)
            start = len(allsongs)
            songs = songEN.search(artist_id=artist.id, buckets=['id:'+CATALOG, 'tracks', 'audio_summary',
                                                                'artist_familiarity','artist_hotttnesss',
                                                                'artist_location','song_hotttnesss'],
                                  limit=True, results=n_askfor)
            allsongs.extend(songs)
            if len(allsongs) >= maxsongs or len(songs) < n_askfor:
                break
        except KeyboardInterrupt:
            raise
        except Exception,e:
            print type(e),':',e
            print 'at time',time.ctime(),'in create_track_file_from_artist, aid=',artist.id,'(we wait',SLEEPTIME,'seconds)'
            time.sleep(SLEEPTIME)
            continue
    # shuffle the songs, to help multithreading
    npr.shuffle(allsongs)
    # iterate over the songs, call for their creation, count how many actually created
    cnt_created = 0
    for song in allsongs:
        created = create_track_file_from_song(maindir,song,artist,mbconnect=mbconnect)
        if created:
            cnt_created += 1
    # done
    return cnt_created
    

def create_track_files_from_artistid(maindir,artistid,mbconnect=None,maxsongs=100):
    """
    Get an artist from its ID, get all his songs, for each song call for its creation
    We assume we already have artist ID.
    We can have a connection to musicbrainz as an option.
    This function should create only one file!
    GOAL: handles some errors.
    INPUT
        maindir    - MillionSongDataset root directory
        artistid   - echonest artist id
        mbconnect  - open musicbrainz pg connection
        maxsongs   - maximum number of files retrieved, default=100, should be 500 or 1k
    RETURN
        number fo files created, 0<=...<=1000?
    """
    assert maxsongs <= 1000,'dont think we can query for more than 1K songs per artist'
    # get that artist
    while True:
        try:
            artist = artistEN.artist(artistid)
            break
        except KeyboardInterrupt:
            raise
        except pyechonest.util.EchoNestAPIError,e:
            print 'MAJOR ERROR, wrong artist id?',artistid
            print e # means the ID does not exist
            return 0
        except Exception,e:
            print type(e),':',e
            print 'at time',time.ctime(),'in create_track_files_from_artistid, aid=',artistid,'(we wait',SLEEPTIME,'seconds)'
            time.sleep(SLEEPTIME)
            continue
    # get his songs, creates his song files, return number of actual files created
    return create_track_files_from_artist(maindir,artist,mbconnect=mbconnect,maxsongs=maxsongs)    

