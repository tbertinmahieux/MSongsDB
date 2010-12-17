"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code is more of a sanitcy checks, it counts how many
leaves there are in the filesystem for the million songs,
thus making sure the track ID's are well-balance.
Also try to find the most recent files, in case we have
to delete some at the end.

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
from Queue import PriorityQueue # from queue for Python 3.0


# put in tuples likes -modifdate, fname
# highest priority = lowest first number
MODIFQUEUE = PriorityQueue()



def get_all_files(basedir,ext='.h5') :
    """
    From a root directory, go through all subdirectories
    and find all files with the given extension.
    Return all absolute paths in a list.
    """
    allfiles = []
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files :
            allfiles.append( os.path.abspath(f) )
    return allfiles


def count_normal_leaves(basedir):
    """
    Count how many directories are of the form
    basedir/A/B/C
    """
    cnt = 0
    for root, dirs, files in os.walk(basedir):
        level3up = os.path.abspath(os.path.join(root,'../../..'))
        if os.path.exists(level3up) and os.path.samefile(level3up,basedir):
            cnt += 1
    return cnt

def get_all_files_modif_date(basedir,ext='.5'):
    """
    From a root directory, look at all the file,
    get their last modification date, put in in priority
    queue so the most recent file pop up first
    """
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files :
            mdate = file_modif_date(f)
            MODIFQUEUE.put_nowait( (-mdate,f) )


def file_modif_date(f):
    """ return modif date in seconds (as in time.time()) """
    return os.stat(f).st_mtime


def die_with_usage():
    """ HELP MENU """
    print 'dataset_filestats.py'
    print '   by T. Bertin-Mahieux (2010) Columbia University'
    print '      tb2332@columbia.edu'
    print 'Simple util to check the file repartition and the most'
    print 'recent file in the Million Song dataset directory'
    print 'usage:'
    print '   python dataset_filestats.py <maindir>'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    maindir = sys.argv[1]

    # number of leaves
    n_leaves = count_normal_leaves(maindir)
    print 'got',n_leaves,'out of',26*26*26
