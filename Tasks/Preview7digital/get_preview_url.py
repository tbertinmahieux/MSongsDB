"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code uses 7digital API and info contained in HDF5 song
file to get a preview URL.

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
import urllib2
from xml.dom import minidom

# Million Song Dataset imports, works under Linux
# otherwise, put the PythonSrc directory in the PYTHONPATH!
pythonsrc = os.path.abspath('__file__')
pythonsrc = os.path.join(pythonsrc,'../../../PythonSrc')
pythonsrc = os.path.abspath( pythonsrc )
sys.path.append( pythonsrc )
import hdf5_utils
import hdf5_getters as GETTERS

# try to get 7digital API key
global DIGITAL7_API_KEY
try:
    DIGITAL7_API_KEY = os.environ['DIGITAL7_API_KEY']
except KeyError:
    DIGITAL7_API_KEY = None



def url_call(url):
    """
    Do a simple request to the 7digital API
    We assume we don't do intense querying, this function is not
    robust
    Return the answer as na xml document
    """
    stream = urllib2.urlopen(url)
    xmldoc = minidom.parse(stream).documentElement
    stream.close()
    return xmldoc

    
def get_link_from_xml(xmldoc):
    """
    After calling the API, we get an XML response that looks like:
    
    <response status="ok" version="1.2" xsi:noNamespaceSchemaLocation="http://api.7digital.com/1.2/static/7digitalAPI.xsd">
      <url>
        http://previews.7digital.com/clips/34/6804688.clip.mp3
      </url>
    </response>

    We parse it for the URL that we return, or '' if a problem
    """
    status = xmldoc.getAttribute('status')
    if status != 'ok':
        return ''
    urlelem = xmldoc.getElementsByTagName('url')[0]
    preview = urlelem.firstChild.nodeValue
    return preview


def die_with_usage():
    """ HELP MENU """
    print 'get_preview_url.py'
    print '    by T. Bertin-Mahieux (2010) Columbia University'
    print 'HELP MENU'
    print 'usage:'
    print '    python get_preview_url.py [FLAG] <SONGFILE>'
    print 'PARAMS:'
    print '  <SONGFILE>  - a Million Song Dataset file TRABC...123.h5'
    print 'FLAGS:'
    print '  -7digitalkey KEY - API key from 7 digital, we recomment you put it'
    print '                     under environment variable: DIGITAL7_API_KEY'
    print 'OUTPUT:'
    print '  url from 7digital that should play a clip of the song.'
    print '  No guarantee that this is the exact audio used for the analysis'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # flags
    while True:
        if sys.argv[1] == '-7digitalkey':
            DIGITAL7_API_KEY = sys.argv[2]
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # params
    h5path = sys.argv[1]

    # sanity checks
    if DIGITAL7_API_KEY is None:
        print 'You need to set a 7digital API key!'
        print 'Get one at: http://developer.7digital.net/'
        print 'Pass it as a flag: -7digitalkey KEY'
        print 'or set it under environment variable: DIGITAL7_API_KEY'
        sys.exit(0)
    if not os.path.isfile(h5path):
        print 'invalid path (not a file):',h5path
        sys.exit(0)


    # open h5 song, get all we know about the song
    h5 = hdf5_utils.open_h5_file_read(h5path)
    track_7digitalid = GETTERS.get_track_7digitalid(h5)
    release_7digitalid = GETTERS.get_release_7digitalid(h5)
    artist_7digitalid = GETTERS.get_artist_7digitalid(h5)
    artist_name = GETTERS.get_artist_name(h5)
    release_name = GETTERS.get_release(h5)
    track_name = GETTERS.get_title(h5)
    h5.close()

    # use all this information to create the best query we can
    if track_7digitalid >= 0:
        url = 'http://api.7digital.com/1.2/track/preview?redirect=false'
        url += '&trackid='+str(track_7digitalid)
        url += '&oauth_consumer_key='+DIGITAL7_API_KEY
        #print url_call(url)
        xmldoc = url_call(url)
        preview = get_link_from_xml(xmldoc)
        if preview == '':
            print 'something went wrong'
        else:
            print preview
        sys.exit(0)

    else:
        print 'for the moment, work only if we have an actual 7api track id'
