"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

To test MusicBrainz
Similar than the python-musicbrainz2 example, except that we
call a local instance of the musicbrainz database instead.

Copyright 2010, Thierry Bertin-Mahieux
Original code part of python-musicbrainz2 package

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


import sys
import logging
import musicbrainz2.webservice as ws
import musicbrainz2.model as m

_local_host = 'thierry-laptop'
_local_port = 3000
_local_path_prefix = ''
_local_version = '' # default '1'

def die_with_usage():
    print "Usage: getartist.py artist-id"
    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        die_with_usage()

    # create query, use local instance of MusicBrainz db
    webservice = ws.WebService(host=_local_host,port=_local_port,
                               pathPrefix=_local_path_prefix,
                               username=None,
                               password=None,
                               realm='musicbrainz.org',
                               opener=None)
    # create query object
    q = ws.Query(ws=webservice)
    # DEBUG URL
    #url = q._ws._makeUrl(entity,id_)
    url = q._ws._makeUrl('artist',sys.argv[1])
    print 'url =',url

    try:
	# The result should include all official albums.
	#
	inc = ws.ArtistIncludes(
		releases=(m.Release.TYPE_OFFICIAL, m.Release.TYPE_ALBUM),
		tags=True, releaseGroups=True)
	artist = q.getArtistById(sys.argv[1], inc)
    except ws.WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


    print "Id         :", artist.id
    print "Name       :", artist.name
    print "SortName   :", artist.sortName
    print "UniqueName :", artist.getUniqueName()
    print "Type       :", artist.type
    print "BeginDate  :", artist.beginDate
    print "EndDate    :", artist.endDate
    print "Tags       :", ', '.join([t.value for t in artist.tags])
    print

    if len(artist.getReleases()) == 0:
	print "No releases found."
    else:
	print "Releases:"

    for release in artist.getReleases():
	print
	print "Id        :", release.id
	print "Title     :", release.title
	print "ASIN      :", release.asin
	print "Text      :", release.textLanguage, '/', release.textScript
	print "Types     :", release.types

    print

    if len(artist.getReleaseGroups()) == 0:
	print
	print "No release groups found."
    else:
	print
	print "Release groups:"

    for rg in artist.getReleaseGroups():
	print
	print "Id        :", rg.id
	print "Title     :", rg.title
	print "Type      :", rg.type

    print

#
# Using the release IDs and Query.getReleaseById(), you could now request 
# those releases, including the tracks, release events, the associated
# DiscIDs, and more. The 'getrelease.py' example shows how this works.
#


