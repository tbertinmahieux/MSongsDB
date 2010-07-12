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
    artist = tables.StringCol(MAXSTRLEN)
    analyzer_version = tables.StringCol(32)
    audio_md5 = tables.StringCol(32)
    bitrate = tables.IntCol()
    duration = tables.FloatCol()
    genre = tables.StringCol(MAXSTRLEN)
    id = tables.StringCol(MAXSTRLEN)
    release = tables.StringCol(MAXSTRLEN)
    sample_md5 = tables.StringCol(32)
    samplerate = tables.IntCol()
    title = tables.StringCol(MAXSTRLEN)
    #analysispath = tables.StringCol(MAXSTRLEN)
    # song mbid
    # album mbid
    # artist mbid

class SongAnalysis(tables.IsDescription):
    """
    Class to hold the analysis of one song
    """
    duration = tables.FloatCol()
    end_of_fade_in = tables.FloatCol()
    segments = tables.Float32Col() # note to self: Float32Col(shape=(2,3))
    key = tables.IntCol()
    key_confidence = tables.Float32Col()
    loudness = tables.FloatCol()
    sample_md5 = tables.StringCol(32)
    segments_start = tables.Float32Col(shape=(717,1))
    segments_confidence = tables.Float32Col(shape=(717,))
    mode = tables.IntCol()
    mode_confidence = tables.Float32Col()
    start_of_fade_out = tables.FloatCol()
    time_signature = tables.IntCol()
    time_signature_confidence = tables.Float32Col()
