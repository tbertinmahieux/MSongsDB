"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code query the musicbrainz database to get some information
like musicbrainz id and release years.
The databased in installed locally.

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
import pg
import glob
import numpy as np

USER='gordon'
PASSWD='gordon'


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQL query
    EXAMPLE:
      That's my boy! -> N'That''s my boy!'
    """
    res = "N'"+s.replace("'","''")+"'"
    res = res.replace("\\''","''")
    res = res.replace("\''","''")
    return res


def connect_mbdb():
    """
    Simple connection to the musicbrainz database, returns a pgobject
    Return None if there is a problem
    """
    try:
        connect = pg.connect('musicbrainz_db','localhost',-1,None,None,
                             USER,PASSWD)
    except TypeError, e:
        print 'CONNECT_MBDB: type error, should not happen:',e
        return None
    except SyntaxError, e:
        print 'CONNECT_MBDB: syntax error, should not happen:',e
        return None
    except pg.InternalError, e:
        print 'CONNECT_MBDB, internal error:', e
        return None
    # check for levenshtein function
    #q = "SELECT levenshtein('allo','allo2')"
    #try:
    #    res = connect.query(q)
    #except pg.ProgrammingError:
    #    print 'we need levenshtein (contrib) added to the database:'
    #    print 'psql -d musicbrainz_db -f /usr/share/postgresql/8.4/contrib/fuzzystrmatch.sq'
    #    connect.close()
    #    return None
    # done
    return connect


def find_year_safemode(connect,artist_mbid,title,release,artist):
    """
    This is the main function for the creation of the MillionSongDataset
    We get a year value only if we have a recognized musicbrainz id
    and an exact match on either the title or the release (lowercase).
    Other possibility, exact match on title and artist_name or
    release_and artist_name
    INPUT
        artist_mbid   string or None          artist musicbrainz id
        title         string                  track name
        release       string ('' if unknown)  album name
        artist        string                  artist name
    RETURN 0 or year as a int
    """
    # case where we have no musicbrainz_id for the artist
    if artist_mbid is None or artist_mbid == '':
        return find_year_safemode_nombid(connect,title,release,artist)
    q = "SELECT artist id FROM artist WHERE gid='"+artist_mbid+"'"
    res = connect.query(q)
    if len(res.getresult()) == 0: # mb does not know that ID... yes it happens
        return find_year_safemode_nombid(connect,title,release,artist)
    # find all album release dates from albums from tracks that match artist, title, and release
    # i.e. we take all the tracks found in the previous query, check their album names
    # and if an album name matches 'release', we take its release date
    # if more than one match, take earliest year
    # CHECK commented lines if you also want to return the track.id
    q = "SELECT min(release.releasedate) FROM track INNER JOIN artist"
    #q = "SELECT release.releasedate,track.gid FROM track INNER JOIN artist"
    q += " ON artist.gid='"+artist_mbid+"' AND artist.id=track.artist"
    q += " AND lower(track.name)="+encode_string(title.lower())
    q += " INNER JOIN albumjoin ON albumjoin.track=track.id"
    q += " INNER JOIN album ON album.id=albumjoin.album"
    q += " INNER JOIN release ON release.album=album.id"
    q += " AND release.releasedate!='0000-00-00' LIMIT 1"
    #q += " AND release.releasedate!='0000-00-00' ORDER BY release.releasedate LIMIT 1"
    res = connect.query(q)
    if not res.getresult()[0][0] is None:
        return int(res.getresult()[0][0].split('-')[0])
    # we relax the condition that we have to find an exact string match for the title
    # if we find the good album name (our 'release' param)
    #q = "SELECT min(release.releasedate) FROM artist INNER JOIN album"
    q = "SELECT min(release.releasedate) FROM artist INNER JOIN album"
    q += " ON artist.gid='"+artist_mbid+"' AND artist.id=album.artist"
    q += " AND lower(album.name)="+encode_string(release.lower())
    q += " INNER JOIN release ON release.album=album.id"
    q += " AND release.releasedate!='0000-00-00' LIMIT 1"
    res = connect.query(q)
    if not res.getresult()[0][0] is None:
        return int(res.getresult()[0][0].split('-')[0])
    # not found
    return 0


def find_year_safemode_nombid(connect,title,release,artist):
    """
    We try to get a year for a particular track without musicbrainz id
    for the artist.
    We get only if we have a perfect match either for (artist_name / title)
    or (artist_name / release)
    RETURN 0 if not found, or year as int
    """
    # find all albums based on tracks found by exact track title match
    # return the earliest release year of one of these albums
    q = "SELECT min(release.releasedate) FROM track INNER JOIN artist"
    q += " ON lower(artist.name)="+encode_string(artist.lower())+" AND artist.id=track.artist"
    q += " AND lower(track.name)="+encode_string(title.lower())
    q += " INNER JOIN albumjoin ON albumjoin.track=track.id"
    q += " INNER JOIN album ON album.id=albumjoin.album"
    q += " INNER JOIN release ON release.album=album.id"
    q += " AND release.releasedate!='0000-00-00' LIMIT 1"
    res = connect.query(q)
    if not res.getresult()[0][0] is None:
        return int(res.getresult()[0][0].split('-')[0])    
    # we relax the condition that we have to find an exact string match for the title
    # if we find the good album name (our 'release' param)
    q = "SELECT min(release.releasedate) FROM artist INNER JOIN album"
    q += " ON lower(artist.name)="+encode_string(artist.lower())+" AND artist.id=album.artist"
    q += " AND lower(album.name)="+encode_string(release.lower())
    q += " INNER JOIN release ON release.album=album.id"
    q += " AND release.releasedate!='0000-00-00' LIMIT 1"
    res = connect.query(q)
    if not res.getresult()[0][0] is None:
        return int(res.getresult()[0][0].split('-')[0])
    # not found
    return 0


def get_artist_tags(connect, artist_mbid, maxtags=20):
    """
    Get the musicbrainz tags and tag count given a musicbrainz
    artist. Returns two list of length max 'maxtags'
    Always return two lists, eventually empty
    """
    if artist_mbid is None or artist_mbid == '':
        return [],[]
    # find all tags
    q = "SELECT tag.name,artist_tag.count FROM artist"
    q += " INNER JOIN artist_tag ON artist.id=artist_tag.artist"
    q += " INNER JOIN tag ON tag.id=artist_tag.tag"
    q += " WHERE artist.gid='"+artist_mbid+"'"
    q += " ORDER BY count DESC LIMIT "+str(maxtags)
    res = connect.query(q)
    if len(res.getresult()) == 0:
        return [],[]
    return map(lambda x: x[0],res.getresult()),map(lambda x: x[1],res.getresult())


def debug_from_song_file(connect,h5path,verbose=0):
    """
    Slow debugging function that takes a h5 file, reads the info,
    check the match with musicbrainz db, prints out the result.
    Only prints when we dont get exact match!
    RETURN counts of how many files we filled for years, tags
    """
    import hdf5_utils as HDF5
    import hdf5_getters as GETTERS
    h5 = HDF5.open_h5_file_read(h5path)
    title = GETTERS.get_title(h5)
    release = GETTERS.get_release(h5)
    artist = GETTERS.get_artist_name(h5)
    ambid = GETTERS.get_artist_mbid(h5)
    h5.close()
    # mbid
    gotmbid=1
    if ambid=='':
        gotmbid = 0
        if verbose>0: print 'no mb id for:',artist
    # year
    year = find_year_safemode(connect,ambid,title,release,artist)
    gotyear = 1 if year > 0 else 0
    if verbose>0: print 'no years for:',artist,'|',release,'|',title
    # tags
    tags,counts = get_artist_tags(connect,ambid)
    gottags = 1 if len(tags) > 0 else 0
    if gottags == 0 and verbose>0: print 'no tags for:',artist
    # return indicator for mbid, year, tag
    return gotmbid,gotyear,gottags


def die_with_usage():
    """ HELP MENU """
    print 'This contains library functions to query the musicbrainz database'
    print 'For debugging:'
    print '    python query.py -hdf5 <list of songs>'
    print '    e.g. python query.py -hdf5 MillionSong/A/A/*/*.h5'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # DEBUGGING
    verbose=0
    while True:
        if sys.argv[1]=='-verbose':
            verbose=1
        else:
            break
        sys.argv.pop(1)
    
    if sys.argv[1] == '-hdf5':
        import time
        import datetime
        sys.path.append( os.path.abspath('..') )
        connect = connect_mbdb()
        paths = sys.argv[2:]
        t1 = time.time()
        cntmbid = 0
        cntyears = 0
        cnttags = 0
        for p in paths:
            mbid,year,tag = debug_from_song_file(connect,p,verbose=verbose)
            cntmbid += mbid
            cntyears += year
            cnttags += tag
        connect.close()
        t2 = time.time()
        stimelength = str(datetime.timedelta(seconds=t2-t1))
        print 'has musicbrainz id for',cntmbid,'out of',len(paths)
        print 'found years for',cntyears,'out of',len(paths)
        print 'found tags for',cnttags,'out of',len(paths)
        print 'all done in',stimelength
        sys.exit(0)


