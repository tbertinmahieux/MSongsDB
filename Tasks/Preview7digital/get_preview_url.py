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

# Million Song Dataset imports, works under Linux
# otherwise, put the PythonSrc directory in the PYTHONPATH!
pythonsrc = os.path.abspath('__file__')
pythonsrc = os.path.join(pythonsrc,'../../PythonSrc')
sys.path.append( os.path.abspath( pythonsrc ) )

# try to get 7digital API key
try:
    DIGITAL7_API_KEY = os.environ['DIGITAL7_API_KEY']
except KeyError:
    DIGITAL7_API_KEY = None




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
    global DIGITAL7_API_KEY
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
