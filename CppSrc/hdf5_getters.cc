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

#ifndef __HDF5_GETTERS__
#define __HDF5_GETTERS__

#include <iostream>
#include <string>
#include <cstring>

#include "H5Cpp.h"
using namespace H5;

#include "hdf5_hl.h"
#include "hdf5_getters.h"

// max characters of a field
//#define FIELDLEN 128

HDF5Getters::HDF5Getters(const char filename[]) {

  // open the file
  const H5std_string h5filename(filename);
  h5file = new H5File(h5filename, H5F_ACC_RDONLY);

  // create the 3 groups' names
  const H5std_string NAME_GROUP_METADATA("metadata");
  const H5std_string NAME_GROUP_ANALYSIS("analysis");
  const H5std_string NAME_GROUP_MUSICBRAINZ("musicbrainz");

  // open the 3 groups
  GROUP_METADATA = h5file->openGroup( NAME_GROUP_METADATA );
  GROUP_ANALYSIS = h5file->openGroup( NAME_GROUP_ANALYSIS );
  GROUP_MUSICBRAINZ = h5file->openGroup( NAME_GROUP_MUSICBRAINZ );

}

/*
 * Destructor
 */
HDF5Getters::~HDF5Getters() {
  // Groups
  GROUP_METADATA.close();
  GROUP_ANALYSIS.close();
  GROUP_MUSICBRAINZ.close();
  // File
  h5file->close();
  delete h5file;
}

/*
 * Get Artist familiarity
 */
double HDF5Getters::get_artist_familiarity() const {
  return get_member_double( GROUP_METADATA, "artist_familiarity");
}

/*
 * Get Artist hotttnesss
 */
double HDF5Getters::get_artist_hotttnesss() const {
  return get_member_double( GROUP_METADATA, "artist_hotttnesss");
}

/*
 * Get Artist ID
 */
std::string HDF5Getters::get_artist_id() const {
  return get_member_str( GROUP_METADATA, "artist_id");
}

/*
 * Get Artist musicbrainz ID.
 */
std::string HDF5Getters::get_artist_mbid() const {
  return get_member_str( GROUP_METADATA, "artist_mbid");
}

/*
 * Get Artist musicbrainz Playme ID.
 */
int HDF5Getters::get_artist_playmeid() const {
  return get_member_int( GROUP_METADATA, "artist_playmeid");
}

/*
 * Get Artist 7digital ID.
 */
int HDF5Getters::get_artist_7digitalid() const {
  return get_member_int( GROUP_METADATA, "artist_7digitalid");
}

/*
 * Get Artist latitude
 */
double HDF5Getters::get_artist_latitude() const {
  return get_member_double( GROUP_METADATA, "artist_latitude");
}

/*
 * Get Artist longitude
 */
double HDF5Getters::get_artist_longitude() const {
  return get_member_double( GROUP_METADATA, "artist_longitude");
}

/*
 * Get Artist location
 */
std::string HDF5Getters::get_artist_location() const {
  return get_member_str( GROUP_METADATA, "artist_location");
}

/*
 * Get Artist name
 */
std::string HDF5Getters::get_artist_name() const {
  return get_member_str( GROUP_METADATA, "artist_name");
}

/*
 * Get Release
 */
std::string HDF5Getters::get_release() const {
  return get_member_str( GROUP_METADATA, "release");
}

/*
 * Get Release 7digital ID.
 */
int HDF5Getters::get_release_7digitalid() const {
  return get_member_int( GROUP_METADATA, "release_7digitalid");
}

/*
 * Get Song ID
 */
std::string HDF5Getters::get_song_id() const {
  return get_member_str( GROUP_METADATA, "song_id");
}

/*
 * Get Song hotttnesss
 */
double HDF5Getters::get_song_hotttnesss() const {
  return get_member_double( GROUP_METADATA, "song_hotttnesss");
}

/*
 * Get Song ID
 */
std::string HDF5Getters::get_title() const {
  return get_member_str( GROUP_METADATA, "title");
}

/*
 * Get Track 7digital ID.
 */
int HDF5Getters::get_track_7digitalid() const {
  return get_member_int( GROUP_METADATA, "track_7digitalid");
}

/*
 * Get analysis sample rate
 */
double HDF5Getters::get_analysis_sample_rate() const {
  return get_member_double( GROUP_ANALYSIS, "analysis_sample_rate");
}

/*
 * Get Audio MD5
 */
std::string HDF5Getters::get_audio_md5() const {
  return get_member_str( GROUP_ANALYSIS, "audio_md5", 32);
}

/*
 * Get danceability
 */
double HDF5Getters::get_danceability() const {
  return get_member_double( GROUP_ANALYSIS, "danceability");
}

/*
 * Get duration
 */
double HDF5Getters::get_duration() const {
  return get_member_double( GROUP_ANALYSIS, "duration");
}

/*
 * Get end of fade in
 */
double HDF5Getters::get_end_of_fade_in() const {
  return get_member_double( GROUP_ANALYSIS, "end_of_fade_in");
}

/*
 * Get energy
 */
double HDF5Getters::get_energy() const {
  return get_member_double( GROUP_ANALYSIS, "energy");
}

/*
 * Get Key
 */
int HDF5Getters::get_key() const {
  return get_member_int( GROUP_ANALYSIS, "key");
}

/*
 * Get key confidence
 */
double HDF5Getters::get_key_confidence() const {
  return get_member_double( GROUP_ANALYSIS, "key_confidence");
}

/*
 * Get loudness
 */
double HDF5Getters::get_loudness() const {
  return get_member_double( GROUP_ANALYSIS, "loudness");
}

/*
 * Get mode
 */
int HDF5Getters::get_mode() const {
  return get_member_int( GROUP_ANALYSIS, "mode");
}

/*
 * Get mode confidence
 */
double HDF5Getters::get_mode_confidence() const {
  return get_member_double( GROUP_ANALYSIS, "mode_confidence");
}

/*
 * Get tempo
 */
double HDF5Getters::get_tempo() const {
  return get_member_double( GROUP_ANALYSIS, "tempo");
}

/*
 * Get start of fade out
 */
double HDF5Getters::get_start_of_fade_out() const {
  return get_member_double( GROUP_ANALYSIS, "start_of_fade_out");
}

/*
 * Get time signature
 */
int HDF5Getters::get_time_signature() const {
  return get_member_int( GROUP_ANALYSIS, "time_signature");
}

/*
 * Get time signature confidence
 */
double HDF5Getters::get_time_signature_confidence() const {
  return get_member_double( GROUP_ANALYSIS, "time_signature_confidence");
}

/*
 * Get Track ID
 */
std::string HDF5Getters::get_track_id() const {
  return get_member_str( GROUP_ANALYSIS, "track_id");
}

/*
 * Get year
 */
int HDF5Getters::get_year() const {
  return get_member_int( GROUP_MUSICBRAINZ, "year");
}

/*
 * Get artist terms freq.
 */
void HDF5Getters::get_artist_terms_freq(std::vector<double>& result) const {
  get_member_double_array( GROUP_METADATA,
			   "artist_terms_freq",
			   result);
}

/*
 * Get artist terms weight.
 */
void HDF5Getters::get_artist_terms_weight(std::vector<double>& result) const {
  get_member_double_array( GROUP_METADATA,
			   "artist_terms_weight",
			   result);
}

/*
 * Get segments start.
 */
void HDF5Getters::get_segments_start(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "segments_start",
			   result);
}

/*
 * Get segments confidence.
 */
void HDF5Getters::get_segments_confidence(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "segments_confidence",
			   result);
}

/*
 * Get segments loudness max.
 */
void HDF5Getters::get_segments_loudness_max(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "segments_loudness_max",
			   result);
}

/*
 * Get segments loudness max time.
 */
void HDF5Getters::get_segments_loudness_max_time(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "segments_loudness_max_time",
			   result);
}

/*
 * Get segments loudness max time.
 */
void HDF5Getters::get_segments_loudness_start(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "segments_loudness_start",
			   result);
}

/*
 * Get sections start.
 */
void HDF5Getters::get_sections_start(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "sections_start",
			   result);
}

/*
 * Get sections confidence.
 */
void HDF5Getters::get_sections_confidence(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "sections_confidence",
			   result);
}

/*
 * Get beats start.
 */
void HDF5Getters::get_beats_start(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "beats_start",
			   result);
}

/*
 * Get beats confidence.
 */
void HDF5Getters::get_beats_confidence(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "beats_confidence",
			   result);
}

/*
 * Get bars start.
 */
void HDF5Getters::get_bars_start(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "bars_start",
			   result);
}

/*
 * Get bars confidence.
 */
void HDF5Getters::get_bars_confidence(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "bars_confidence",
			   result);
}

/*
 * Get tatums start.
 */
void HDF5Getters::get_tatums_start(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "tatums_start",
			   result);
}

/*
 * Get tatums confidence.
 */
void HDF5Getters::get_tatums_confidence(std::vector<double>& result) const {
  get_member_double_array( GROUP_ANALYSIS,
			   "tatums_confidence",
			   result);
}

/**
 * Get artist musicbrainz tags count.
 */
void HDF5Getters::get_artist_mbtags_count(std::vector<double>& result) const
{
  get_member_double_array( GROUP_MUSICBRAINZ,
			   "artist_mbtags_count",
			   result);
}

/*
 * Get segments timbre.
 */
void HDF5Getters::get_segments_timbre(std::vector<double>& result) const {
  get_member_double_12_array( GROUP_ANALYSIS,
			      "segments_timbre",
			      result);
}

/*
 * Get segments pitches.
 */
void HDF5Getters::get_segments_pitches(std::vector<double>& result) const {
  get_member_double_12_array( GROUP_ANALYSIS,
			      "segments_pitches",
			      result);
}

/*
 * Get artist terms.
 */
void HDF5Getters::get_artist_terms(std::vector<std::string>& result) const {
  get_member_str_array( GROUP_METADATA,
			"artist_terms",
			result);
}

/*
 * Get artist mbtags.
 */
void HDF5Getters::get_artist_mbtags(std::vector<std::string>& result) const {
  get_member_str_array( GROUP_MUSICBRAINZ,
			"artist_mbtags",
			result);
}

/*
 * Get similar artists.
 */
void HDF5Getters::get_similar_artists(std::vector<std::string>& result) const {
  get_member_str_array( GROUP_METADATA,
			"similar_artists",
			result,
			20);
}


/***************** UTITITY FUNCTIONS *******************/

/*
 * To get a double member from a given group;
 * dataset name is always 'songs'
 */
double HDF5Getters::get_member_double(const Group& group, const std::string name_member) {
  const H5std_string MEMBER( name_member );
  const CompType mtype( sizeof(double) );
  mtype.insertMember( MEMBER, 0, PredType::NATIVE_DOUBLE);
  DataSet dataset( group.openDataSet( "songs" ));
  double data_out = -1.;
  dataset.read( &data_out, mtype );
  dataset.close();
  return data_out;
}

/*
 * To get a int member from a given group;
 * dataset name is always 'songs'
 */
int HDF5Getters::get_member_int(const Group& group, const std::string name_member) {
  const H5std_string MEMBER( name_member );
  const CompType mtype( sizeof(int) );
  mtype.insertMember( MEMBER, 0, PredType::NATIVE_INT);
  DataSet dataset( group.openDataSet( "songs" ));
  int data_out = -1;
  dataset.read( &data_out, mtype );
  dataset.close();
  return data_out;
}

/*
 * To get a string member from a given group;
 * dataset name is always 'songs'
 */
std::string HDF5Getters::get_member_str(const Group& group,
					const std::string name_member,
					uint buffer_length) {
  const H5std_string MEMBER( name_member );
  DataSet dataset( group.openDataSet( "songs" ));

  // Figuring out the proper string type is a mess.
  CompType datasetcomptype(dataset);
  int memberidx = datasetcomptype.getMemberIndex( MEMBER );
  DataType dtype = datasetcomptype.getMemberDataType( memberidx );
  const CompType mtype( (size_t) 1024 );
  mtype.insertMember( MEMBER, 0, dtype);

  // Ideally we'd figure out the proper size!
  // Otherwise, let's have a buffer that is always big enough...
  char buf[buffer_length + 1];
  dataset.read( (void*) buf, mtype );
  dataset.close();
  buf[buffer_length] = '\0'; // HACK, some strings are not null-terminated.
  return std::string(buf);  
}

/*
 * To get a member which is an array of double;
 * result put in 'result';
 * dataset name is always 'songs'. 
 */
void  HDF5Getters::get_member_double_array(const Group& group,
					   const std::string name_member,
					   std::vector<double>& result)
{
  const H5std_string MEMBER( name_member );
  DataSet dataset( group.openDataSet( MEMBER ));

  hsize_t data_mem_size = dataset.getInMemDataSize();
  if (data_mem_size == 0) {
    dataset.close();
    return;
  }
  DataSpace filespace = dataset.getSpace();
  hsize_t dims[2]; 	// dataset dimensions
  filespace.getSimpleExtentDims( dims );

  int n_entries = dims[0];
  double values[n_entries];
  FloatType floattype(dataset);
  dataset.read((void*) values, floattype);
  dataset.close();

  result.clear();
  for (int k = 0; k < n_entries; ++k)
    {
      result.push_back(values[k]);
    }
}

/*
 * To get a member which is an array of array of size 12
 * (used for pitch and timbre features);
 * data is flatten segments first (i.e. first 12 values are from the
 * fist segments, etc).
 * result put in 'result';
 */
void  HDF5Getters::get_member_double_12_array(const Group& group,
					      const std::string name_member,
					      std::vector<double>& result)
{
  const H5std_string MEMBER( name_member );
  DataSet dataset( group.openDataSet( MEMBER ));

  hsize_t data_mem_size = dataset.getInMemDataSize();
  if (data_mem_size == 0) {
    dataset.close();
    return;
  }
  FloatType floattype(dataset);

  DataSpace filespace = dataset.getSpace();
  hsize_t dims[2]; 	// dataset dimensions
  int rank = filespace.getSimpleExtentDims( dims );
  DataSpace mspace1(rank, dims);

  int n_values = dims[0];
  double values[n_values][12]; // buffer for dataset to be read
  dataset.read(values, floattype, mspace1, filespace);
  dataset.close();

  result.clear();
  for (int row = 0; row < n_values; ++row)
    for (int col = 0; col < 12; ++col)
      result.push_back(values[row][col]);
}

/*
 * To get a member which is an array of strings.
 * (used for tags for instance);
 * result put in 'result';
 */
void  HDF5Getters::get_member_str_array(const Group& group,
					const std::string name_member,
					std::vector<std::string>& result,
					uint word_length)
{
  const H5std_string MEMBER( name_member );
  DataSet dataset( group.openDataSet( MEMBER ));

  hsize_t data_mem_size = dataset.getInMemDataSize();
  if (data_mem_size == 0) {
    dataset.close();
    return;
  }
  DataSpace filespace = dataset.getSpace();
  hsize_t dims[2]; 	// dataset dimensions
  int rank = filespace.getSimpleExtentDims( dims );
  DataSpace mspace1(rank, dims);

  uint n_values = dims[0];
  char values[n_values * word_length];
  StrType stringtype(dataset);
  dataset.read(values, stringtype, mspace1, filespace);

  // We split the values
  char * pch;
  char * in_values = values;
  const char* delims = "\0";
  pch = strtok (in_values, delims);
  uint counter = 0;
  result.clear();
  while (counter < n_values)
  {
    result.push_back(std::string(pch));
    counter += 1;
    if (counter == n_values)
      break;

    // hack to remove the padding introduced by HDF5
    in_values += strlen(pch);
    while(*in_values == '\0')
      ++in_values;

    pch = strtok (in_values, delims);
    }

  dataset.close();
}

#endif // __HDF5_GETTERS__
