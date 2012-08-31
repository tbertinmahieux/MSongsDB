/** 
 Thierry Bertin-Mahieux (2010) Columbia University
 tb2332@columbia.edu

 Code to access fields of a MSD HDF5 song file.

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

#include <vector>
#include <string>

#include "H5Cpp.h"
using namespace H5;

// max characters of a field
#define FIELDLEN 128

class HDF5Getters {

 private:
  
  // file
  H5File* h5file;

  // the 3 groups
  Group GROUP_METADATA;
  Group GROUP_ANALYSIS;
  Group GROUP_MUSICBRAINZ;

  // utility functions
  static double get_member_double(const Group& group,
				  const std::string name_member);
  static int get_member_int(const Group& group,
			    const std::string name_member);
  static std::string get_member_str(const Group& group,
				    const std::string name_member,
				    uint buffer_length=1024);

 public:

  // constructor
  HDF5Getters(const char filename[]);

  // destructor
  ~HDF5Getters();

  // get the number of songs
  int get_num_songs() const;

  // members
  double get_artist_familiarity() const;
  double get_artist_hotttnesss() const;
  std::string get_artist_id() const;
  std::string get_artist_mbid() const;
  int get_artist_playmeid() const;
  int get_artist_7digitalid() const;
  double get_artist_latitude() const;
  double get_artist_longitude() const;
  std::string get_artist_location() const;
  std::string get_artist_name() const;
  std::string get_release() const;
  int get_release_7digitalid() const;
  std::string get_song_id() const;
  double get_song_hotttnesss() const;
  std::string get_title() const;
  double get_analysis_sample_rate() const;
  std::string get_audio_md5() const;
  double get_danceability() const;
  double get_duration() const;




  int get_key() const;
};
