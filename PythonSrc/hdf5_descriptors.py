"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains descriptors used to create HDF5 files
for the Million Song Database Project

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

# code relies on pytables, see http://www.pytables.org
import tables


MAXSTRLEN = 1024

class SongMetaData(tables.IsDescription):
    """
    Class to hold the metadata of one song
    """
    artist = tables.StringCol(MAXSTRLEN,pos=0)
    analyzer_version = tables.StringCol(32,pos=1)
    audio_md5 = tables.StringCol(32,pos=2)
    bitrate = tables.IntCol(pos=3)
    duration = tables.FloatCol(pos=4)
    genre = tables.StringCol(MAXSTRLEN,pos=5)
    id = tables.StringCol(MAXSTRLEN,pos=6)
    release = tables.StringCol(MAXSTRLEN,pos=7)
    sample_md5 = tables.StringCol(32,pos=8)
    samplerate = tables.IntCol(pos=9)
    title = tables.StringCol(MAXSTRLEN,pos=10)
    #analysispath = tables.StringCol(MAXSTRLEN)
    # song mbid
    # album mbid
    # artist mbid

class SongAnalysis(tables.IsDescription):
    """
    Class to hold the analysis of one song
    """
    duration = tables.FloatCol(pos=0)
    end_of_fade_in = tables.FloatCol(pos=1)
    #segments = tables.Float32Col() # note to self: Float32Col(shape=(2,3))
    key = tables.IntCol(pos=2)
    key_confidence = tables.Float32Col(pos=3)
    loudness = tables.FloatCol(pos=4)
    sample_md5 = tables.StringCol(32,pos=5)
    mode = tables.IntCol(pos=6)
    mode_confidence = tables.Float32Col(pos=7)
    start_of_fade_out = tables.FloatCol(pos=8)
    time_signature = tables.IntCol(pos=9)
    time_signature_confidence = tables.Float32Col(pos=10)


class SongPath(tables.IsDescription):
    """
    Class to hold the path to the HDF5 file of one song
    """
    path = tables.StringCol(MAXSTRLEN,pos=0)
