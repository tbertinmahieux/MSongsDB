"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Code to parse the whole training set, get a summary of the features,
and save them in a KNN-ready format.

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
import randproj as RANDPROJ
for p in YEAR_REC_FOLDERS:
    sys.path.append(p)
from beat_aligned_feats import get_bttimbre


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


def process_filelist_train(filelist=None,testartists=None,tmpfilename=None,
                           npicks=None,winsize=None,finaldim=None,typecompress='picks'):
    """
    Main function, process all files in the list (as long as their artist
    is not in testartist)
    INPUT
       filelist     - a list of song files
       testartists  - set of artist ID that we should not use
       tmpfilename  - where to save our processed features
       npicks       - number of segments to pick per song
       winsize      - size of each segment we pick
       finaldim     - how many values do we keep
       typecompress - one of 'picks' (win of btchroma), 'corrcoef' (correlation coefficients),
                      'cov' (covariance)
    """
    # sanity check
    for arg in locals().values():
        assert not arg is None,'process_filelist_train, missing an argument, something still None'
    if os.path.isfile(tmpfilename):
        print 'ERROR: file',tmpfilename,'already exists.'
        return
    # create outputfile
    output = tables.openFile(tmpfilename, mode='a')
    group = output.createGroup("/",'data','TMP FILE FOR YEAR RECOGNITION')
    output.createEArray(group,'feats',tables.Float64Atom(shape=()),(0,finaldim),'',
                        expectedrows=len(filelist))
    output.createEArray(group,'year',tables.IntAtom(shape=()),(0,),'',
                        expectedrows=len(filelist))
    output.createEArray(group,'track_id',tables.StringAtom(18,shape=()),(0,),'',
                        expectedrows=len(filelist))
    # random projection
    ndim = 12 # fixed in this dataset
    if typecompress == 'picks':
        randproj = RANDPROJ.proj_point5(ndim * winsize, finaldim)
    elif typecompress == 'corrcoeff' or typecompress == 'cov':
        randproj = RANDPROJ.proj_point5(ndim * ndim, finaldim)
    elif typecompress == 'avgcov':
        randproj = RANDPROJ.proj_point5(90, finaldim)
    else:
        assert False,'Unknown type of compression: '+str(typecompress)
    # iterate over files
    cnt_f = 0
    for f in filelist:
        cnt_f += 1
        # verbose
        if cnt_f % 50000 == 0:
            print 'training... checking file #',cnt_f
        # check file
        h5 = GETTERS.open_h5_file_read(f)
        artist_id = GETTERS.get_artist_id(h5)
        year = GETTERS.get_year(h5)
        track_id = GETTERS.get_track_id(h5)
        h5.close()
        if year <= 0 or artist_id in testartists:
            continue
        # we have a train artist with a song year, we're good
        bttimbre = get_bttimbre(f)
        if typecompress == 'picks':
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
        # save them to tmp file
        n_p_feats = processed_feats.shape[0]
        output.root.data.year.append( np.array( [year] * n_p_feats ) )
        output.root.data.track_id.append( np.array( [track_id] * n_p_feats ) )
        output.root.data.feats.append( processed_feats )
    # we're done, close output
    output.close()
    return

            
def process_filelist_train_wrapper(args):
    """ wrapper function for multiprocessor, calls process_filelist_train """
    try:
        process_filelist_train(**args)
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


def process_filelist_train_main_pass(nthreads,maindir,testartists,
                                     npicks,winsize,finaldim,trainsongs=None,
                                     typecompress='picks'):
    """
    Do the main walk through the data, deals with the threads,
    creates the tmpfiles.
    INPUT
      - nthreads     - number of threads to use
      - maindir      - dir of the MSD, wehre to find song files
      - testartists  - set of artists to ignore
      - npicks       - number of samples to pick per song
      - winsize      - window size (in beats) of a sample
      - finaldim     - final dimension of the sample, something like 5?
      - trainsongs   - list of files to use for training
      - typecompress - 'picks', 'corrcoeff', 'cov'
    RETURN
      - tmpfiles     - list of tmpfiles that were created
                       or None if something went wrong
    """
    # sanity checks
    assert nthreads >= 0,'Come on, give me at least one thread!'
    if not os.path.isdir(maindir):
        print 'ERROR: directory',maindir,'does not exist.'
        return None
    # get all files
    if trainsongs is None:
        allfiles = get_all_files(maindir)
    else:
        allfiles = trainsongs
    assert len(allfiles)>0,'Come on, give me at least one file in '+maindir+'!'
    if nthreads > len(allfiles):
        nthreads = len(allfiles)
        print 'more threads than files, reducing number of threads to:',nthreads
    print 'WE FOUND',len(allfiles),'POTENTIAL TRAIN FILES'
    # prepare params for each thread
    params_list = []
    default_params = {'npicks':npicks,'winsize':winsize,'finaldim':finaldim,
                      'testartists':testartists,'typecompress':typecompress}
    tmpfiles_stub = 'mainpass_tmp_output_win'+str(winsize)+'_np'+str(npicks)+'_fd'+str(finaldim)+'_'+typecompress+'_'
    tmpfiles = map(lambda x: os.path.join(os.path.abspath('.'),tmpfiles_stub+str(x)+'.h5'),range(nthreads))
    nfiles_per_thread = int(np.ceil(len(allfiles) * 1. / nthreads))
    for k in range(nthreads):
        # params for one specific thread
        p = copy.deepcopy(default_params)
        p['tmpfilename'] = tmpfiles[k]
        p['filelist'] = allfiles[k*nfiles_per_thread:(k+1)*nfiles_per_thread]
        params_list.append(p)
    # launch, run all the jobs
    pool = multiprocessing.Pool(processes=nthreads)
    try:
        pool.map(process_filelist_train_wrapper, params_list)
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



def train(nthreads,maindir,output,testartists,npicks,winsize,finaldim,trainsongs=None,typecompress='picks'):
    """
    Main function to do the training
    Do the main pass with the number of given threads.
    Then, reads the tmp files, creates the main output, delete the tmpfiles.
    INPUT
      - nthreads     - number of threads to use
      - maindir      - dir of the MSD, wehre to find song files
      - output       - main model, contains everything to perform KNN
      - testartists  - set of artists to ignore
      - npicks       - number of samples to pick per song
      - winsize      - window size (in beats) of a sample
      - finaldim     - final dimension of the sample, something like 5?
      - trainsongs   - list of songs to use for training
      - typecompress - 'picks', 'corrcoeff' or 'cov'
    RETURN
       - nothing
    """
    # sanity checks
    if os.path.isfile(output):
        print 'ERROR: file',output,'already exists.'
        return
    # initial time
    t1 = time.time()
    # do main pass
    tmpfiles = process_filelist_train_main_pass(nthreads,maindir,testartists,
                                                npicks,winsize,finaldim,
                                                trainsongs=trainsongs,typecompress=typecompress)
    if tmpfiles is None:
        print 'Something went wrong, tmpfiles are None'
        return
    # intermediate time
    t2 = time.time()
    stimelen = str(datetime.timedelta(seconds=t2-t1))
    print 'Main pass done after',stimelen; sys.stdout.flush()
    # find approximate number of rows per tmpfiles
    h5 = tables.openFile(tmpfiles[0],'r')
    nrows = h5.root.data.year.shape[0] * len(tmpfiles)
    h5.close()
    # create output
    output = tables.openFile(output, mode='a')
    group = output.createGroup("/",'data','KNN MODEL FILE FOR YEAR RECOGNITION')
    output.createEArray(group,'feats',tables.Float64Atom(shape=()),(0,finaldim),'feats',
                        expectedrows=nrows)
    output.createEArray(group,'year',tables.IntAtom(shape=()),(0,),'year',
                        expectedrows=nrows)
    output.createEArray(group,'track_id',tables.StringAtom(18,shape=()),(0,),'track_id',
                        expectedrows=nrows)
    # aggregate temp files
    for tmpf in tmpfiles:
        h5 = tables.openFile(tmpf)
        output.root.data.year.append( h5.root.data.year[:] )
        output.root.data.track_id.append( h5.root.data.track_id[:] )
        output.root.data.feats.append( h5.root.data.feats[:] )
        h5.close()
        # delete tmp file
        os.remove(tmpf)
    # close output
    output.close()
    # final time
    t3 = time.time()
    stimelen = str(datetime.timedelta(seconds=t3-t1))
    print 'Whole training done after',stimelen
    # done
    return


def die_with_usage():
    """ HELP MENU """
    print 'process_train_set.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print 'Code to perform year prediction on the Million Song Dataset.'
    print 'This performs the training of the KNN model.'
    print 'USAGE:'
    print '  python process_train_set.py [FLAGS] <MSD_DIR> <output>'
    print 'PARAMS:'
    print '        MSD_DIR  - main directory of the MSD dataset'
    print '         output  - output filename (.h5 file)'
    print 'FLAGS:'
    print '    -nthreads n  - number of threads to use'
    print ' -testartists f  - file containing test artists (to ignore)'
    print '      -npicks n  - number of windows to pick per song'
    print '     -winsize n  - windows size in beats for each pick'
    print '    -finaldim n  - final dimension after random projection'
    print '        -tmdb f  - path to track_metadata.db, makes things faster'
    print '-typecompress s  - actual features we use, "picks", "corrcoeff" or "cov"'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # flags
    nthreads = 1
    testartists = ''
    npicks = 3
    winsize = 12
    finaldim = 5
    tmdb = ''
    typecompress = 'picks'
    while True:
        if sys.argv[1] == '-nthreads':
            nthreads = int(sys.argv[2])
            sys.argv.pop(1)
        elif sys.argv[1] == '-testartists':
            testartists = sys.argv[2]
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
        elif sys.argv[1] == '-tmdb':
            tmdb = sys.argv[2]
            sys.argv.pop(1)
        elif sys.argv[1] == '-typecompress':
            typecompress = sys.argv[2]
            sys.argv.pop(1)
        else:
            break
        sys.argv.pop(1)

    # params
    msd_dir = sys.argv[1]
    output = sys.argv[2]

    # read test artists
    testartists_set = set()
    if testartists != '':
        f = open(testartists,'r')
        for line in f.xreadlines():
            if line == '' or line.strip() == '':
                continue
            testartists_set.add( line.strip() )
        f.close()

    # get songlist from track_metadata.db
    trainsongs = None
    if tmdb != '':
        assert os.path.isfile(tmdb),'Database: '+tmdb+' does not exist.'
        conn = sqlite3.connect(tmdb)
        q = "CREATE TEMP TABLE testartists (artist_id TEXT)"
        res = conn.execute(q)
        conn.commit()
        for aid in testartists_set:
            q = "INSERT INTO testartists VALUES ('"+aid+"')"
            conn.execute(q)
        conn.commit()
        q = "CREATE TEMP TABLE trainartists (artist_id TEXT)"
        res = conn.execute(q)
        conn.commit()
        q = "INSERT INTO trainartists SELECT DISTINCT artist_id FROM songs"
        q += " EXCEPT SELECT artist_id FROM testartists"
        res = conn.execute(q)
        conn.commit()
        q = "SELECT track_id FROM songs JOIN trainartists"
        q += " ON trainartists.artist_id=songs.artist_id WHERE year>0"
        res = conn.execute(q)
        data = res.fetchall()
        conn.close()
        print 'Found',len(data),'training files from track_metadata.db'
        trainsongs = map(lambda x: fullpath_from_trackid(msd_dir,x[0]),data)
        assert os.path.isfile(trainsongs[0]),'first training file does not exist? '+trainsongs[0]

    # settings
    print 'msd dir:',msd_dir
    print 'output:',output
    print 'nthreads:',nthreads
    print 'testartists:',testartists,'('+str(len(testartists_set))+' artists)'
    print 'npicks:',npicks
    print 'winsize:',winsize
    print 'finaldim:',finaldim
    print 'tmdb:',tmdb
    print 'typecompress:',typecompress

    # sanity check
    if not os.path.isdir(msd_dir):
        print 'ERROR:',msd_dir,'is not a directory.'
        sys.exit(0)
    if os.path.isfile(output):
        print 'ERROR: file',output,'already exists.'
        sys.exit(0)

    # launch training
    train(nthreads,msd_dir,output,testartists_set,npicks,winsize,finaldim,trainsongs,typecompress)

    # done
    print 'DONE!'
