"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains descriptors used to create HDF5 files
for the Million Song Database Project.
What information gets in the database should be decided here.

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
    artist_name = tables.StringCol(MAXSTRLEN,pos=0)
    artist_id = tables.StringCol(MAXSTRLEN,pos=1)
    analyzer_version = tables.StringCol(32,pos=2)
    audio_md5 = tables.StringCol(32,pos=3)
    analysis_sample_rate = tables.IntCol(pos=4)
    duration = tables.FloatCol(pos=5)
    genre = tables.StringCol(MAXSTRLEN,pos=6)
    id = tables.StringCol(MAXSTRLEN,pos=7)
    release = tables.StringCol(MAXSTRLEN,pos=8)
    sample_md5 = tables.StringCol(32,pos=9)
    title = tables.StringCol(MAXSTRLEN,pos=11)
    artist_familiarity = tables.FloatCol(pos=12)
    artist_hotttnesss = tables.FloatCol(pos=13)
    song_hotttnesss = tables.FloatCol(pos=14)
    artist_latitude = tables.FloatCol(pos=15)
    artist_longitude = tables.FloatCol(pos=16)
    artist_location = tables.StringCol(MAXSTRLEN,pos=17)

    # TO ADD
    
    # song mbid
    # album mbid
    # artist mbid

    # tags (from EN) need to crate a new table
    # we just need a start
    tags_idx = tables.IntCol(pos=14)

    # url
    
    # preview url, 7digital, release_image


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
    tempo = tables.FloatCol(pos=9)
    time_signature = tables.IntCol(pos=10)
    time_signature_confidence = tables.Float32Col(pos=11)
    # ARRAY INDECES
    idx_segments_start = tables.IntCol(pos=12)
    idx_segments_confidence = tables.IntCol(pos=13)
    idx_segments_pitches = tables.IntCol(pos=14)
    idx_segments_timbre = tables.IntCol(pos=15)
    idx_segments_loudness_max = tables.IntCol(pos=16)
    idx_segments_loudness_max_time = tables.IntCol(pos=17)
    idx_segments_loudness_start = tables.IntCol(pos=18)
    idx_sections_start = tables.IntCol(pos=19)
    idx_sections_confidence = tables.IntCol(pos=20)
    idx_beats_start = tables.IntCol(pos=21)
    idx_beats_confidence = tables.IntCol(pos=22)
    idx_bars_start = tables.IntCol(pos=23)
    idx_bars_confidence = tables.IntCol(pos=24)
    idx_tatums_start = tables.IntCol(pos=25)
    idx_tatums_confidence = tables.IntCol(pos=26)

class SongPath(tables.IsDescription):
    """
    Class to hold the path to the HDF5 file of one song
    Used for database maintenance? if we merge many HDF5 files
    """
    path = tables.StringCol(MAXSTRLEN,pos=0)

