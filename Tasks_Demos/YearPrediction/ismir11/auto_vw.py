#!/usr/bin/env python
"""
Code to test a lot of parameters of vowpal
"""

import os
import sys
import copy
import time
import datetime
import numpy as np
from operator import itemgetter
import measure_vw_res as MEASURE


# FIXED ARGS
PREFIX='/home/bin/?????/vowpal_wabbit/vw'         # path to vw program
CACHE='cache_vw_tmp'                              # path to cache file
#CACHETEST='cache_vw_tmp_test'                    # path to test cache file
TRAIN='vw_train.txt'                              # train file
TEST='vw_test.txt'                                # test file
#TRAIN='vw_subtrain.txt'
#TEST='vw_subvalid.txt'
MODEL='vw_model'                                  # where to save the model
PREDS='vw_preds.txt'                              # where to output predictions
QUIET=True                                        # don't display much

AUTOTRAINOUTPUT='auto_train_results.txt'          # save the summary

# PARAMS TO TRY
PASSES=[10,50,100]                                # number of passes
INITIALT=[1,1000,100000]                          # initial t (see vw doc)
LOSSF=['squared','quantile'] # hinge bad?         # loss functions
LRATE=[.1,1,10,100]                               # learning rate
DLRATE=[1./np.sqrt(2),1.]                         # decay learning rate
CONJGRAD=['',' --conjugate_gradient',' --adaptive']  # gradient?

def build_commands():
    """
    Build commands based on arguments to try
    """
    # fixed info
    cmd = PREFIX + ' -c --cache_file ' + CACHE + ' ' + TRAIN
    cmd += ' -f ' + MODEL
    if QUIET:
        cmd += ' --quiet'
    cmd += ' ' # hack, so we can split and keep the interesting part
    # number of passes
    cmds = map(lambda x: cmd + ' --passes '+str(x),PASSES)
    # loss function
    tmpcmds = copy.deepcopy(cmds)
    cmds = []
    for cmd in tmpcmds:
        c = map(lambda x: cmd + ' --loss_function '+x,LOSSF)
        cmds.extend(c)
    # conjugate gradient
    tmpcmds = copy.deepcopy(cmds)
    cmds = []
    for cmd in tmpcmds:
        c = map(lambda x: cmd + x,CONJGRAD)
        cmds.extend(c)
    # learning rate (unless conjugate gradient)
    tmpcmds = copy.deepcopy(cmds)
    cmds = []
    for cmd in tmpcmds:
        c = map(lambda x: cmd + ' -l '+str(x) if cmd.find('conjugate')<0 else cmd,LRATE)
        cmds.extend(c)
    # initial t
    tmpcmds = copy.deepcopy(cmds)
    cmds = []
    for cmd in tmpcmds:
        c = map(lambda x: cmd + ' --initial_t '+str(x) if cmd.find('conjugate')<0 else cmd,INITIALT)
        cmds.extend(c)
    # decay learning rate
    tmpcmds = copy.deepcopy(cmds)
    cmds = []
    for cmd in tmpcmds:
        c = map(lambda x: cmd + ' --decay_learning_rate '+str(x) if cmd.find('conjugate')<0 else cmd ,DLRATE)
        cmds.extend(c)
    # done
    cmds = list(np.unique(cmds))
    return cmds

def build_test_cmd():
    """ CREATE TEST COMMAND """
    cmd = PREFIX + " " + TEST + ' --quiet'
    cmd += " -i " + MODEL + " -p " + PREDS
    # done
    return cmd

def print_best_results(results,ntoprint=5):
    """ function to print best results so far """
    print '*******************************************'
    print 'BEST RESULTS:'
    results = sorted(results,key=itemgetter(0))
    for res in results[:ntoprint]:
        print '*',res[0],'->',res[1].split('  ')[1],format('(%.3f %.3f %.3f %.3f)' % res[2])
    print '*******************************************'


def results_to_file(results):
    """ output results to file """
    results = sorted(results,key=itemgetter(0))
    f = open(AUTOTRAINOUTPUT,'w')
    for res in results:
        f.write('* ['+str(res[0])+'] '+res[1].split('  ')[1]+' -> '+str(res[2]))
        f.write('\n')
    f.close()


def launch_vw_wrapper(cmd=None,threadid=0,outputf=''):
    """
    Wrapper to use our automatic training with multiple processes
    IN DEVELOPMENT
    """
    try:
        assert not cmd is None
        assert not outputf is ''
        # replace stuff
        model = MODEL + str(int(threadid))
        cmd = cmd.replace(MODEL,model)
        cache = CACHE + str(int(threadid))
        cmd = cmd.replace(CACHE,cache)
        # launch
        raise NotImplementedError
        # get results and write them
        raise NotImplementedError
        # cleanup
        if os.path.isfile(model):
            os.remove(model)
        if os.path.isfile(cache):
            os.remove(cache)
    except KeyboardInterrupt:
        raise KeyboardInterruptError()

def die_with_usage():
    """ HELP MENU """
    print 'auto_vw.py'
    print 'test a ton of vw parameters, shows the results'
    print ''
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        die_with_usage()

    # create commands
    cmds = build_commands()
    np.random.shuffle(cmds)
    print 'Got',len(cmds),'commands, first ones:'
    print cmds[:3]

    # results, contains avg diff, cmd, all results
    results = []

    # start time
    t1 = time.time()

    # launch 
    for idx,cmd in enumerate(cmds):
        # launch command
        res = os.system(cmd)
        if res != 0:
            print '************************************************'
            print 'last cmd =',cmd
            print "Something went wrong, keyboard interrupt?"
            break
        # measure result
        test_cmd = build_test_cmd()
        res = os.system(test_cmd)
        if res != 0:
            print "Something went wrong, keyboard interrupt?"
            break
        meas = MEASURE.measure(TEST,PREDS,verbose=0)
        # results
        results.append( [meas[0], cmd, meas] )
        # meas contains: avg diff, std diff, avg diff sq, std diff sq
        print str(idx)+')',format('%.3f %.3f %.3f %.3f' % meas)
        # display time
        if idx % 5 == 4:
            print 'Time so far:',str(datetime.timedelta(seconds=time.time()-t1))
            print_best_results(results)
            results_to_file(results)

    # print best results
    print_best_results(results)

    # print results to file
    results_to_file(results)
