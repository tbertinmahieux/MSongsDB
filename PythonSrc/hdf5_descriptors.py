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
    artist_name = tables.StringCol(MAXSTRLEN)
    artist_id = tables.StringCol(32)
    artist_mbid = tables.StringCol(40)
    artist_playmeid = tables.IntCol()
    artist_7digitalid = tables.IntCol()
    analyzer_version = tables.StringCol(32)
    genre = tables.StringCol(MAXSTRLEN)
    release = tables.StringCol(MAXSTRLEN)
    release_7digitalid = tables.IntCol()
    title = tables.StringCol(MAXSTRLEN)
    artist_familiarity = tables.Float64Col()
    artist_hotttnesss = tables.Float64Col()
    song_id = tables.StringCol(32)
    song_hotttnesss = tables.Float64Col()
    artist_latitude = tables.Float64Col()
    artist_longitude = tables.Float64Col()
    artist_location = tables.StringCol(MAXSTRLEN)
    track_7digitalid = tables.IntCol()
    # ARRAY INDICES
    idx_similar_artists = tables.IntCol()
    idx_artist_terms = tables.IntCol()
    # TO ADD
    
    # song mbid
    # album mbid

    # url    
    # preview url, 7digital, release_image


class SongAnalysis(tables.IsDescription):
    """
    Class to hold the analysis of one song
    """
    analysis_sample_rate = tables.IntCol()
    audio_md5 = tables.StringCol(32)
    danceability = tables.Float64Col()
    duration = tables.Float64Col()
    end_of_fade_in = tables.Float64Col()
    energy = tables.Float64Col()
    key = tables.IntCol()
    key_confidence = tables.Float64Col()
    loudness = tables.Float64Col()
    mode = tables.IntCol()
    mode_confidence = tables.Float64Col()
    start_of_fade_out = tables.Float64Col()
    tempo = tables.Float64Col()
    time_signature = tables.IntCol()
    time_signature_confidence = tables.Float64Col()
    track_id = tables.StringCol(32)
    # ARRAY INDICES
    idx_segments_start = tables.IntCol()
    idx_segments_confidence = tables.IntCol()
    idx_segments_pitches = tables.IntCol()
    idx_segments_timbre = tables.IntCol()
    idx_segments_loudness_max = tables.IntCol()
    idx_segments_loudness_max_time = tables.IntCol()
    idx_segments_loudness_start = tables.IntCol()
    idx_sections_start = tables.IntCol()
    idx_sections_confidence = tables.IntCol()
    idx_beats_start = tables.IntCol()
    idx_beats_confidence = tables.IntCol()
    idx_bars_start = tables.IntCol()
    idx_bars_confidence = tables.IntCol()
    idx_tatums_start = tables.IntCol()
    idx_tatums_confidence = tables.IntCol()
    
class SongMusicBrainz(tables.IsDescription):
    """
    Class to hold information coming from
    MusicBrainz for one song
    """
    year = tables.IntCol()
    # ARRAY INDEX
    idx_artist_mbtags = tables.IntCol()
