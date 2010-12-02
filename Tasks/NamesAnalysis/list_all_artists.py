"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code contains code to parse the dataset and list
all artists. It can either be used as a library, or
as a standalone if we want the result to be output to a file.

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


def get_artistid_trackid_artistname(trackfile):
    """
    Utility function, opens a h5 file, gets the 3 following fields:
     - artist Echo Nest ID
     - track Echo Nest ID
     - artist name
    It is returns as a triple (,,)
    """


def list_all(maindir):
    """
    Goes through all subdirectories, open every song file,
    and list all artists it finds.
    It returns a dictionary of string -> tuples:
       artistID -> (trackID, artist_name)
    The track ID is random, i.e. the first one we find for that
    artist. The artist information should be the same in all track
    files from that artist.
    INPUT
      maindir  - top directory of the dataset, we will parse all
                 subdirectories for .h5 files
    RETURN
      dictionary that maps artist ID to tuple (track ID, artist name)
    """
    raise NotImplementedError


def die_with_usage():
    """ HELP MENU """
    print 'list_all_artists.py'
    print '   by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'usage:'
    print '  python list_all_artists.py <DATASET DIR> output.txt'
    print ''
    print 'This code lets you list all artists contained in all'
    print 'subdirectories of a given directory.'
    print 'This script puts the result in a text file, but its main'
    print 'function can be used by other codes.'
    print 'The txt file format is: (we use <SEP> as separator symbol):'
    print 'artist Echo Nest ID<SEP>one track Echo Nest ID<SEP>artist name'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    maindir = sys.argv[1]
    output = sys.argv[2]

    # sanity checks
    if not os.path.isdir(maindir):
        print maindir,'is not a directory'
        sys.exit(0)
    if os.path.isfile(output):
        print 'output file:',output,'exists, please delete or choose new one'
        sys.exit(0)

    




