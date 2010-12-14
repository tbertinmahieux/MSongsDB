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
import copy
import time
import datetime
import multiprocessing
import numpy as np
try:
    import hdf5_utils as HDF5
except ImportError:
    pass # will be imported in command line



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

# error passing problems
class KeyboardInterruptError(Exception):pass

# wrapper
def sanity_check_1thread_wrapper(args):
    """ wrapper for multiprocessing to call the real function """
    sanity_check_1thread(**args)

# actual function
def sanity_check_1thread(maindir=None,threadid=-1,nthreads=-1,allfiles=[]):
    """
    Main function, check a bunch of files by opening every field in
    getter.
    """
    assert not maindir is None,'wrong param maindir'
    assert threadid>-1,'wrong param threadid'
    assert nthreads>0,'wrong param nthreads'
    assert len(allfiles)>0,'wrong param allfiles, or no files'
    # get getters
    getters = filter(lambda x: x[:4] == 'get_', GETTERS.__dict__.keys())
    # get the files to check
    files_per_thread = int(np.ceil(len(allfiles) * 1. / nthreads))
    p1 = files_per_thread * threadid
    p2 = min(len(allfiles),files_per_thread * (threadid+1))
    # iterate over files between p1 and p2
    for f in allfiles[p1:p2]:
        try:
            h5 = GETTERS.open_h5_file_read(f)
            for getter in getters:
                tmp = GETTERS.__getattribute__(getter)(h5)
        except KeyboardInterrupt:
            raise KeyboardInterruptError()
        except Exception,e:
            print 'PROBLEM WITH FILE:',f; sys.stdout.flush()
            raise
        finally:
            h5.close()
    # done, all fine
    return


def die_with_usage():
    """ HELP MENU """
    print 'dataset_sanity_check.py'
    print '  by T. Bertin-Mahieux (2010) Columbia University'
    print '     tb2332@columbia.edu'
    print 'do a simple but full sanity check on the dataset'
    print 'GOAL: read every field of every file to make sure nothing'
    print '      is corrupted'
    print 'usage:'
    print '  python dataset_sanity_check.py -nthreads N <main dir>'
    print 'PARAMS:'
    print '  main dir      - Million Song Dataset root directory'
    print 'FLAGS:'
    print '  -nthreads N   - number of threads, default 1'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # local imports
    sys.path.append(os.path.abspath(os.path.join(sys.argv[0],'../..')))
    import hdf5_getters as GETTERS

    # flags
    nthreads = 1
    while True:
        if sys.argv[1] == '-nthreads':
            nthreads = int(sys.argv[2])
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # params
    maindir = sys.argv[1]

    # count files
    allfiles = get_all_files(maindir,ext='.h5')
    nfiles = len(allfiles)
    print 'we found',nfiles,'files.'
    if nfiles != 1000000:
        print 'WATCHOUT! NOT A MILLION FILES'
    allfiles = sorted(allfiles)
    
    # create args for the threads
    params_list = []
    for k in range(nthreads):
        params = {'maindir':maindir,'allfiles':allfiles,
                  'threadid':k,'nthreads':nthreads}
        params_list.append(params)

    # start time
    t1 = time.time()

    # launch the processes
    got_probs = False
    pool = multiprocessing.Pool(processes=nthreads)
    try:
        pool.map(sanity_check_1thread_wrapper, params_list)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print 'MULTIPROCESSING'
        print 'stopping multiprocessing due to a keyboard interrupt'
        pool.terminate()
        pool.join()
    except Exception, e:
        print 'MULTIPROCESSING'
        print 'got exception: %r, terminating the pool' % (e,)
        pool.terminate()
        pool.join()
        got_probs = True
    
    # end time
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    if not got_probs:
        print 'ALL DONE, no apparent problem'
    print 'execution time:', stimelength
