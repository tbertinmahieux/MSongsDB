"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code contains a set of routines to use the Billboard API
from a python environment.
Our main goal is to get the list of charts, then the list of top
album/artist/song for each of these charts, for as far back as possible.
THIS IS NOT INTENDED TO BE A FULL COVERAGE OF THE BILLBOARD API!


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
import string
import tempfile
import urlparse
import urllib
import urllib2
import socket

# billboard api key from environment variable
BILLBOARD_API_KEY = 'NOT DEFINED'
try:
    BILLBOARD_API_KEY = os.environ['BILLBOARD_API_KEY']
except KeyError:
    print '***********************************************************'
    print 'you did not specify an API key in the environment variable:'
    print 'BILLBOARD_API_KEY'
    print 'you will not be able to use the API'
    print '***********************************************************'
TURTLE = True             # set to True if you have the reular limit 2 calls per seconds
COUNT_BILLBOARD_CALLS = 0 # can be use to slow down if we pass the limits


def do_json_call(url,filename=''):
    """
    Calls billboard API with a given command, expect an answer in
    JSON format (= a dict in python)
    Returns dictionary, or None if major problem

    If filename provided, saves data to file, then reads it
    For some reason, it can be safer, we recommend it (using temp files)
    """
    global COUNT_BILLBOARD_CALLS
    # open the connection
    try:
        COUNT_BILLBOARD_CALLS += 1
        if filename == '':
            f = urllib2.urlopen(url,timeout=30.)
        else:
            fname,httpheaders = urllib.urlretrieve(url,filename)
            f = open(fname,'r')
    except KeyboardInterrupt as e:
        print 'do_json_call:',e,'on',time.ctime(),', we close the connection'
        try:
            f.close()
        except IOError:
            pass
        raise
    except Exception as e:
        print 'do_json_call:',e,'on', time.ctime(),': check connection if happens often.'
        try:
            f.close()
        except:
            pass
        return None
    # read the line (hope there is only one...)
    # use to do (should still work): data = f.readline()
    try:
        lines = f.readlines()
        data = ''
        for l in lines:
            data += l
        data = string.replace(data,'\n','')
    except StopIteration:
        print 'do_json_call, data cant be fully read, connection problem? on', time.ctime()
        f.close()
        return None
    # close the connection
    f.close()
    # eval
    try:
        d = eval(data)
    except SyntaxError as e:
        #print e,', result message was:'
        #print data
        return None
    # return dictionary
    return d



def get_all_charts(charttype=None,chartname=None):
    """
    Try to get all charts from billboard, returns the result as a list
    of 'chart object', or None if something goes wrong
    You can specify a specific type, e.g. 'Singles' or 'Decade-end Artists'
    """
    charts = []
    start = 1
    count = 50
    while True:
        if TURTLE:
            time.sleep(.6)
        url = 'http://api.billboard.com/apisvc/chart/v1/list/spec?'
        url += 'start='+str(start)+'&count='+str(count)
        if charttype is not None:
            url += '&type='+urllib2.quote(charttype)
        if chartname is not None:
            url += '&name='+urllib2.quote(chartname)
        url += '&format=json&api_key=' + BILLBOARD_API_KEY
        res = do_json_call(url)
        if res is None:
            print 'error retrieving charts'
            return None
        n_newcharts = len(res['chartSpecs']['chartSpec'])
        if n_newcharts == 0:
            break
        charts.extend( res['chartSpecs']['chartSpec'] )
        if n_newcharts < count:
            break
        start += count
    return charts


def from_one_chart(chartid):
    """
    Get as much as we want from one chart, using chart id
    Get a chart id from get_all_charts, for instance.
    """
    if TURTLE:
        time.sleep(.6)
    url = 'http://api.billboard.com/apisvc/chart/v1/item?id='+str(chartid)
    url += '&format=json'
    url += '&api_key=' + BILLBOARD_API_KEY
    res = do_json_call(url)
    return res


def die_with_usage():
    """ HELP MENU """
    print 'pybillboard.py'
    print 'T. Bertin-Mahieux (2010) Columbia University'
    print 'tb2332@columbia.edu'
    print ''
    print 'code intended to be used as a library'
    print 'look at the main for inspiration, but it was intended'
    print 'as debugging'
    print 'to launch the __main__, do:'
    print '   python pybillboard.py -go'
    sys.exit(0)

if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # DEBUGGING

    print 'you API key:',BILLBOARD_API_KEY
    assert BILLBOARD_API_KEY != 'NOT DEFINED', 'cant go further without an API key'

    all_charts = get_all_charts()
    if all_charts is None:
        print 'something went wrong with charts'
        sys.exit(0)
    for chart in all_charts:
        print chart
    print 'num charts found:',len(all_charts)

    #print 'now just the Mid-year Albums chart:'
    #charts = get_all_charts(charttype='Mid-year Albums')
    #if charts is None:
    #    print 'something went wrong with charts'
    #    sys.exit(0)
    #for chart in charts:
    #    print chart
    #print 'num charts found:',len(charts)

    #print 'now just the Singles chart:'
    #singles_charts = get_all_charts(charttype='Singles')
    #if singles_charts is None:
    #    print 'something went wrong with charts'
    #    sys.exit(0)
    #for chart in singles_charts:
    #    print chart
    #print 'num charts found:',len(singles_charts)

    # ONE SPECIFIC CHART
    #charts = get_all_charts(charttype='Singles',chartname='Dance')
    #print 'num charts found for specific type and name:',len(charts)
    #for chart in charts:
    #    print chart
    #print 'we take the last one:'
    #chart = charts[-1]
    #print 'we take the first one:'
    #chart = charts[0]
    #print chart
    #print 'name as utf 8:',chart['name'].encode('utf-8')
    #print 'id:',chart['id']
    #chartid = chart['id']

    # get all songs from that chart
    #res = from_one_chart(chartid)
    #print res

    # from all charts, count the ones where the server does not crash
    cnt = 0
    for chart in all_charts:
        res = from_one_chart(chart['id'])
        if res is not None:
            cnt += 1
            print chart['id']
    print 'number of good charts:',cnt
