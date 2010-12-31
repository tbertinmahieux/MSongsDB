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
import time
import glob
try:
    from Queue import PriorityQueue # from queue for Python 3.0
except ImportError:
    from queue import PriorityQueue # Python 3.0

# put in tuples likes -modifdate, fname
# highest priority = lowest first number
MODIFQUEUE = PriorityQueue()

# list of leaves ordered by number of files
# get filled up when we count leaves (by default)
MAP_NFILES_DIR = {}


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


def count_normal_leaves(basedir,revindex=True):
    """
    Count how many directories are of the form
    basedir/A/B/C
    If revindex, we fill up MAP_NFILES_DIR where
    the keys are number of files, and the value is
    a set of directory filenames
    """
    cnt = 0
    for root, dirs, files in os.walk(basedir):
        level3up = os.path.abspath(os.path.join(root,'../../..'))
        if os.path.exists(level3up) and os.path.samefile(level3up,basedir):
            cnt += 1
            if revindex:
                nfiles = len(glob.glob(os.path.join(root,'*.h5')))
                if not nfiles in MAP_NFILES_DIR.keys():
                    MAP_NFILES_DIR[nfiles] = set()
                MAP_NFILES_DIR[nfiles].add(root)
    return cnt

def get_all_files_modif_date(basedir,ext='.h5'):
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

    trimdryrun = False
    trim = False
    while True:
        if sys.argv[1] == '-trimdryrun':
            trimdryrun = True
            trim = False
        elif sys.argv[1] == '-trim':
            if trimdryrun:
                pass
            else:
                trim = True
                print 'WE TRIM FOR REAL!!!!'
        else:
            break
        sys.argv.pop(1)

    maindir = sys.argv[1]

    # number of leaves
    n_leaves = count_normal_leaves(maindir)
    print '******************************************************'
    print 'got',n_leaves,'leaves out of',26*26*26,'possible ones.'

    # empty and full leaves
    print '******************************************************'
    min_nfiles = min(MAP_NFILES_DIR.keys())
    print 'most empty leave(s) have',min_nfiles,'files, they are:'
    print MAP_NFILES_DIR[min_nfiles]
    max_nfiles = max(MAP_NFILES_DIR.keys())
    print 'most full leave(s) have',max_nfiles,'files, they are:'
    print MAP_NFILES_DIR[max_nfiles]
    nfiles = 0
    for k in MAP_NFILES_DIR:
        nfiles += k * len(MAP_NFILES_DIR[k])
    print 'we found',nfiles,'files in total'
    print 'average number of files per leaf:',nfiles * 1. / n_leaves

    # tmp files
    ntmpfiles = len( get_all_files(maindir,ext='.h5_tmp') )
    print 'we found',ntmpfiles,'temp files'
    if ntmpfiles > 0: print 'WATCHOUT FOR TMP FILES!!!!'

    # find modif date for all files, and pop out the most recent ones
    get_all_files_modif_date(maindir)
    print '******************************************************'
    if not trim and not trimdryrun:
        print 'most recent files are:'
        for k in range(5):
            t,f = MODIFQUEUE.get_nowait()
            print f,'(',time.ctime(-t),')'
    elif trim or trimdryrun:
        ntoomany = nfiles - 1000000
        print 'we have',ntoomany,'too many files.'
        for k in range(ntoomany):
            t,f = MODIFQUEUE.get_nowait()
            print f,'(',time.ctime(-t),')'
            if trim:
                os.remove(f)
    # done
    print '******************************************************'
