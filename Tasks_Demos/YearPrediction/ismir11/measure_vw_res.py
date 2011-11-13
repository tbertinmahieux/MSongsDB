"""
Measure vowpal output
"""

import os
import sys
import numpy as np
sys.path.append( os.path.abspath('..') ) # hack!
import year_pred_benchmark as BENCHMARK


def convert_back_to_year(val):
    """
    get something between 0 and 1, return a year between 1922 and 2011
    """
    assert val >= 0 and val <= 1
    return 1922. + val * ( 2011. - 1922. )



def measure(testf,vwout,verbose=1):
    """
    measure the result from the test file and vw output
    """
    years_real = []
    years_pred = []
    f_real = open(testf,'r')
    f_pred = open(vwout,'r')
    for line_real in f_real.xreadlines():
        line_pred = f_pred.readline().strip()
        years_real.append( convert_back_to_year(float(line_real.split(' ')[0])) )
        years_pred.append( convert_back_to_year(float(line_pred)) )
    # close files
    f_real.close()
    f_pred.close()
    # measure
    return BENCHMARK.evaluate(years_real,years_pred,verbose=verbose)


def die_with_usage():
    """ HELP MENU """
    print 'python measure_vw_res.py testfile vwoutput'
    sys.exit(0)

if __name__ == '__main__':

    if len(sys.argv) < 3:
        die_with_usage()

    testf = sys.argv[1]
    vwout = sys.argv[2]
    measure(testf,vwout)

