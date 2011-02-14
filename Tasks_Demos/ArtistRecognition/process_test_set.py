"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Code to parse the whole testing set using a trained KNN
and predict an artist.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.

Copyright (c) 2011, Thierry Bertin-Mahieux, All Rights Reserved

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
import copy
import tables
import sqlite3
import datetime
import multiprocessing
import numpy as np
from operator import itemgetter
import hdf5_getters as GETTERS
import process_train_set as TRAIN # for the features
try:
    import scikits.ann as ANN
except ImportError:
    print 'you need scikits.ann: http://www.scipy.org/scipy/scikits/wiki/AnnWrapper'
    sys.exit(0)
    
# error passing problems, useful for multiprocessing
class KeyboardInterruptError(Exception):pass

def fullpath_from_trackid(maindir,trackid):
    """ Creates proper file paths for song files """
    p = os.path.join(maindir,trackid[2])
    p = os.path.join(p,trackid[3])
    p = os.path.join(p,trackid[4])
    p = os.path.join(p,trackid+'.h5')
    return str(p)

def get_all_files(basedir,ext='.h5'):
    """
    From a root directory, go through all subdirectories
    and find all files with the given extension.
    Return all absolute paths in a list.
    """
    allfiles = []
    apply_to_all_files(basedir,func=lambda x: allfiles.append(x),ext=ext)
    return allfiles


def apply_to_all_files(basedir,func=lambda x: x,ext='.h5'):
    """
    From a root directory, go through all subdirectories
    and find all files with the given extension.
    Apply the given function func
    If no function passed, does nothing and counts file
    Return number of files
    """
    cnt = 0
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files :
            func(f)
            cnt += 1
    return cnt


def compute_features(h5):
    """
    Get the same features than during training
    """
    return TRAIN.compute_features(h5)
    

def do_prediction(processed_feats,kd,h5model,K=1):
    """
    Receive processed features from test set, apply KNN,
    return an actual predicted year (float)
    INPUT
       processed_feats - extracted from a test song
                    kd - ANN kdtree on top of model
               h5model - open h5 file with data.feats and data.year
                     K - K-nn parameter
    """
    res = kd.knn(processed_feats,K)
    if K == 1:
        index = res[0][0]
        pred_artist_id = h5model.root.data.artist_id[index]
    else:
        # find artist with most results
        # if tie, the one that was the highest ranking wins
        indices = res[0].flatten()
        artists = {}
        for pos,i in enumerate(indices):
            artist_id = h5model.root.data.artist_id[i]
            if not artist_id in artists.keys():
                artists[artist_id] = [1,-pos]
            else:
                artists[artist_id][0] += 1
        tuples = zip(artists.keys(),artists.values())
        res = sorted(tuples,key=itemgetter(1),reverse=True)
        pred_artist_id = res[0][0]
    # done
    return pred_artist_id
    

def process_filelist_test(filelist=None,model=None,tmpfilename=None,K=1):
    """
    Main function, process all files in the list (as long as their track_id
    is not in testsongs)
    INPUT
       filelist     - a list of song files
       model        - h5 file containing feats and artist_id for all train songs
       tmpfilename  - where to save our processed features
       K            - K-nn parameter (default=1)
    """
    # sanity check
    for arg in locals().values():
        assert not arg is None,'process_filelist_train, missing an argument, something still None'
    if os.path.isfile(tmpfilename):
        print 'ERROR: file',tmpfilename,'already exists.'
        return
    if not os.path.isfile(model):
        print 'ERROR: model',model,'does not exist.'
        return
    # dimension fixed (12-dimensional timbre vector)
    ndim = 12
    finaldim = 90
    # create kdtree
    h5model = tables.openFile(model, mode='r')
    assert h5model.root.data.feats.shape[1]==finaldim,'inconsistency in final dim'
    kd = ANN.kdtree(h5model.root.data.feats)
    # create outputfile
    output = tables.openFile(tmpfilename, mode='a')
    group = output.createGroup("/",'data','TMP FILE FOR ARTIST RECOGNITION')
    output.createEArray(group,'artist_id_real',tables.StringAtom(18,shape=()),(0,),'',
                        expectedrows=len(filelist))
    output.createEArray(group,'artist_id_pred',tables.StringAtom(18,shape=()),(0,),'',
                        expectedrows=len(filelist))
    # iterate over files
    cnt_f = 0
    for f in filelist:
        cnt_f += 1
        # verbose
        if cnt_f % 50000 == 0:
            print 'training... checking file #',cnt_f
        # check what file/song is this
        h5 = GETTERS.open_h5_file_read(f)
        artist_id = GETTERS.get_artist_id(h5)
        track_id = GETTERS.get_track_id(h5)
        if track_id in testsongs: # just in case, but should not be necessary
            print 'Found test track_id during training? weird.',track_id
            h5.close()
            continue
        # extract features, then close file
        processed_feats = compute_features(h5)
        h5.close()
        if processed_feats is None:
            continue
        # do prediction
        artist_id_pred = do_prediction(processed_feats,kd,h5model,K)
        # save features to tmp file
        output.root.data.artist_id_real.append( np.array( [artist_id] ) )
        output.root.data.artist_id_pred.append( np.array( [artist_id_pred] ) )
    # we're done, close output
    output.close()
    return

            
def process_filelist_test_wrapper(args):
    """ wrapper function for multiprocessor, calls process_filelist_test """
    try:
        process_filelist_test(**args)
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


def process_filelist_test_main_pass(nthreads,model,testsongs,K):
    """
    Do the main walk through the data, deals with the threads,
    creates the tmpfiles.
    INPUT
      - nthreads     - number of threads to use
      - model        - h5 files containing feats and artist_id for all train songs
      - testsongs    - set of songs to ignore
      - K            - K-nn parameter
    RETURN
      - tmpfiles     - list of tmpfiles that were created
                       or None if something went wrong
    """
    # sanity checks
    assert nthreads >= 0,'Come on, give me at least one thread!'
    # prepare params for each thread
    params_list = []
    default_params = {'model':model,'K':K}
    tmpfiles_stub = 'mainpasstest_artistrec_tmp_output_'
    tmpfiles = map(lambda x: os.path.join(os.path.abspath('.'),tmpfiles_stub+str(x)+'.h5'),range(nthreads))
    nfiles_per_thread = int(np.ceil(len(testsongs) * 1. / nthreads))
    for k in range(nthreads):
        # params for one specific thread
        p = copy.deepcopy(default_params)
        p['tmpfilename'] = tmpfiles[k]
        p['filelist'] = testsongs[k*nfiles_per_thread:(k+1)*nfiles_per_thread]
        params_list.append(p)
    # launch, run all the jobs
    pool = multiprocessing.Pool(processes=nthreads)
    try:
        pool.map(process_filelist_test_wrapper, params_list)
        pool.close()
        pool.join()
    except KeyboardInterruptError:
        print 'MULTIPROCESSING'
        print 'stopping multiprocessing due to a keyboard interrupt'
        pool.terminate()
        pool.join()
        return None
    except Exception, e:
        print 'MULTIPROCESSING'
        print 'got exception: %r, terminating the pool' % (e,)
        pool.terminate()
        pool.join()
        return None
    # all done!
    return tmpfiles


def test(nthreads,model,testsongs,K):
    """
    Main function to do the training
    Do the main pass with the number of given threads.
    Then, reads the tmp files, creates the main output, delete the tmpfiles.
    INPUT
      - nthreads     - number of threads to use
      - model        - h5 files containing feats and artist_id for all train songs
      - testsongs    - set of songs to ignore
      - K            - K-nn parameter
    RETURN
       - nothing :)
    """
    # initial time
    t1 = time.time()
    # do main pass
    tmpfiles = process_filelist_test_main_pass(nthreads,model,testsongs,K)
    if tmpfiles is None:
        print 'Something went wrong, tmpfiles are None'
        return
    # intermediate time
    t2 = time.time()
    stimelen = str(datetime.timedelta(seconds=t2-t1))
    print 'Main pass done after',stimelen; sys.stdout.flush()
    # aggregate temp files
    artist_id_found = 0
    total_predictions = 0
    for tmpf in tmpfiles:
        h5 = tables.openFile(tmpf)
        for k in range( h5.root.data.artist_id_real.shape[0] ):
            total_predictions += 1
            if h5.root.data.artist_id_real[k] == h5.root.data.artist_id_pred[k]:
                artist_id_found += 1
        h5.close()
        # delete tmp file
        os.remove(tmpf)
    # final time
    t3 = time.time()
    stimelen = str(datetime.timedelta(seconds=t3-t1))
    print 'Whole testing done after',stimelen
    # results
    print 'We found the right artist_id',artist_id_found,'times out of',total_predictions,'predictions.'
    print 'e.g., accuracy is:',artist_id_found*1./total_predictions
    # done
    return


def die_with_usage():
    """ HELP MENU """
    print 'process_test_set.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print 'Code to perform artist recognition on the Million Song Dataset.'
    print 'This performs the evaluation of a trained KNN model.'
    print 'REQUIRES ANN LIBRARY and its python wrapper.'
    print 'USAGE:'
    print '  python process_test_set.py [FLAGS] <MSD_DIR> <model> <testsongs> <tmdb>'
    print 'PARAMS:'
    print '        MSD_DIR  - main directory of the MSD dataset'
    print '          model  - h5 file where the training is saved'
    print '      testsongs  - file containing test songs (to ignore)'
    print '           tmdb  - path to track_metadata.db'
    print 'FLAGS:'
    print '           -K n  - K-nn parameter (default=1)'
    print '    -nthreads n  - number of threads to use (default: 1)'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 5:
        die_with_usage()

    # flags
    nthreads = 1
    K = 1
    while True:
        if sys.argv[1] == '-nthreads':
            nthreads = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-K':
            K = int(sys.argv[2])
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # params
    msd_dir = sys.argv[1]
    model = sys.argv[2]
    testsongs = sys.argv[3]
    tmdb = sys.argv[4]

    # sanity check
    assert os.path.isdir(msd_dir),'ERROR: dir '+msd_dir+' does not exist.'
    assert os.path.isfile(testsongs),'ERROR: file '+testsongs+' does not exist.'
    assert os.path.isfile(model),'ERROR: file '+model+' does not exist.'
    assert os.path.isfile(tmdb),'ERROR: file '+tmdb+' does not exist.'

    # read test artists
    if not os.path.isfile(testsongs):
        print 'ERROR:',testsongs,'does not exist.'
        sys.exit(0)
    testsongs_set = set()
    f = open(testsongs,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        testsongs_set.add( line.strip().split('<SEP>')[0] )
    f.close()
    testsongs_list = map(lambda x: fullpath_from_trackid(msd_dir,x), testsongs_set)

    # settings
    print 'msd dir:',msd_dir
    print 'testsongs:',testsongs,'('+str(len(testsongs_set))+' songs)'
    print 'tmdb:',tmdb
    print 'nthreads:',nthreads
    print 'K:',K

    # launch testing
    test(nthreads,model,testsongs_list,K)

    # done
    print 'DONE!'
