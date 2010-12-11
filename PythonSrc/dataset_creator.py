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
import thread
import time
import shutil
import hdf5_utils as HDF5


# lock to access the set of tracks being treated
# getting a track on the lock means having put the EN id
# of that track in the set TRACKSET
# use: get_lock_song
#      release_lock_song
TRACKSET_LOCK = thread.allocate_lock()
TRACKSET = set()
TRACKSET_CLOSED = False # use to end the process, nothing can get a
                        # track lock if this is turn to True

# HOW LONG DO WE WAIT WHEN SOMETHING GOES WRONG
SLEEPTIME = 15 # in seconds

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
                # TODO billboard? lastfm?
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
