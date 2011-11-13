"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

Library to generate random matrices using different methods

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

# square root of 3, which we might comput eoften otherwise
SQRT3=np.sqrt(3.)


def proj_point5(dimFrom,dimTo,seed=3232343):
    """
    Creates a matrix dimFrom x dimTo where each element is
    .5 or -.5 with probability 1/2 each
    For theoretical results using this projection see:
      D. Achlioptas. Database-friendly random projections.
      In Symposium on Principles of Database Systems
      (PODS), pages 274-281, 2001.
      http://portal.acm.org/citation.cfm?doid=375551.375608
    """
    if dimFrom == dimTo:
        return np.eye(dimFrom)
    np.random.seed(seed)
    return np.random.randint(2,size=(dimFrom,dimTo)) - .5


def proj_sqrt3(dimFrom, dimTo,seed=3232343):
    """
    Creates a matrix dimFrom x dimTo where each element is
    sqrt(3) or -sqrt(3) with probability 1/6 each
    or 0 otherwise
    Slower than proj_point5 to create, and lots of zeros.
    For theoretical results using this projection see:
      D. Achlioptas. Database-friendly random projections.
      In Symposium on Principles of Database Systems
      (PODS), pages 274-281, 2001.
      http://portal.acm.org/citation.cfm?doid=375551.375608
    """
    if dimFrom == dimTo:
        return np.eye(dimFrom)
    np.random.seed(seed)
    x = np.random.rand(dimFrom,dimTo)
    res = np.zeros((dimFrom,dimTo))
    res[np.where(x<1./6)] = SQRT3
    res[np.where(x>1.-1./6)] = -SQRT3
    return res


def die_with_usage():
    """ HELP MENU """
    print 'randproj.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print ''
    print 'This code generates matrices for random projections.'
    print 'Should be used as a library, no main'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    die_with_usage()
