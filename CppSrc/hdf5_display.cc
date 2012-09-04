/*
 Thierry Bertin-Mahieux (2010) Columbia University
 tb2332@columbia.edu

 Demo code to display all fields of a given MSD HDF5 song file.

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
*/

#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <vector>
using namespace std;

#include "hdf5_getters.h"

/*
 * Help menu
 */
void help_menu(void) {
  
  cout << "hdf5_display" << endl;
  cout << "    by T. Bertin-Mahieux (2011) Columbia U." << endl;
  cout << "       tb2332@columbia.edu" << endl;
  exit(0);
}


int main(int argc, const char* argv[]) {

  // help menu?
  if (argc < 2 || strcmp(argv[1],"help") == 0 || strcmp(argv[1],"-help") == 0)
    help_menu();

  // create wrapper
  HDF5Getters getters(argv[1]);
  
  // init values
  double dval;
  std::string sval;
  int ival;
  vector<double> dvec;
  vector<string> svec;

  // print everything!
  dval = getters.get_analysis_sample_rate();
  cout << "analysis_sample_rate: " << dval << endl;
  ival = getters.get_artist_7digitalid();
  cout << "artist_7digitalid: " << ival << endl;
  dval = getters.get_artist_familiarity();
  cout << "artist_familiarity: " << dval << endl;
  dval = getters.get_artist_hotttnesss();
  cout << "artist_hotttnesss: " << dval << endl;
  sval = getters.get_artist_id();
  cout << "artist_id: " << sval << endl;
  dval = getters.get_artist_latitude();
  cout << "artist_latitude: " << dval << endl;
  sval = getters.get_artist_location();
  cout << "artist_location: " << sval << endl;
  dval = getters.get_artist_longitude();
  cout << "artist_longitude: " << dval << endl;
  sval = getters.get_artist_mbid();
  cout << "artist_mbid: " << sval << endl;
  getters.get_artist_mbtags(svec);
  cout << "artist_mbtags: shape = (" << svec.size() << ",)" << endl;
  getters.get_artist_mbtags_count(dvec);
  cout << "artist_mbtags_count: shape = (" << dvec.size() << ",)" << endl;
  sval = getters.get_artist_name();
  cout << "artist_name: " << sval << endl;
  ival = getters.get_artist_playmeid();
  cout << "artist_playmeid: " << ival << endl;
  getters.get_artist_terms(svec);
  cout << "artist_terms: shape = (" << svec.size() << ",)" << endl;
  getters.get_artist_terms_freq(dvec);
  cout << "artist_terms_freq: shape = (" << dvec.size() << ",)" << endl;
  getters.get_artist_terms_weight(dvec);
  cout << "artist_terms_weight: shape = (" << dvec.size() << ",)" << endl;
  sval = getters.get_audio_md5();
  cout << "audio_md5: " << sval << endl;
  getters.get_bars_confidence(dvec);
  cout << "bars_confidence: shape = (" << dvec.size() << ",)" << endl;
  getters.get_bars_start(dvec);
  cout << "bars_start: shape = (" << dvec.size() << ",)" << endl;
  getters.get_beats_confidence(dvec);
  cout << "beats_confidence: shape = (" << dvec.size() << ",)" << endl;
  getters.get_beats_start(dvec);
  cout << "beats_start: shape = (" << dvec.size() << ",)" << endl;
  dval = getters.get_danceability();
  cout << "danceability: " << dval << endl;
  dval = getters.get_duration();
  cout << "duration: " << dval << endl;
  dval = getters.get_end_of_fade_in();
  cout << "end_of_fade_in: " << dval << endl;
  dval = getters.get_energy();
  cout << "energy: " << dval << endl;
  ival = getters.get_key();
  cout << "key: " << ival << endl;
  dval = getters.get_key_confidence();
  cout << "key_confidence: " << dval << endl;
  dval = getters.get_loudness();
  cout << "loudness: " << dval << endl;
  ival = getters.get_mode();
  cout << "mode: " << ival << endl;
  dval = getters.get_mode_confidence();
  cout << "mode_confidence: " << dval << endl;
  sval = getters.get_release();
  cout << "release: " << sval << endl;
  ival = getters.get_release_7digitalid();
  cout << "release_7digitalid: " << ival << endl;
  getters.get_sections_confidence(dvec);
  cout << "sections_confidence: shape = (" << dvec.size() << ",)" << endl;
  getters.get_sections_start(dvec);
  cout << "sections_start: shape = (" << dvec.size() << ",)" << endl;
  getters.get_segments_confidence(dvec);
  cout << "segments_confidence: shape = (" << dvec.size() << ",)" << endl;
  getters.get_segments_loudness_max(dvec);
  cout << "segments_loudness_max: shape = (" << dvec.size() << ",)" << endl;
  getters.get_segments_loudness_max_time(dvec);
  cout << "segments_loudness_max_time: shape = (" << dvec.size() << ",)" << endl;
  getters.get_segments_loudness_start(dvec);
  cout << "segments_loudness_start: shape = (" << dvec.size() << ",)" << endl;
  getters.get_segments_pitches(dvec);
  cout << "segments_pitches: shape = (" << dvec.size() / 12 << ", 12)" << endl;
  getters.get_segments_start(dvec);
  cout << "segments_start: shape = (" << dvec.size() << ",)" << endl;
  getters.get_segments_timbre(dvec);
  cout << "segments_timbre: shape = (" << dvec.size() / 12 << ", 12)" << endl;
  getters.get_similar_artists(svec);
  cout << "similar_artists: shape = (" << svec.size() << ",)" << endl;
  dval = getters.get_song_hotttnesss();
  cout << "song_hotttnesss: " << dval << endl;
  sval = getters.get_song_id();
  cout << "song_id: " << sval << endl;
  dval = getters.get_start_of_fade_out();
  cout << "start_of_fade_out: " << dval << endl;
  getters.get_tatums_confidence(dvec);
  cout << "tatums_confidence: shape = (" << dvec.size() << ",)" << endl;
  getters.get_tatums_start(dvec);
  cout << "tatums_start: shape = (" << dvec.size() << ",)" << endl;
  dval = getters.get_tempo();
  cout << "tempo: " << dval << endl;
  ival = getters.get_time_signature();
  cout << "time_signature: " << ival << endl;
  dval = getters.get_time_signature_confidence();
  cout << "time_signature_confidence: " << dval << endl;
  sval = getters.get_title();
  cout << "title: " << sval << endl;
  ival = getters.get_track_7digitalid();
  cout << "track_7digitalid: " << ival << endl;
  sval = getters.get_track_id();
  cout << "track_id: " << sval << endl;
  ival = getters.get_year();
  cout << "year: " << ival << endl;

  return 0; // succesfully terminated
}
