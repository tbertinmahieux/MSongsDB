"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Library to compress beat features, mostly timbre here,
probably using random projections in order to use large KNN later.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.

Copyright 2011, Thierry Bertin-Mahieux

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
import numpy as np
import randproj as RANDPROJ


def corr_and_compress(feats,finaldim,seed=3232343,randproj=None):
    """
    From a features matrix 12x.... (beat-aligned or not)
    Compute the correlation matrix (12x12) and projects it (except diagonal)
    to the given final dim
    RETURN
       vector 1xfinaldim   or 0xfinaldim is problem
    """
    # features length
    ftlen = feats.shape[1]
    ndim = feats.shape[0]
    # too small case
    if ftlen < 3:
        return np.zeros((0,finaldim))
    # random projection
    if randproj is None:
        # 12*12
        randproj = RANDPROJ.proj_point5(144, finaldim, seed=seed)
    # corr
    corrc = np.corrcoef(feats)
    # compress
    return np.dot(corrc.flatten(),randproj).reshape(1,finaldim)


def cov_and_compress(feats,finaldim,seed=3232343,randproj=None):
    """
    From a features matrix 12x.... (beat-aligned or not)
    Compute the correlation matrix (12x12) and projects it (except diagonal)
    to the given final dim
    RETURN
       vector 1xfinaldim   or 0xfinaldim is problem
    """
    # features length
    ftlen = feats.shape[1]
    ndim = feats.shape[0]
    # too small case
    if ftlen < 3:
        return np.zeros((0,finaldim))
    # random projection
    if randproj is None:
        # 12*12
        randproj = RANDPROJ.proj_point5(144, finaldim, seed=seed)
    # corr
    fcov = np.cov(feats)
    # compress
    return np.dot(fcov.flatten(),randproj).reshape(1,finaldim)

def avgcov_and_compress(feats,finaldim,seed=3232343,randproj=None):
    """
    From a features matrix 12x.... (beat-aligned or not)
    Compute the correlation matrix (12x12) and projects it (except diagonal)
    to the given final dim
    RETURN
       vector 1xfinaldim   or 0xfinaldim is problem
    """
    # features length
    ftlen = feats.shape[1]
    ndim = feats.shape[0]
    # too small case
    if ftlen < 3:
        return np.zeros((0,finaldim))
    # random projection
    if randproj is None:
        # 12 + 78, 78=13*12/2
        randproj = RANDPROJ.proj_point5(90, finaldim, seed=seed)
    # corr
    avg = np.average(feats,1)
    cov = np.cov(feats)
    covflat = []
    for k in range(12):
        covflat.extend( np.diag(cov,k) )
    covflat = np.array(covflat)
    feats = np.concatenate([avg,covflat])
    # compress
    return np.dot(feats.flatten(),randproj).reshape(1,finaldim)

def extract_and_compress(btfeat,npicks,winsize,finaldim,seed=3232343,randproj=None):
    """
    From a btfeat matrix, usually 12xLENGTH
    Extracts 'npicks' windows of size 'winsize' equally spaced
    Flatten these picks, pass them through a random projection, final
    size is 'finaldim'
    Returns matrix npicks x finaldim, or 0 x finaldim if problem
    (btfeats not long enough for instance)
    We could return less than npicks if not long enough!
    For speed, we can compute the random projection once and pass it as an
    argument.
    """
    # features length
    ftlen = btfeat.shape[1]
    ndim = btfeat.shape[0]
    # too small case
    if ftlen < winsize:
        return np.zeros((0,finaldim))
    # random projection
    if randproj is None:
        randproj = RANDPROJ.proj_point5(ndim * winsize, finaldim, seed=seed)
    # not big enough for number of picks, last one too large return just 1
    if ftlen < int(ftlen * (npicks *1./(npicks+1))) + winsize:
        pos = int( (ftlen-winsize) /  2.) # middle
        picks = [ btfeat[:,pos:pos+winsize] ]
    # regular case, picks will contain npicks
    else:
        picks = []
        for k in range(1,npicks+1):
            pos = int(ftlen * (k *1./(npicks+1)))
            picks.append( btfeat[:,pos:pos+winsize] )
    # project / compress these
    projections = map(lambda x: np.dot(x.flatten(),randproj).reshape(1,finaldim), picks)
    return np.concatenate(projections)
    


def die_with_usage():
    """ HELP MENU """
    print 'compress_feat.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print ''
    print 'This code extracts and compress samples from beat-aligned features.'
    print 'Should be used as a library, no main'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    die_with_usage()
