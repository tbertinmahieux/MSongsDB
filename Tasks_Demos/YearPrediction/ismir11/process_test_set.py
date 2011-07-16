"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Code to go through the test set, get a summary of the features
(the same as for train set) and predict year using KNN.

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

# path to the YearRecognition folder in the Million Song Dataset
# project, if not in PYTHONPATH
YEAR_REC_FOLDERS=['/home/thierry/Columbia/MSongsDB/Tasks_Demos/YearPrediction','/home/empire6/thierry/MSongsDB/Tasks_Demos/YearPrediction']

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
import hdf5_getters as GETTERS
import compress_feat as CBTF
import year_pred_benchmark as BENCHMARK
import randproj as RANDPROJ
for p in YEAR_REC_FOLDERS:
    sys.path.append(p)
from beat_aligned_feats import get_bttimbre
try:
    import scikits.ann as ANN
except ImportError:
    print 'you need scikits.ann: http://www.scipy.org/scipy/scikits/wiki/AnnWrapper'
    sys.exit(0)


class KeyboardInterruptError(Exception):pass


def fullpath_from_trackid(maindir,trackid):
    p = os.path.join(maindir,trackid[2])
    p = os.path.join(p,trackid[3])
    p = os.path.join(p,trackid[4])
    p = os.path.join(p,trackid+'.h5')
    return str(p)


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
    # we take the average for all K, all picks
    indexes = res[0].flatten()
    years = map(lambda x: h5model.root.data.year[x], indexes)
    pred_year = np.average(years)
    if np.isnan(pred_year):
        print 'PROBLEM! we got NaN from years:',years
        print 'Processed feats had NaN?',np.isnan(processed_feats).any()
        print 'processed_feats.shape=',processed_feats.shape
        print 'feats=',processed_feats
        return None
    # done (maybe we should return more info...?
    return pred_year


def process_filelist_test(filelist=None,model=None,tmpfilename=None,
                           npicks=None,winsize=None,finaldim=None,K=1,
                          typecompress='picks'):
    """
    Main function, process all files in the list (as long as their artist
    is in testartist)
    INPUT
       filelist     - a list of song files
       model        - h5 file containing feats and year for all train songs
       tmpfilename  - where to save our processed features
       npicks       - number of segments to pick per song
       winsize      - size of each segment we pick
       finaldim     - how many values do we keep
       K            - param of KNN (default 1)
       typecompress - feature type, 'picks', 'corrcoeff' or 'cov'
                      must be the same as in training
    """
    # sanity check
    for arg in locals().values():
        assert not arg is None,'process_filelist_test, missing an argument, something still None'
    if os.path.isfile(tmpfilename):
        print 'ERROR: file',tmpfilename,'already exists.'
        return
    if not os.path.isfile(model):
        print 'ERROR: model',model,'does not exist.'
        return
    # create kdtree
    h5model = tables.openFile(model, mode='r')
    assert h5model.root.data.feats.shape[1]==finaldim,'inconsistency in final dim'
    kd = ANN.kdtree(h5model.root.data.feats)
    # create outputfile
    output = tables.openFile(tmpfilename, mode='a')
    group = output.createGroup("/",'data','TMP FILE FOR YEAR RECOGNITION')
    output.createEArray(group,'year_real',tables.IntAtom(shape=()),(0,),'',
                        expectedrows=len(filelist))
    output.createEArray(group,'year_pred',tables.Float64Atom(shape=()),(0,),'',
                        expectedrows=len(filelist))
    # random projection
    ndim = 12 # fixed in this dataset
    if typecompress == 'picks':
        randproj = RANDPROJ.proj_point5(ndim * winsize, finaldim)
    elif typecompress == 'corrcoeff' or typecompress=='cov':
        randproj = RANDPROJ.proj_point5(ndim * ndim, finaldim)
    elif typecompress == 'avgcov':
        randproj = RANDPROJ.proj_point5(90, finaldim)
    else:
        assert False,'Unknown type of compression: '+str(typecompress)
    # go through files
    cnt_f = 0
    for f in filelist:
        cnt_f += 1
        if cnt_f % 5000 == 0:
            print 'TESTING FILE #'+str(cnt_f)
        # check file
        h5 = GETTERS.open_h5_file_read(f)
        artist_id = GETTERS.get_artist_id(h5)
        year = GETTERS.get_year(h5)
        track_id = GETTERS.get_track_id(h5)
        h5.close()
        if year <= 0: # probably useless but...
            continue
        if typecompress == 'picks':
            # we have a train artist with a song year, we're good
            bttimbre = get_bttimbre(f)
            if bttimbre is None:
                continue
            # we even have normal features, awesome!
            processed_feats = CBTF.extract_and_compress(bttimbre,npicks,winsize,finaldim,
                                                        randproj=randproj)
        elif typecompress == 'corrcoeff':
            h5 = GETTERS.open_h5_file_read(f)
            timbres = GETTERS.get_segments_timbre(h5).T
            h5.close()
            processed_feats = CBTF.corr_and_compress(timbres,finaldim,randproj=randproj)
        elif typecompress == 'cov':
            h5 = GETTERS.open_h5_file_read(f)
            timbres = GETTERS.get_segments_timbre(h5).T
            h5.close()
            processed_feats = CBTF.cov_and_compress(timbres,finaldim,randproj=randproj)
        elif typecompress == 'avgcov':
            h5 = GETTERS.open_h5_file_read(f)
            timbres = GETTERS.get_segments_timbre(h5).T
            h5.close()
            processed_feats = CBTF.avgcov_and_compress(timbres,finaldim,randproj=randproj)
        else:
            assert False,'Unknown type of compression: '+str(typecompress)
        if processed_feats is None:
            continue
        if processed_feats.shape[0] == 0:
            continue
        # do prediction
        year_pred = do_prediction(processed_feats,kd,h5model,K)
        # add pred and ground truth to output
        if not year_pred is None:
            output.root.data.year_real.append( [year] )
            output.root.data.year_pred.append( [year_pred] )
    # close output and model
    del kd
    h5model.close()
    output.close()
    # done
    return


def process_filelist_test_wrapper(args):
    """ wrapper function for multiprocessor, calls process_filelist_test """
    try:
        process_filelist_test(**args)
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


def process_filelist_test_main_pass(nthreads,model,testsongs,
                                    npicks,winsize,finaldim,K,typecompress):
    """
    Do the main walk through the data, deals with the threads,
    creates the tmpfiles.
    INPUT
      - nthreads     - number of threads to use
      - model        - h5 files containing feats and year for all train songs
      - testsongs    - list of songs in the test set
      - npicks       - number of samples to pick per song
      - winsize      - window size (in beats) of a sample
      - finaldim     - final dimension of the sample, something like 5?
      - K            - K-nn parameter
      - typecompress - feature type, 'picks', 'corrcoeff', 'cov'
    RETURN
      - tmpfiles     - list of tmpfiles that were created
                       or None if something went wrong
    """
    # sanity checks
    assert nthreads >= 0,'Come on, give me at least one thread!'
    # prepare params for each thread
    params_list = []
    default_params = {'npicks':npicks,'winsize':winsize,'finaldim':finaldim,
                      'model':model,'K':K,'typecompress':typecompress}
    tmpfiles_stub = 'mainpasstest_tmp_output_win'+str(winsize)+'_np'+str(npicks)+'_fd'+str(finaldim)+'_'+typecompress+'_'
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


def test(nthreads,model,testsongs,npicks,winsize,finaldim,K,typecompress):
    """
    Main function to do the testing
    Do the main pass with the number of given threads.
    Then, reads the tmp files, computes the score, delete the tmpfiles.
    INPUT
      - nthreads     - number of threads to use
      - model        - h5 files containing feats and year for all train songs
      - testsongs    - songs to test on
      - npicks       - number of samples to pick per song
      - winsize      - window size (in beats) of a sample
      - finaldim     - final dimension of the sample, something like 5?
      - K            - K-nn parameter
      - typecompress - feature type, one of: 'picks', 'corrcoeff', 'cov'
    RETURN
       - nothing
    """
    # initial time
    t1 = time.time()
    # do main pass
    tmpfiles = process_filelist_test_main_pass(nthreads,model,testsongs,
                                               npicks,winsize,finaldim,K,
                                               typecompress)
                                               
    if tmpfiles is None:
        print 'Something went wrong, tmpfiles are None'
        return
    # intermediate time
    t2 = time.time()
    stimelen = str(datetime.timedelta(seconds=t2-t1))
    print 'Main pass done after',stimelen; sys.stdout.flush()
    # aggregate temp files
    year_real = []
    year_pred = []
    for tmpf in tmpfiles:
        h5 = tables.openFile(tmpf)
        year_real.extend( h5.root.data.year_real[:] )
        year_pred.extend( h5.root.data.year_pred[:] )
        h5.close()
        # delete tmp file
        os.remove(tmpf)
    # result
    BENCHMARK.evaluate(year_real,year_pred,verbose=1)
    # final time
    t3 = time.time()
    stimelen = str(datetime.timedelta(seconds=t3-t1))
    print 'Whole testing done after',stimelen
    # done
    return


def die_with_usage():
    """ HELP MENU """
    print 'process_test_set.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print 'Code to perform year prediction on the Million Song Dataset.'
    print 'This performs the testing based of a KNN model.'
    print 'USAGE:'
    print '  python process_test_set.py [FLAGS] <MSD_DIR> <model> <testartists> <tmdb>'
    print 'PARAMS:'
    print '        MSD_DIR  - main directory of the MSD dataset'
    print '          model  - h5 file where the training is saved'
    print '    testartists  - file containing test artists'
    print '           tmdb  - path to track_metadata.db'
    print 'FLAGS:'
    print '    -nthreads n  - number of threads to use'
    print '      -npicks n  - number of windows to pick per song (can be != than training)'
    print '     -winsize n  - windows size in beats for each pick'
    print '    -finaldim n  - final dimension after random projection'
    print '-typecompress s  - type of features, "picks", "corrcoeff" or "cov"'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 5:
        die_with_usage()

    # flags
    nthreads = 1
    npicks = 3
    winsize = 12
    finaldim = 5
    K = 1
    typecompress = 'picks'
    while True:
        if sys.argv[1] == '-nthreads':
            nthreads = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-npicks':
            npicks = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-winsize':
            winsize = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-finaldim':
            finaldim = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-K':
            K = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-typecompress':
            typecompress = sys.argv[2]
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # params
    msd_dir = sys.argv[1]
    model = sys.argv[2]
    testartists = sys.argv[3]
    tmdb = sys.argv[4]

    # sanity check
    assert os.path.isdir(msd_dir),'ERROR: dir '+msd_dir+' does not exist.'
    assert os.path.isfile(testartists),'ERROR: file '+testartists+' does not exist.'
    assert os.path.isfile(model),'ERROR: file '+model+' does not exist.'
    assert os.path.isfile(tmdb),'ERROR: file '+tmdb+' does not exist.'

    # verbose
    print '************ PARAMS ***************'
    print 'msd_dir:',msd_dir
    print 'model:',model
    print 'testartists:',testartists
    print 'tmdb:',tmdb
    print 'nthreads:', nthreads
    print 'npicks:',npicks
    print 'winsize:',winsize
    print 'finaldim:',finaldim
    print 'K:',K
    print 'typecompress:',typecompress
    print '***********************************'

    # read test artists
    testartists_set = set()
    f = open(testartists,'r')
    for line in f.xreadlines():
        if line == '' or line.strip() == '':
            continue
        testartists_set.add( line.strip() )
    f.close()
    print 'Found',len(testartists_set),'test artists.'

    # get test songs
    conn = sqlite3.connect(tmdb)
    q = "CREATE TEMP TABLE testartists (artist_id TEXT)"
    res = conn.execute(q)
    conn.commit()
    for aid in testartists_set:
        q = "INSERT INTO testartists VALUES ('"+aid+"')"
        conn.execute(q)
    conn.commit()
    q = "SELECT track_id FROM songs JOIN testartists"
    q += " ON testartists.artist_id=songs.artist_id WHERE year>0"
    res = conn.execute(q)
    data = res.fetchall()
    conn.close()
    print 'Found',len(data),'testing files from track_metadata.db'
    testsongs = map(lambda x: fullpath_from_trackid(msd_dir,x[0]),data)
    assert os.path.isfile(testsongs[0]),'first testing file does not exist? '+testsongs[0]

    # launch testing
    test(nthreads,model,testsongs,npicks,winsize,finaldim,K,typecompress)
    
    # done
    print 'DONE!'
    
