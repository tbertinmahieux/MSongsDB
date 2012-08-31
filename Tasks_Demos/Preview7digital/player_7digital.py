"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code uses 7digital API and info contained in HDF5 song
file to get a preview URL and play it.
It can be used to quickly listen to a song in the dataset.
The goal is to be able to search songs by artist name, title,
or Echo Nest ID.

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
import urllib
import urllib2
import sqlite3
import numpy as np
import threading
import get_preview_url as GETURL
try:
    from Tkinter import *
except ImportError:
    print 'you need Tkinter installed!'
    sys.exit(0)
try:
    import ao
except ImportError:
    print 'you need pyao installed!'
    sys.exit(0)
try:
    import mad
except ImportError:
    print 'you need pymad installed!'
    sys.exit(0)

# sampling rate from 7 digital
DIGITAL7SRATE=22500


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'"+s.replace("'","''")+"'"


class PlayerApp(Frame):
    """
    MAIN CLASS, contains the Tkinter app
    """
    def __init__(self, master=None, tmdb=None, url=''):
        """
        Contstructor
        INPUTS
           tmdb  - path to track_metadata.db (containing track_7digitalid)
           url   - more for debugging, starts with a loaded url
        """
        Frame.__init__(self, master)
        # verbose
        self.verbose=1
        # some class variables
        self.curr_track_id = None
        self.is_playing = False
        # db conn
        self.tmdb = tmdb
        self.conn_tmdb = sqlite3.connect(tmdb) if tmdb else None
        # grid and size
        self.grid(sticky=N+S+E+W)
        self.config(height=300,width=500)
        self.columnconfigure(0,minsize=60)
        self.grid_propagate(0)
        # add objects
        self.createButtons()
        self.createSearchFields()
        self.createListBoxes()
        # read url
        self.url = url

    def __del__(self):
        """ DESTRUCTOR """
        if not self.conn_tmdb is None:
            self.conn_tmdb.close()

    def createButtons(self):
        # quit
        self.quitButton = Button(self, text='Quit', command=self.do_quit)
        self.quitButton.grid(row=0,column=0,sticky=N+S+E+W)
        # search EN ID
        self.searchidButton = Button(self, text='Search by EN id', command=self.search_enid)
        self.searchidButton.grid(row=4,column=1,sticky=N+S+E+W)
        # search artist name
        self.searchTitleButton = Button(self, text='Search by Artist/Title', command=self.search_title)
        self.searchTitleButton.grid(row=5,column=3,sticky=N+S+E+W)
        # play
        self.playButton = Button(self,text='play', command=self.play_thread)
        self.playButton.grid(row=7,column=1,sticky=N+S+E+W)
        # stop
        self.stopButton = Button(self,text='stop', command=self.stop)
        self.stopButton.grid(row=7,column=2,sticky=N+S+E+W)

    def createSearchFields(self):
        # search Echo Nest ID
        self.entryENID = Entry(self)
        self.entryENID.grid(row=3,column=1,sticky=N+S+E+W)
        # search artist + title
        self.entryArtist = Entry(self)
        self.entryArtist.grid(row=3,column=3,sticky=N+S+E+W)
        self.entryTitle = Entry(self)
        self.entryTitle.grid(row=4,column=3,sticky=N+S+E+W)

    def createListBoxes(self):
        # vertical scrollbar
        self.yScroll = Scrollbar(self,orient=VERTICAL)
        self.yScroll.grid(row=6,column=5,sticky=N+S)
        # listbox
        self.listboxResult = Listbox(self,yscrollcommand=self.yScroll.set)
        self.listboxResult.grid(row=6,column=1,columnspan=4,
                                sticky=N+S+E+W)
        self.listboxResult.exportselection = 0 # prevent copy past
        self.listboxResult.selectmode = SINGLE # one line at a time

    #************************* COMMANDS FOR BUTTONS *******************#

    def update_display(self):
        """ update the main display (ListBox) from a given track_id """
        if self.curr_track_id is None:
            print "no current track id"
        conn = sqlite3.connect(self.tmdb)
        q = "SELECT artist_name,title FROM songs WHERE track_id='"+self.curr_track_id+"' LIMIT 1"
        res = conn.execute(q)
        data = res.fetchone()
        conn.close()
        self.listboxResult.insert(0,'**************************')
        self.listboxResult.insert(1,data[0])
        self.listboxResult.insert(2,data[1])
        self.listboxResult.insert(3,self.curr_track_id)
        if self.url:
            self.listboxResult.insert(4,self.url)

    def search_title(self):
        """ search using artist name and title """
        aname = self.entryArtist.get().strip()
        title = self.entryTitle.get().strip()
        if aname == '' or title == '':
            print 'Empty artist or title field:',aname,'/',title
            return
        # search
        q = "SELECT track_7digitalid,track_id FROM songs WHERE artist_name="+encode_string(aname)
        q += " AND title="+encode_string(title)+" LIMIT 1"
        res = self.conn_tmdb.execute(q)
        d7id = res.fetchone()
        if len(d7id) == 0 or d7id[0] == 0:
            print 'Sorry, we do not have the 7digital track ID for this one'
            return
        self.url = self.get_url_thread(d7id[0])
        self.curr_track_id = d7id[1]
        
    def search_enid(self):
        """ search for a song by its trackid or songid """
        tid = self.entryENID.get().strip().upper()
        if len(tid) != 18:
            print 'WRONG ECHO NEST ID:',tid,'(length='+str(len(tid))+')'
            return
        if tid[:2] != 'TR' and tid[:2] != 'SO':
            print 'WRONG ECHO NEST ID:',tid,'(should start by TR or SO)'
            return
        # we got an id, lets go
        if tid[:2] == 'TR':
            q = "SELECT track_7digitalid,track_id FROM songs WHERE track_id='"+tid+"' LIMIT 1"
            res = self.conn_tmdb.execute(q)
            d7id = res.fetchone()
        else:
            q = "SELECT track_7digitalid,track_id FROM songs WHERE song_id='"+tid+"' LIMIT 1"
            res = self.conn_tmdb.execute(q)
            d7id = res.fetchone()
        print 'for',tid,'we found 7digital track id:',d7id
        if len(d7id) == 0 or d7id[0] == 0:
            print 'Sorry, we do not have the 7digital track ID for this one'
            return
        self.url = self.get_url_thread(d7id[0])
        self.curr_track_id = d7id[1]

    def get_url_thread(self,d7id):
        """ launch 'get_url' as a thread, button does not stay pressed """
        t = threading.Thread(target=self.get_url,args=(d7id,))
        t.start()
        
    def get_url(self,d7id):
        """ get an url from a 7digital track id """
        url = GETURL.get_preview_from_trackid(d7id)
        print 'Found url:',url
        self.url = url
        self.update_display() # update main display

    def do_quit(self):
        """ quit but close stream before """
        self.stop()
        self.quit()
        
    def stop(self):
        self.do_stop = True

    def play_thread(self):
        """ launch 'play' as a thread, button does not stay pressed """
        t = threading.Thread(target=self.play)
        t.start()
        
    def play(self):
        """
        Main function that plays a 7digital url
        """
        if self.url == '':
            return
        if self.is_playing:
            return
        self.is_playing = True
        self.do_stop = False
        self.printinfo('start playing url:',self.url)
        #urldata = urllib.urlretrieve(self.url)
        urlstream = urllib2.urlopen(self.url)
        mf = mad.MadFile(urlstream)
        # if bits=32, too fast
        self.dev = ao.AudioDevice('alsa', bits=16, rate=mf.samplerate(),channels=2)
        buf = mf.read()
        t1 = time.time()
        while buf != None and not self.do_stop:
            # len(buf) is 4608
            self.dev.play(buf, len(buf))
            buf = mf.read()
        self.do_stop = False
        self.is_playing = False
        tlag = time.time() - t1
        self.printinfo('done playing url after',str(int(tlag)),'seconds')

    def printinfo(self,*msg):
        """ print message if verbose """
        if self.verbose>0:
            s = 'INFO:'
            for k in msg:
                s += ' ' + str(k)
            print s



def launch_applet(tmdb=None,url=''):
    """
    Should be the main function to launch the interface
    """
    app = PlayerApp(tmdb=tmdb,url=url)
    app.master.title("7digital Player for the Million Song Dataset")
    app.mainloop()
    

def die_with_usage():
    """ HELP MENU """
    print 'player_7digital.py'
    print '    by T. Bertin-Mahieux (2011) Columbia University'
    print '       tb2332@columbia.edu'
    print 'Small interface to the 7digital service.'
    print 'INPUT'
    print '   python player_7digital.py track_metadata.db'
    print 'REQUIREMENTS'
    print '  * 7digital key in your environment as: DIGITAL7_API_KEY'
    print '  * pyao'
    print '  * pymad'
    print '  * Tkinter for python'
    print '  * track_metadata.db (new one with 7digital ids, check website)'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # check track metadata, makes sure it's the new version
    # with track_7digitalid
    tmdb = sys.argv[1]
    if not os.path.isfile(tmdb):
        print 'ERROR: file',tmdb,'does not exist.'
        sys.exit(0)
    conn = sqlite3.connect(tmdb)
    try:
        res = conn.execute("SELECT track_7digitalid FROM songs LIMIT 1")
        data = res.fetchone()
    except sqlite3.OperationalError:
        print 'ERROR: do you have the old track_metadata.db?'
        print '       get the new one with 7digital ids on the Million Song Dataset website'
        sys.exit(0)
    finally:
        conn.close()

    # launch interface
    url = ''
    launch_applet(tmdb=tmdb,url=url)
